# HealthQualify Local Edition v0.8 — Setup and Guided Qualification

**Status:** Developer alpha; synthetic data only. No PHI, clinical care, regulated approvals, validated QMS or regulated electronic signatures. The default local edition needs **no cloud account, purchased API key, LLM subscription, or installed model**.

## Start locally

From a cloned checkout, on **Windows**, double-click `launch-healthqualify.bat`. On **macOS**, run `sh launch-healthqualify.command`; on **Linux**, run `sh launch-healthqualify.sh`. Python 3.10+ must already be installed for these source launchers.

Alternately run:

```bash
python -m healthqualify.local_edition_v08
```

The app opens at `http://127.0.0.1:8899` and saves its local SQLite data under `~/.healthqualify/local-edition.db`. Create an administrator name and password on first launch; after that, the browser uses HttpOnly session cookies and CSRF-protected requests. **No manually generated dashboard token** is required. Back up the database securely before upgrading.

The **[Local Edition standalone build](https://github.com/Tec-Wel/HealthQualify/actions/runs/43690197548)** has succeeded on Windows 2025, macOS 15 and Ubuntu 24.04. Each job created a platform-specific PyInstaller executable, ran its `--help` startup smoke test, and published a downloadable artifact for 30 days. Use the workflow page's **Artifacts** section to download the appropriate OS bundle. GitHub may require signing in to download Actions artifacts; cloning the source does not require a cloud account.

These are **unsigned development binaries**, not certified, notarized or independently security-assessed installers. Actual first-run desktop UI behavior still needs manual verification on each target OS; a successful `--help` test is not equivalent to a validated installer. For users who need a completely account-free binary download, a public GitHub Release asset or equivalent open download is still a distribution task.

## Guided synthetic workflow

1. Sign in. The overview starts empty on a new installation.
2. Click **Start guided qualification**, then **Run synthetic example**.
3. The system creates a fictional LIS with seven documented requirements and a versioned **DRAFT** protocol, then performs an explicitly identified **draft technical execution**. The expected outcome is **2 PASS / 5 FAIL**; these failures are intentionally seeded. No QA baseline is asserted or silently signed.
4. Open **Qualification & evidence** to view requirement-to-test-to-run evidence references and unresolved deviations.
5. Open **Five AI agents**, choose the new system and run an investigation. The deterministic agents work with no LLM and create a source-linked **DRAFT** in the local review queue.
6. To exercise reviewer separation, sign in as an admin and open **QA review queue**. Create a separate QA account and grant it access to the synthetic system. Sign out, then sign in as that QA reviewer. Review a draft written by another account. `ACKNOWLEDGED`, `NEEDS_INVESTIGATION`, and `DISMISSED` **do not qualify software**.
7. See **Local Qwen** for the optional, model-disabled-by-default check and explanations.

## Optional Qwen — no paid inference tokens

Install Ollama separately, then download a reviewed Qwen model once:

```bash
ollama pull qwen3:8b
python -m healthqualify.local_edition_v08 --allow-local-qwen
```

The application checks only `http://127.0.0.1:11434/api/tags` when the user clicks **Check locally installed Qwen**. If the model is present, users may click **Explain with local Qwen** after generating an agent investigation. Only bounded summaries and deterministic source-linked findings are passed to local Ollama. The resulting explanation is **DRAFT_UNVERIFIED** and never changes existing findings, PASS/FAIL, deviations or release approval.

The availability check is not a real inference acceptance test. For model evaluation, use `python -m healthqualify.agent_model_probe_v07 --enable-local-ollama --model qwen3:8b --max-cases 30 --out local-model-review.json` and independently review the results. The CI tests mock Ollama, so they do not establish model groundedness.

## Security boundaries and limits

- Browser and backend bind only to loopback. Host and Origin checks, HttpOnly SameSite cookies and an explicit CSRF header protect local requests.
- First-run admin bootstrap is only available before any account exists. It must not be exposed to a shared network.
- Local roles are `admin`, `qa`, `validator`, `viewer`. QA reviews cannot be performed by the author of the same agent observation.
- Filesystem/SQLite storage is not protected WORM, full audit independence or enterprise tenant isolation.
- Do not expose the HTTP server through a reverse proxy or port forward, process PHI, or use these results as regulated release authorization.
- Standalone binary distribution requires signing/notarization and OS testing before general release.
- No internet or LLM is required for the basic synthetic workflow.

Run `python -m unittest tests.test_local_edition_v08 -v` for the HTTP acceptance suite, and `python -m unittest discover -s tests -v` for the entire project.
