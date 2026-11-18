"""Check technical public-launch documentation, not copyright or regulatory status."""
from __future__ import annotations
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REQUIRED = {
    "LICENSE": ("Apache License", "Version 2.0"),
    "PRIVACY.md": ("Local Edition", "PHI", "127.0.0.1"),
    "DISCLAIMER.md": ("FDA", "synthetic", "Apache"),
    "NOTICE": ("HealthQualify", "copyright"),
    "THIRD_PARTY_NOTICES.md": ("Qwen", "Ollama", "license"),
    "TRADEMARK_POLICY.md": ("Apache", "owner", "brand"),
    "docs/OWNER_IP_RELEASE_DECISION.md": ("NOT APPROVED", "patent", "PENDING"),
    "CODE_OF_CONDUCT.md": ("Reporting", "harassment"),
    "GOVERNANCE.md": ("public", "maintainers"),
    "SECURITY.md": ("Report vulnerabilities",),
    "CONTRIBUTING.md": ("Apache-2.0", "Signed-off-by"),
    "SUPPORT.md": ("best-effort",),
    "CHANGELOG.md": ("v0.8", "v0.7"),
    "docs/PUBLIC_LAUNCH_READINESS.md": ("HOLD", "human", "secrets"),
}

def main() -> None:
    for filename, words in REQUIRED.items():
        path = BASE / filename
        if not path.is_file():
            raise SystemExit(f"Missing launch file: {filename}")
        content = path.read_text(encoding="utf-8")
        missing = [word for word in words if word.casefold() not in content.casefold()]
        if missing:
            raise SystemExit(f"Launch file {filename} missing required terms: {missing}")
    print("Launch documents: present; legal/IP/security reviews still PENDING.")
    print("No readiness status or public repository visibility has been changed.")

if __name__ == "__main__":
    main()
