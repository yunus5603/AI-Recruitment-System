"""The sandbox must contain hostile snippets, not just run friendly ones."""

import os

import pytest

from services.code_executor import Limits, execute_python_code

FAST = Limits(timeout_s=2, cpu_s=2, memory_mb=128)


def test_prints_output():
    result = execute_python_code("for i in range(3): print(i)")
    assert result.success
    assert result.output == "0\n1\n2\n"


def test_reports_exceptions_with_traceback():
    result = execute_python_code("1 / 0")
    assert not result.success
    assert "ZeroDivisionError" in result.error


def test_infinite_loop_times_out():
    result = execute_python_code("while True: pass", FAST)
    assert not result.success
    assert "timed out" in result.error or "killed" in result.error


def test_sleep_is_bounded_by_wall_clock_timeout():
    result = execute_python_code("import time; time.sleep(30)", FAST)
    assert not result.success
    assert "timed out" in result.error


@pytest.mark.skipif(os.name != "posix", reason="rlimits are POSIX-only")
def test_memory_bomb_is_stopped():
    result = execute_python_code("x = bytearray(1024 * 1024 * 1024)", FAST)
    assert not result.success
    assert "MemoryError" in result.error or "killed" in result.error


def test_cannot_see_server_environment(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "super-secret")
    result = execute_python_code("import os; print(os.environ.get('GROQ_API_KEY'))")
    assert result.output.strip() == "None"


def test_runs_in_empty_scratch_directory():
    result = execute_python_code("import os; print(os.listdir('.'))")
    assert result.output.strip() == "['main.py']"


def test_cannot_crash_the_api_process():
    result = execute_python_code("import sys; sys.exit(3)")
    assert not result.success
    assert "Exit code 3" in result.error


def test_output_is_truncated():
    result = execute_python_code("print('a' * 200_000)")
    assert result.output.endswith("[output truncated]")
    assert len(result.output) < 70_000


def test_rejects_huge_code():
    result = execute_python_code("#" * 50_000)
    assert not result.success
    assert "larger than" in result.error
