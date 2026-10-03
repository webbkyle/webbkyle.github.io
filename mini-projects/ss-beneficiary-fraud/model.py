#!/usr/bin/env python3
"""
Prototype Bayesian model: fraudulent Social Security (OASDI) beneficiaries.

v1 — conjugate Beta-Binomial only, no MCMC. Fully reproducible.

Quantities
  R            reported OASDI beneficiaries in current-payment status (Dec 2024, SSA MBR 100% data)
  theta        P(a reported beneficiary's payments are fraudulent/improper)
  N_fraud      = R * theta   (fraudulent beneficiaries among reported)
  N_actual     = R - N_fraud (legitimate beneficiaries)
  pi           P(a DOGE-flagged "stale" record was actually receiving payments)
               informed by SSA OIG: 44,000 paid out of 18.9M flagged-type records
  N_ghost(F)   = F * pi      (DOGE-implied improper payments for a flagged universe F)

Prior stances on theta (documented in notes.md):
  skeptical  mean 0.02%  - true fraud well below measured improper rates (mostly errors)
  neutral    mean 0.28%  - blended OASDI stewardship overpayment rate (dollar basis), FY2024
  alarmist   mean 1.00%  - order of magnitude above measured; "hidden fraud" thesis
Prior strength: 20,000 pseudo-observations for all three.

Outputs: data/posteriors.json with posterior summaries + 200-pt density grids.
"""
import json
import numpy as np
from scipy import stats

OUT = "/home/hatch/workspace/mini-project-drafts/ss-beneficiary-fraud/data/posteriors.json"

# ---- inputs (all sourced; see data/sources.json) ----
R = 68_455_973            # OASDI beneficiaries, current-payment status, Dec 2024 (SSA Stat. Supplement 2025, T5.A1)
AVG_BEN = 1834.43         # avg monthly OASDI benefit, Dec 2024 (same table)
ANNUAL_PER_BEN = AVG_BEN * 12

N0 = 20_000               # prior pseudo-observations (strength)
STANCES = {
    "skeptical": {"mean": 0.0002, "rationale": "true fraud well below measured improper-payment rates (mostly errors)"},
    "neutral":   {"mean": 0.0028, "rationale": "blended OASDI stewardship overpayment rate, FY2024 (0.28% dollar basis)"},
    "alarmist":  {"mean": 0.01,   "rationale": "order of magnitude above measured; hidden-fraud thesis"},
}

# pi: OIG-measured conversion, flagged stale records -> actually paid
# y = 44,000 paid of n = 18,900,000 flagged-type records (2023 OIG report, via secondary summary)
PI_A, PI_B = 44_000, 18_900_000 - 44_000

# DOGE flagged universes
FLAGGED = {
    "cleanup_3_26M":   {"F": 3_261_057,  "label": "DOGE-announced reclassification of numberholders age 120+ (Mar 2025)"},
    "oig_universe_18_9M": {"F": 18_900_000, "label": "OIG 2023 stale-records universe (born <=1920, no death info)"},
    "musk_claim_20M":  {"F": 20_000_000, "label": "Musk claim: '20M dead marked as alive' (hypothetical flagged universe)"},
}

GRID = 200


def scaled_beta_density(a, b, scale, q_lo=0.0001, q_hi=0.9999, n=GRID):
    """Density of X = scale * Beta(a, b) on a quantile-spanned grid."""
    lo, hi = stats.beta.ppf([q_lo, q_hi], a, b) * scale
    x = np.linspace(lo, hi, n)
    y = stats.beta.pdf(x / scale, a, b) / scale
    return x, y


def summarize_scaled_beta(a, b, scale):
    d = stats.beta(a, b)
    qs = d.ppf([0.025, 0.5, 0.975]) * scale
    mean = d.mean() * scale
    var = d.var() * scale**2
    return {
        "mean": float(mean),
        "median": float(qs[1]),
        "sd": float(np.sqrt(var)),
        "ci95": [float(qs[0]), float(qs[2])],
        "p_gt_100k": float(d.sf(100_000 / scale)),
        "p_gt_1M": float(d.sf(1_000_000 / scale)),
        "annual_dollars_mean": float(mean * ANNUAL_PER_BEN),
    }


result = {
    "meta": {
        "R_reported_beneficiaries": R,
        "R_source": "SSA Annual Statistical Supplement 2025, Table 5.A1 (Dec 2024, MBR 100% data)",
        "avg_monthly_benefit": AVG_BEN,
        "prior_strength_pseudo_n": N0,
        "note": "Conjugate Beta model; no MCMC. See notes.md for assumptions and limitations.",
    },
    "stances": {},
    "doge_implied": {},
}

for name, s in STANCES.items():
    m = s["mean"]
    a = m * N0
    b = (1 - m) * N0
    entry = {
        "theta_prior": {"a": a, "b": b, "mean": m, "rationale": s["rationale"]},
    }
    # fraudulent: X = R * Beta(a, b)
    fx, fy = scaled_beta_density(a, b, R)
    entry["fraudulent"] = summarize_scaled_beta(a, b, R)
    entry["fraudulent"]["density"] = {"x": fx.tolist(), "y": fy.tolist()}
    # actual: R - X  -> density mirrored; summaries derived from fraudulent
    fr = entry["fraudulent"]
    ax = (R - fx[::-1])  # ascending grid
    ay = fy[::-1]
    entry["actual"] = {
        "mean": float(R - fr["mean"]),
        "median": float(R - fr["median"]),
        "sd": fr["sd"],
        "ci95": [float(R - fr["ci95"][1]), float(R - fr["ci95"][0])],
        "density": {"x": ax.tolist(), "y": ay.tolist()},
    }
    result["stances"][name] = entry

# reported: admin count treated as known; narrow Normal for display only
rep_sd = 0.0005 * R
rx = np.linspace(R - 4 * rep_sd, R + 4 * rep_sd, GRID)
ry = stats.norm.pdf(rx, R, rep_sd)
result["reported"] = {
    "value": R,
    "note": "Administrative count treated as known; narrow Normal(R, (0.05% R)^2) for display only.",
    "density": {"x": rx.tolist(), "y": ry.tolist()},
}

# DOGE-implied ghost payments: N_ghost(F) = F * pi, pi ~ Beta(PI_A, PI_B)
pi_mean = PI_A / (PI_A + PI_B)
doge = {"pi_posterior": {"a": PI_A, "b": PI_B, "mean": pi_mean,
        "rationale": "OIG-measured: 44,000 paid of 18.9M flagged-type records (2023 OIG report)"},
        "scenarios": {}}
for key, f in FLAGGED.items():
    F = f["F"]
    gx, gy = scaled_beta_density(PI_A, PI_B, F)
    summ = summarize_scaled_beta(PI_A, PI_B, F)
    summ["density"] = {"x": gx.tolist(), "y": gy.tolist()}
    summ["F"] = F
    summ["label"] = f["label"]
    doge["scenarios"][key] = summ
result["doge_implied"] = doge

with open(OUT, "w") as fh:
    json.dump(result, fh)

# ---- console headline numbers ----
print(f"R = {R:,}")
for name, s in result["stances"].items():
    fr = s["fraudulent"]
    print(f"\n[{name}] theta prior mean={s['theta_prior']['mean']:.4f}")
    print(f"  N_fraud: mean={fr['mean']:,.0f}  median={fr['median']:,.0f}  "
          f"95% CrI=[{fr['ci95'][0]:,.0f}, {fr['ci95'][1]:,.0f}]")
    print(f"  P(N_fraud > 100k)={fr['p_gt_100k']:.3f}  P(N_fraud > 1M)={fr['p_gt_1M']:.4f}")
    print(f"  implied annual $ (mean) = ${fr['annual_dollars_mean']:,.0f}")
    ac = s["actual"]
    print(f"  N_actual: mean={ac['mean']:,.0f}  95% CrI=[{ac['ci95'][0]:,.0f}, {ac['ci95'][1]:,.0f}]")
print(f"\npi (flag->paid) posterior mean = {pi_mean:.6f}")
for key, sc in doge["scenarios"].items():
    print(f"  ghost({key}, F={sc['F']:,}): mean={sc['mean']:,.0f}  "
          f"95% CrI=[{sc['ci95'][0]:,.0f}, {sc['ci95'][1]:,.0f}]  P(>1M)={sc['p_gt_1M']:.4f}")
print(f"\nwrote {OUT}")
