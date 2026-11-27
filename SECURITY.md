# Security

## Reporting a vulnerability

Please don't open a public issue for security problems. Use GitHub's
[private vulnerability reporting](../../security/advisories/new) instead, and
expect a reply within a week.

## Threat model: the interview code runner

The AI interview lets a candidate run Python from the browser
(`POST /interview/execute-code`). That is remote code execution by design, so
the snippet has to be treated as hostile.

### What we protect

| Asset | Example threat |
|---|---|
| Secrets in the API process | `print(os.environ["GROQ_API_KEY"])` |
| The API process itself | `sys.exit()`, monkey-patching modules, `while True: pass` |
| The host | fork bombs, filling the disk, allocating all memory |
| Other users' data | reading `recruitment.db` or other candidates' files |
| The network | using the server to scan internal services or send spam |

### History

The first version ran snippets with `exec()` **inside the API process**. Every
row in the table above was reachable: a snippet could read the API key, wipe
the database or hang the server for everyone.

### Controls now in place (`backend/services/code_executor.py`)

| Control | Stops |
|---|---|
| Separate interpreter process (`python -I -B`) | crashing or patching the API; `sys.exit()` only ends the child |
| Scrubbed environment (only `PATH`) | reading API keys and other env secrets |
| Fresh empty temp directory as `cwd`, deleted afterwards | stumbling onto app files with relative paths, leftovers between runs |
| Wall-clock timeout (5 s) | infinite loops, `sleep()`, blocking reads (stdin is `/dev/null`) |
| `RLIMIT_CPU` | CPU-bound loops even if the timeout misfires |
| `RLIMIT_AS` (256 MB) | memory bombs |
| `RLIMIT_FSIZE` (1 MB), `RLIMIT_NOFILE` | filling the disk, exhausting descriptors |
| `RLIMIT_NPROC` (in the Docker image, where the API has its own user) | fork bombs |
| Non-root user in the Docker image | writing to the application code |
| Output capped at 64 KB, code capped at 20 KB | memory pressure on the API and the browser |
| Runs off the event loop (`run_in_threadpool`) | one slow snippet blocking other requests |

Each control has a test in `backend/tests/test_code_executor.py` that runs the
hostile snippet and checks it is contained.

### Known gaps and the stronger option

The default `subprocess` backend is **not** a full sandbox. The child runs as
the same OS user as the API, so it can still read files that user can read
(by absolute path) and it has network access.

For anything public, set `CODE_EXECUTOR=docker`. Each snippet then runs in a
throwaway container with:

- `--network none` (no network at all)
- `--read-only` root filesystem, with only a small `tmpfs` at `/tmp`
- the code mounted read-only, no access to the app or database
- `--cap-drop ALL`, `no-new-privileges`, and running as `nobody`
- `--memory`, `--cpus` and `--pids-limit`

The API host needs access to a Docker daemon for this. Next steps beyond that
would be gVisor (`--runtime=runsc`) or a microVM such as Firecracker, and a
per-user rate limit on the endpoint.

## Other notes

- Uploads must be PDFs (checked by extension and the `%PDF` magic bytes) and
  are capped at 5 MB.
- The chat endpoint only accepts `user` messages, so a client can't inject
  `system` or `assistant` turns into the prompt.
- There is no authentication yet. Don't expose a deployment with real
  candidate data until it has one (see the roadmap in the README).
