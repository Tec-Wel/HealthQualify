# Release presentation template

Use this template for **future** tagged GitHub releases. It does not represent a published or qualified HealthQualify release.

## HealthQualify vX.Y — [Human-readable title]

**Developer-alpha / preview / stable status:** [choose accurate status]

### At a glance

One short sentence describing the actual shipped changes.

| New | Improved | Important limitations |
| :--- | :--- | :--- |
| [Verified capability] | [Measurable UX update] | [Known unsupported area] |

### See it in action

Add a **real, reviewed, synthetic-data product screenshot** here. Include the commit SHA and view being shown. Do not use a concept graphic as evidence of product behavior.

### Start using it

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python -m unittest discover -s tests -v
```

Link to the correct versioned setup instructions and operating-system differences.

### What changed

- [User-facing changes with exact links to source/docs]
- [Accessibility or documentation improvements]
- [Verification evidence and reproducible commands]

### Compatibility & security

Explain migrations, API/CLI changes, supported environments, and limits of regulated use. A successful software test does not imply FDA certification or qualified GxP validation.

### Checks

- [ ] GitHub Actions passed on exact release commit
- [ ] README and docs source links verified
- [ ] Changes manually inspected for personal information
- [ ] Real screenshots labeled accurately
- [ ] Release notes reviewed and approved for publication
