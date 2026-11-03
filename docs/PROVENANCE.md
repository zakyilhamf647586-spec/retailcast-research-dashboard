# Frozen data lineage / provenance

| Local file in `data/` | Source phase / path | Meaning |
| --- | --- | --- |
| `final_holdout_predictions.csv` | Phase 3 / `results/final_holdout_predictions.csv` | 1,800 rolling 1-week-ahead predictions |
| `final_holdout_metrics.csv` | Phase 3 / `results/final_holdout_metrics.csv` | WAPE/MAE/RMSE, 3 models |
| `validation_metrics.csv` | Phase 2C / `results/model_comparison.csv` | Prior 40-week model selection results |
| `simulation_detail.csv` | Phase 4 / `results/simulation_detail.csv` | 10,800 synthetic indexed penalty observations |
| `simulation_scenario_comparison.csv` | Phase 4 / `results/simulation_scenario_comparison.csv` | Aggregate scenario cross-check (not re-trained) |
| `selected_50_skus_continuous.csv` | Phase 2A / `results/selected_50_skus_continuous.csv` | Frozen SKU sample |
| `weekly_panel_50_skus_continuous.csv` | Phase 2A / `results/weekly_panel_50_skus_continuous.csv` | Historical observed positive weekly sales |
| `audit_report.json` | Phase 2A / `results/audit_report.json` | Original quality flags and target definitions |
| `simulation_metadata.json` | Phase 4 / `results/simulation_metadata.json` | Policy caveats, calibration checks and scenario assumptions |

Original source: Chen, D. (2012), UCI Machine Learning Repository DOI 10.24432/C5CG6D. This demo does not contact a live business system.
