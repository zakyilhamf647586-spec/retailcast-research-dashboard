# RETAILCAST — Research-grade Retail Forecasting & Decision Support

**Historical sales forecasting • Evaluated against baselines • Inventory-loss simulation**

RETAILCAST is a **read-only research prototype** built on [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
It evaluates **50 item codes × 104 full weeks** of historical, recorded positive sales. The dashboard **does not** operate or recommend actual purchase orders, and no production system is claimed.

## Scientific results (frozen)

- Evaluation: rolling one-week-ahead forecasting, 40-week development validation, last 12 weeks as a separate final forecasting holdout.
- Pre-selected candidate after validation: **Moving Average (4 weeks)** — validation WAPE **73.63%**.
- Final 12-week holdout WAPE: **Ridge 53.46%, MA4 54.10%, Histogram Gradient Boosting 55.87%**.
- Ridge's slight holdout advantage is **not** strong evidence of general superiority; no model was reselected using holdout.
- Exploratory post-hoc inventory penalty simulation: model/policy comparisons depend on assumed shortage:excess ratios. **Penalty values are dimensionless, not monetary savings.**

## What is in the dashboard?

1. **Forecast comparison:** validation-selected model, final holdout WAPE, sales trend.
2. **Product analysis:** per-SKU actual vs predicted units over 12 holdout weeks.
3. **Inventory scenarios:** hypothetical one-week capacity targets, with 1:1, 3:1 and 5:1 penalty assumptions.
4. **Research & limitations:** source attribution, protocol, data-quality caveats, business-model limits.

## Run locally

Use **Python 3.13** (not 3.14) to match the Cloud deployment target.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/smoke_http.py
python -m streamlit run app.py
```

The first two commands after installation exercise pure core logic and Streamlit's **official AppTest**; the smoke script starts a real local Streamlit server and checks health. None of these alone guarantees a deployed browser UI looks correct: visually check all four tabs after deployment.

## Publish on Streamlit Community Cloud

1. Create a **new GitHub repository** dedicated to RETAILCAST. Upload **the contents of this folder at the repository root**, keeping `data/`, `core.py`, `app.py`, and `requirements.txt` together.
2. Check the repository **Actions** tab; the GitHub workflow installs pinned dependencies, runs AppTest, and checks the server.
3. At [share.streamlit.io](https://share.streamlit.io/), choose the repo, branch `main`, entrypoint `app.py`, and select **Python 3.13 in Advanced settings**.
4. Verify all four tabs, change StockCode and penalty ratio, and review error logs before sharing the link.

**Do not delete your earlier house-price prediction repository.** This project is separate.

## Research integrity and limitations

- Source: Chen, D. (2012). *Online Retail II*. UCI Machine Learning Repository. DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D). Data licensed **CC BY 4.0**; cite source when using derived data.
- Source records cover 2009–2011; patterns need not reflect current retail demand.
- Target is **recorded positive sales**, not censored demand or true inventory needs. Returns, cancellations, and store outages are not recovered as customer demand.
- **Phase 2A data quality gate remains conditional:** duplicate-looking lines, bulk quantities, and special StockCodes are flagged but not authoritative reconciled against source invoices/catalogs.
- Inventory simulation was constructed after forecast holdout was inspected; treat policy comparisons as **exploratory**, not a second independent out-of-sample experiment.
- No stock on hand, real economic costs, lead times, or lost sales are available. Scenario output is **not a purchasing recommendation**.
- These limitations and selection rules are explained in `docs/PROVENANCE.md`.

## File structure

```text
RETAILCAST/
├── app.py                   # Read-only Streamlit dashboard
├── core.py                  # Pure research presentation / integrity functions
├── data/                    # Frozen, attributed derived CSV/JSON inputs (no CustomerID)
├── docs/                    # Provenance, checksums and scope
├── tests/                   # Data checks, mocked UI and real Streamlit AppTest
├── scripts/smoke_http.py    # Actual Streamlit server health test
├── .github/workflows/      # Continuous integration
├── requirements.txt        # Pinned Python dependencies
└── RETAILCAST_Research_Preview.html  # Offline static preview
```

## Verification status

Core dataset/UI tests **passed** in an offline Python 3.13 environment. Streamlit itself **could not be installed there due to unavailable package index**; true AppTest and server integration are included in CI and **must pass after publishing**. No live Streamlit deployment has been asserted. See `VERIFICATION_STATUS.md`.
