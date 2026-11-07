# RETAILCAST | Retail Forecasting & Decision-Support Research

**Research-driven forecasting • Transparent model comparison • Exploratory inventory simulation**

[**Live Streamlit dashboard**](https://retailcast-research-zaky.streamlit.app/) · [**Data source: UCI Online Retail II**](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

RETAILCAST is a **read-only applied research prototype**, not an operational inventory system. It compares simple baselines with machine-learning models for weekly **recorded positive sales units** and illustrates the consequences of hypothetical stock-capacity penalties. The code, results, assumptions, and methodological limitations are documented openly.

## Research at a glance

| Component | Study design / observed result |
|---|---|
| Raw source | UCI Online Retail II, 1,067,371 transaction line items (2009–2011) |
| Research sample | 50 frozen SKUs × 104 complete weeks |
| Forecast protocol | Rolling one-week-ahead, 40-week model-selection validation + separate 12-week holdout |
| Validation-selected approach | **4-week moving average (MA4)**, WAPE **73.6334%** |
| Final holdout | Ridge **53.4649%** · MA4 **54.0980%** · Histogram Gradient Boosting **55.8704%** WAPE |
| Interpretation | Ridge's small observed holdout advantage does **not** establish general superiority; MA4 remains the validation-selected incumbent |
| Exploratory inventory simulation (3:1 shortage:excess) | MA4 raw loss index **277,905** vs MA4 residual-quantile adjusted **256,486** (**−7.71%**) |
| Research integrity | Phase 2A audit **conditional**; policy comparison **post-hoc**, not a second independent holdout |

**WAPE is an error metric, not an accuracy percentage.** Simulated loss is a *dimensionless index*, **not monetary savings**. The data do not reveal true unconstrained demand, on-hand inventory, lost sales, or supplier lead times.

## Live dashboard

Access **https://retailcast-research-zaky.streamlit.app/**. The research prototype presents:

1. **Forecast comparison:** holdout WAPE and weekly observed/predicted unit series.
2. **Product analysis:** per-SKU diagnostic charts and prediction rows.
3. **Inventory scenarios:** hypothetical 1:1, 3:1 and 5:1 shortage/excess penalty settings.
4. **Research & limitations:** source provenance, frozen protocol, data-quality exceptions, and post-hoc policy caveat.

**Verification (7 November 2026):** GitHub Actions run displayed a green result, the public Streamlit app opened, and screenshots showed all four tabs rendering without visible errors. Changing every selector and testing all possible browser states have not been independently established from those screenshots.

## Methodology

- The initial **52 weeks** were used for exploratory SKU selection based on recorded sales-volume and continuity. The next **40 weeks** supported rolling model comparison and residual calibration. The last **12 weeks** formed a separate final forecast holdout.
- MA4, Ridge Regression and Histogram Gradient Boosting were evaluated without random splitting or contemporaneous sales leakage. The primary criterion was pooled WAPE, with MAE, RMSE and macro-MASE as secondary measures.
- Hypothetical one-period capacity targets are compared using shortage/excess penalties. Residual-quantile adjustments use validation residuals only. **Scenario/policy design followed inspection of the forecast holdout**, so no confirmatory inventory-saving claim is made.

## Important limitations

- **Phase 2A remains conditional:** 34,335 identical raw lines were flagged, not proven incorrect; unusual wholesale quantities and catalog code exceptions could affect data quality.
- Recorded *positive* sales are not net sales, unconstrained customer demand or actual stock withdrawals; returns/cancellations are outside this target definition.
- The selected panel excludes some plausible items with unusual StockCode formats. The SKU selection criteria were developed during exploratory audit.
- The data are historical UK retail records from **2009–2011**, not a live Indonesian business dataset.
- The dashboard does **not** issue purchase orders or estimate realized financial savings.

## Repository structure

```text
app.py                      Streamlit research dashboard
core.py                     Frozen-data presentation and integrity functions
data/                      Derived CSV/JSON research outputs (no raw customer table)
docs/                      Provenance and source checksums
tests/                     Core tests and Streamlit AppTest
scripts/smoke_http.py      Local Streamlit HTTP health verification
.github/workflows/         GitHub Actions continuous integration
.streamlit/config.toml     Streamlit interface settings
requirements.txt           Pinned runtime dependencies
RETAILCAST_Research_Preview.html   Read-only offline preview
```

## Run locally

Use **Python 3.13**.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/smoke_http.py
python -m streamlit run app.py
```

The deployed dashboard loads *frozen derived outputs*. Reproducing every raw-data cleaning step from the original workbook requires the separate Phase 2A scripts and the source XLSX, not just this dashboard repository.

## Attribution

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D. Data licensed **CC BY 4.0**. Study's derived artifacts acknowledge this source.

Additional methodological background: Hyndman & Koehler (2006), *International Journal of Forecasting*, https://doi.org/10.1016/j.ijforecast.2006.03.001; MIT OpenCourseWare, *Newsvendor Inventory Problem*.

## Author

**Zaky Ilham Ferdiansyah** · Informatics Engineering · Universitas Dian Nuswantoro

> Applied research portfolio demonstration. Not peer reviewed, not an enterprise deployment, and not verified as a production inventory tool.
