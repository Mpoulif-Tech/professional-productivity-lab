# Professional Productivity Lab

Three tested Python tools that connect privacy, performance reporting and bilingual communication across technical, administrative and care-related environments.

## Projects

| # | Project | Practical outcome |
|---|---|---|
| 18 | **Confidentiality Redactor** | Redacts common sensitive tokens and organization-specific terms. |
| 19 | **KPI Report Generator** | Summarizes a numeric indicator and compares it with an explicit target. |
| 20 | **Bilingual Template Manager** | Keeps French and English templates aligned and safely renders required fields. |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m professional_productivity_lab
```

## Engineering choices

- Deterministic, testable outputs
- Strict input and template-field validation
- Privacy-safe examples with no live secrets or personal data
- Bilingual French/English workflow support
- GitHub Actions CI with read-only repository permissions

These are personal portfolio projects, not client work.

## License

MIT © Henri Mpouli
