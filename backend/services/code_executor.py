"""Run untrusted interview code in an isolated child process.

The old implementation called ``exec()`` inside the API process, so any
candidate snippet could read secrets, delete files or hang the server. Code
now runs in a separate interpreter with hard limits. See ``SECURITY.md`` for
the threat model.

Two backends are available, picked with ``CODE_EXECUTOR``:

* ``subprocess`` (default): a fresh ``python -I`` process in an empty temp
  directory with a scrubbed environment, a wall-clock timeout and POSIX
  rlimits on CPU time, memory, file size, open files and process count.
* ``docker``: the same snippet in a throwaway ``python:3.12-slim`` container
  with ``--network none``, a read-only root filesystem, dropped capabilities,
  and memory/CPU/pid limits. Use this when the API host can run Docker.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from models.schemas import CodeExecutionResult


@dataclass(frozen=True)
class Limits:
    timeout_s: float = float(os.getenv("CODE_TIMEOUT_SECONDS", "5"))
    cpu_s: int = int(os.getenv("CODE_CPU_SECONDS", "5"))
    memory_mb: int = int(os.getenv("CODE_MEMORY_MB", "256"))
    max_output_bytes: int = 64 * 1024
    max_code_bytes: int = 20 * 1024
    max_file_bytes: int = 1024 * 1024
    max_open_files: int = 64
    max_processes: int = 1


DEFAULT_LIMITS = Limits()
DOCKER_IMAGE = os.getenv("CODE_EXECUTOR_IMAGE", "python:3.12-slim")


def _apply_rlimits(limits: Limits):  # pragma: no cover - runs in the child
    import resource

    mem = limits.memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_CPU, (limits.cpu_s, limits.cpu_s))
    resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits.max_file_bytes, limits.max_file_bytes))
    resource.setrlimit(resource.RLIMIT_NOFILE, (limits.max_open_files, limits.max_open_files))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        # Blocks fork bombs. RLIMIT_NPROC counts every process of the user,
        # so it is only safe when the API runs as a dedicated user (as in the
        # Docker image); otherwise skip it rather than break the server.
        if os.getenv("CODE_LIMIT_NPROC") == "1":
            resource.setrlimit(resource.RLIMIT_NPROC, (limits.max_processes, limits.max_processes))
    except (ValueError, OSError):
        pass
    os.setsid()


def _truncate(text: str, limit: int) -> str:
    data = text.encode()
    if len(data) <= limit:
        return text
    return data[:limit].decode(errors="ignore") + "\n... [output truncated]"


def _subprocess_command(script: str) -> list[str]:
    # -I: isolated mode (ignores PYTHON* env vars and user site-packages),
    # -B: don't write .pyc files.
    return [sys.executable, "-I", "-B", script]


def _docker_command(workdir: str, limits: Limits) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,size=16m",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "32",
        "--memory",
        f"{limits.memory_mb}m",
        "--cpus",
        "0.5",
        "--user",
        "65534:65534",
        "-v",
        f"{workdir}:/sandbox:ro",
        "-w",
        "/tmp",
        DOCKER_IMAGE,
        "python",
        "-I",
        "-B",
        "/sandbox/main.py",
    ]


def execute_python_code(code: str, limits: Limits = DEFAULT_LIMITS) -> CodeExecutionResult:
    """Execute a Python snippet in a sandbox and capture its output."""
    if len(code.encode()) > limits.max_code_bytes:
        return CodeExecutionResult(
            success=False, output="", error=f"Code is larger than {limits.max_code_bytes} bytes"
        )

    backend = os.getenv("CODE_EXECUTOR", "subprocess")
    with tempfile.TemporaryDirectory(prefix="sandbox-") as workdir:
        script = os.path.join(workdir, "main.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(code)

        if backend == "docker":
            cmd, kwargs = _docker_command(workdir, limits), {}
        else:
            cmd = _subprocess_command(script)
            kwargs = {
                "cwd": workdir,
                "env": {"PATH": "/usr/bin:/bin", "PYTHONIOENCODING": "utf-8"},
                "preexec_fn": (lambda: _apply_rlimits(limits)) if os.name == "posix" else None,
            }

        try:
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=limits.timeout_s + (5 if backend == "docker" else 0),
                **kwargs,
            )
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode(errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or "")
            return CodeExecutionResult(
                success=False,
                output=_truncate(out, limits.max_output_bytes),
                error=f"Execution timed out after {limits.timeout_s:g}s",
            )

    stdout = _truncate(proc.stdout, limits.max_output_bytes)
    stderr = _truncate(proc.stderr, limits.max_output_bytes)

    if proc.returncode == 0 and not stderr:
        return CodeExecutionResult(
            success=True, output=stdout or "Code executed successfully (no output)", error=None
        )

    if proc.returncode < 0:  # killed by a signal, usually an rlimit
        stderr = (stderr + f"\nProcess killed (signal {-proc.returncode}): resource limit exceeded").strip()
    elif "MemoryError" in stderr:
        stderr += f"\nMemory limit is {limits.memory_mb} MB"
    return CodeExecutionResult(success=False, output=stdout, error=stderr or f"Exit code {proc.returncode}")
