# Authentic dashboard screenshots — local capture guide

The user-facing README includes **illustrations**, not screenshots. To add screenshots of the actual local UI, capture the running implementation using synthetic fixtures.

## Install the optional, free screenshot tooling

```bash
python -m pip install "playwright>=1.49,<2"
python -m playwright install chromium
```

This is optional and not needed to run HealthQualify or build the documentation.

## Capture the real dashboard

From the repository root:

```bash
python scripts/capture_agent_dashboard.py --output-dir .healthqualify/screenshots
```

The script starts the local HealthQualify dashboard with an ephemeral token, opens it through Chromium at `127.0.0.1`, runs the five **deterministic** synthetic investigations, and captures desktop, tablet, and mobile screenshots.

The script uses fixed synthetic examples and never enables Ollama. It neither requests a cloud account nor sends material to a hosted screenshot service. It stores images locally and prints their paths. **Screenshot files are not auto-published to GitHub.**

### Review before committing screenshots

Inspect screenshots manually for accidental user information and model output; replace any sensitive content before committing. The capture token is entered into a password field and not visible in the screenshots. An actual screenshot should be described as `Synthetic local dashboard, [commit SHA]`, not as a customer deployment.

Suggested future README placement: immediately below the two-product-area diagram, with one desktop screenshot and a link to a gallery in this guide. Do not insert screenshot links before files are committed.

## Visual checks

```bash
python scripts/check_visual_assets.py
python -m mkdocs build --site-dir site
python scripts/check_docs_render.py site
```

The asset check validates SVG structure, nonempty accessible titles/descriptions, expected artwork files and aspect ratios. The MkDocs checks verify the rendered HTML. Optional desktop/mobile screenshot comparisons should be reviewed manually until stable Playwright baselines are captured for each viewport.

## No-paid-tool policy

Use Python, Playwright, and the locally running synthetic dashboard. No commercial UI testing service, paid image asset, hosting upgrade, or analytics integration is required.
