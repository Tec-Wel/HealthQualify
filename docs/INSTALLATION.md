# Installation and local setup

## Supported setup

- Python **3.10+** for the stdlib synthetic and workspace tools; **3.12 recommended**.
- Git to clone the repository.
- `requirements-security.txt` only when using cryptography, optional DICOM support, or the secure interoperability test suite.
- Docker + Docker Compose are optional for **workspace initialization**, not required for the first run.
- Internet access is needed to clone or install packages, **not** to execute the embedded synthetic v0.5 protocol.

Avoid sudo/administrator Python installations when using a virtual environment. Never store tokens, evidence encryption keys or patient records in Git.

## Windows 10/11: PowerShell

Install Git and Python from trusted distribution channels. In PowerShell:

```powershell
git clone https://github.com/Tec-Wel/HealthQualify.git
Set-Location HealthQualify
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/win-run
```

The last command exits 1 **by design** because of five seeded failures. If PowerShell refuses script activation, use `.\.venv\Scripts\python.exe` directly (without changing execution policy). Install security dependencies inside the environment if needed:

```powershell
python -m pip install -r requirements-security.txt
```

## macOS: Terminal (zsh) and Linux: shell

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/unix-run
```

For optional security/DICOM helpers:

```bash
python -m pip install -r requirements-security.txt
```

On some Linux distributions, install the matching Python venv OS package first. On macOS, use a supported Python 3.12 distribution if the system Python is too old.

## Check setup independently

```bash
python -m healthqualify.appcli --help
python -m healthqualify.v05cli --help
python -m healthqualify.cli --help
python -m unittest discover -s tests -v
```

Run all commands from the **repository root**. No `pip install -e .` packaging step is currently required or supported by the repository layout.

## SQLite workspace (a separate usage path)

```bash
python -m healthqualify.appcli --db healthqualify.db init
python -m healthqualify.appcli --db healthqualify.db system-add "Synthetic LIS" "Demonstrate lab interface qualification with fictional data" "Engineer"
python -m healthqualify.appcli --db healthqualify.db systems
```

This path records v0.2 protocols and local review events; it is **not** the same as the v0.5 standalone v0.3 JSON runner. See [End-to-end workflow](END_TO_END_WORKFLOW.md).

## Authenticated local API (opt-in)

```bash
python -m healthqualify.appcli --db healthqualify.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db healthqualify.db serve
```

The admin bootstrap prompts for a password of at least 12 characters. By default the API binds to `http://127.0.0.1:8877`; GET `/health` requires no authentication, but other read/write routes need a bearer session. The secure API is **not** a browser dashboard; do not expect a React interface. See [Integration](INTEGRATION_GUIDE.md).

## Docker Compose: initialization only

```bash
docker compose build
docker compose run --rm healthqualify
```

The Compose service runs `appcli init` against a local named volume and **does not** expose the API. Container portability does not provide production security, storage governance or regulatory validation.

## Windows, paths, secrets, and repeat runs

- Use a **fresh `--out` directory** on every standalone run. Do not delete earlier evidence before capturing its trust anchor.
- Keep project fixture data public or synthetic; make a separate copy before editing.
- Preserve original example JSON files; do not commit generated databases, tokens, evidence, or test output.
- For CLI copy/paste examples, `YOUR_SAVED_DIGEST` is a placeholder and must be replaced; do **not** type literal angle brackets.

## Common failures

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `No module named healthqualify` | Command run outside repository root / wrong Python | `cd HealthQualify`, activate correct environment |
| Python not found | Python launcher differs by OS | Use Windows `py -3` or Unix `python3` |
| `File exists` for run directory | Output already used | Choose a new directory; evidence is append-by-new-run |
| Run exits 1 but tests suite passed | Five intentionally failing assertions | Inspect `results.json`; this is expected |
| API connection refused | `serve` not running / wrong port | Start service and use `127.0.0.1:8877` |
| Import error for optional security package | Dependencies not installed | Install `requirements-security.txt` in the active environment |

More details: [Troubleshooting](TROUBLESHOOTING.md).
