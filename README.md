# Hamta (همتا)

**Peer-graph intelligence for finding payment merchants with untapped transaction growth.**

*همتا* means "peer / counterpart" in Persian — the core idea of the project: don't judge a
merchant against itself, judge it against the merchants that share its customers, its
category (صنف) and its transaction rhythm. A merchant that sits well below its true peers is a
candidate for a growth campaign.

> Persian title: طراحی سامانه هوشمند شناسایی پذیرندگان دارای ظرفیت رشد تراکنش با استفاده از تحلیل گراف و هوش مصنوعی

## The idea in one example

| Merchant      | Transactions |
|---------------|-------------:|
| Gold shop A   | 100          |
| Gold shop B   | 180          |
| Gold shop C   | 165          |

If A shares many customers with B and C and behaves like them, why does it get only 100?
That gap is a signal of growth capacity. Hamta finds these gaps across the whole network and
returns a ranked list of merchants for campaign targeting.

## Inputs

Anonymized transaction records: `card_hash, merchant_id, amount, timestamp, cast_name`.

## Output

A ranked list of merchants: current volume, expected (peer-based) volume, growth-gap score,
confidence, and a short explanation of *why* the merchant was selected.

## Status

Research / design phase. Target venue for the first paper: ICAEA 2026 (10th Iranian Conference
on Advances in Enterprise Architecture), Track 5 — Data Analytics, BI and Decision Support.

## Documents

- [docs/proposal.md](docs/proposal.md) — the original idea (Persian)
- [docs/research.md](docs/research.md) — analysis of the idea, pitfalls, related work and state-of-the-art technology
- [docs/roadmap.md](docs/roadmap.md) — phased roadmap from baseline to production
- [docs/conference/](docs/conference/README.md) — ICAEA 2026 requirements, dates, templates and forms

## Repository layout

```
docs/
  proposal.md        original idea (Persian)
  research.md        analysis, pitfalls, related work, technology landscape
  roadmap.md         phased plan and publication path
  conference/        ICAEA 2026 notes + official templates and forms
```

Code (`src/`), notebooks and the paper draft (`paper/`) will be added as the work starts.

## Data policy

No real transaction data is ever committed to this repository. See `.gitignore`.
