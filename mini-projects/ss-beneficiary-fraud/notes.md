# SS Beneficiary Fraud — Bayesian draft notes

**Status:** research + prototype. DRAFT ONLY — nothing published.

## The question

How many Social Security (OASDI) beneficiaries are fraudulent, given (a) SSA's published
beneficiary counts, (b) DOGE's flagged-record numbers, and (c) SSA/OIG's own measurement
of how often flagged records actually correspond to payments? Answered distributionally:
posteriors over reported, fraudulent, and actual beneficiaries.

## Data sources (full detail in data/sources.json)

| Figure | Value | Source | Confidence |
|---|---|---|---|
| OASDI beneficiaries, Dec 2024 (R) | 68,455,973 | SSA Stat. Supplement 2025, T5.A1 (page opened) | high |
| Avg monthly benefit, Dec 2024 | $1,834.43 | same table (page opened) | high |
| Stale records, born <=1920, no death info | 18.9M | OIG Jul 2023 report (secondary summaries) | medium |
| Flagged-type records actually paid | 44,000 | secondary summary of OIG report | **low - verify vs primary** |
| DOGE 120+ cleanup | 3,261,057 records | DOGE X post via Mitrade (secondary) | medium |
| Musk "20M dead marked alive" | 20M claimed | interview claim, SSA rebutted | claim, not fact |
| Stewardship FY2024 (OASI/DI/SSI overpayment-free) | 99.91% / 98.72% / 89.97% | SSA AFR Other Reporting Reqmts (snippet) | medium |
| OIG 2021: payments to deceased, 1998-2019 | $298M / ~24k | secondary summary | medium |
| State-level fake-SSN reports (OASDI) | — | **not found** | n/a (see below) |

## Model (model.py — conjugate Beta, no MCMC)

- `theta` = P(a reported beneficiary's payments are fraudulent/improper).
  Prior `Beta(a, b)`, mean by stance, strength 20,000 pseudo-observations:
  - **skeptical** 0.02% — true fraud well below measured improper rates (mostly errors)
  - **neutral** 0.28% — blended OASDI stewardship *dollar* improper-payment rate, FY2024
    (($1.62B + $2.34B) / ($1.29T + $143.44B) = 0.276%)
  - **alarmist** 1.00% — order of magnitude above measured; hidden-fraud thesis
- `N_fraud = R * theta` (scaled Beta; summaries + 200-pt density grids in posteriors.json)
- `N_actual = R - N_fraud`
- `R` treated as known admin count; narrow Normal for display only.
- **DOGE ghost check** (separate): `pi` = P(flagged record actually paid),
  `pi ~ Beta(44000, 18856000)` from OIG measurement; `N_ghost(F) = F * pi` for
  F in {3.26M cleanup, 18.9M OIG universe, 20M Musk claim}.

### Headline results

| Stance | N_fraud mean | 95% CrI | Implied $/yr (mean) | P(N_fraud > 1M) |
|---|---|---|---|---|
| skeptical | 13,691 | [3,731 – 30,006] | $0.30B | 0 |
| neutral | 191,677 | [144,844 – 244,949] | $4.2B | 0 |
| alarmist | 684,560 | [593,381 – 782,090] | $15.1B | 0 |

Ghost check (`pi` posterior mean 0.00233): 3.26M flagged -> **~7,592** actually paid
[7,521 – 7,663]; 18.9M -> ~44,000; even Musk's 20M -> ~46,561. P(>1M) = 0 in all cases.
This is the money chart: flagged *records* in the millions, implied *payments* in the thousands.

## Key modeling assumptions

1. **Improper != fraud, everywhere.** SSA stewardship measures improper payments
   (over + under, mostly errors). Using them to center priors makes the neutral/alarmist
   stances *upper bounds* on fraud, not estimates of fraud. Say this loudly in the write-up.
2. The 44,000/18.9M conversion is the load-bearing number and the weakest-sourced.
   If the primary OIG report gives a different figure, `pi` (and the ghost check) moves.
3. Prior strength (20k pseudo-obs) is a judgment call; the interactive widget should let
   readers weaken/strengthen it and watch posteriors widen/narrow.
4. `R` as fixed ignores admin revisions; immaterial at this scale.
5. Dollar conversion uses the *average* benefit; fraudulent cases may skew (unknown direction).
6. SSI excluded (focus is OASDI). DI's 1.28% overpayment rate vs OASI's 0.09% is worth
   a sensitivity: fraud concentrated in DI would change the blend.
7. The model does NOT use the whistleblower 2.7M death-file story as data (it cuts the
   other way: living people marked dead). Kept as context only.

## Open uncertainties / needs stronger sourcing (before any publish)

1. **Verify 44,000 vs primary OIG report.** Open oig.ssa.gov, find the July 2023 (and March 2023)
   "numberholders age 112+" reports, confirm the paid-among-flagged count.
2. **Verify stewardship PDF directly** (open the "Other Reporting Requirements" PDF, confirm
   99.91% / 98.72% / $1.62B / $2.34B).
3. **DOGE primary posts**: the X announcements (3.26M cleanup; the 150-159 table) — find
   primary or at least AP/Reuters coverage.
4. **State-level fake-SSN reports: NOT FOUND for OASDI.** The user's recollection appears to
   conflate the **USDA SNAP 29-state review** (185,986 deceased SSNs on SNAP rolls, 350k-500k
   duplicates; SNAP != Social Security). Do not present SNAP figures as OASDI fraud evidence.
   If the draft mentions states at all, it must be labeled as the SNAP program.
5. Decide the interactive widget's parameter ranges (prior mean slider, prior strength slider,
   flagged-count input, conversion-rate slider) — posteriors.json already has the density
   grids; the page math is closed-form Beta updates.
6. Consider a DI-vs-OASI split as a follow-up sensitivity (DI overpayment rate is ~14x OASI's).
