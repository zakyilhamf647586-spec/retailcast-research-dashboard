"""Pure analytics functions for the RETAILCAST read-only research dashboard.
No training, no live inventory transactions, no Streamlit dependencies.
"""
from pathlib import Path
import json
import pandas as pd

DATA=Path(__file__).resolve().parent/'data'
MODELS={'moving_average_4':'Moving average · 4 weeks','ridge':'Ridge regression',
        'hist_gradient_boosting':'Histogram gradient boosting'}
POLICIES={'point_forecast':'Raw forecast','validation_quantile_adjusted':'Validation-quantile adjusted'}


def read_data(directory=DATA):
    d=Path(directory)
    files={
        'forecast':pd.read_csv(d/'final_holdout_predictions.csv',dtype={'stockcode':'string'},parse_dates=['week_start_monday']),
        'metrics':pd.read_csv(d/'final_holdout_metrics.csv'),
        'validation_metrics':pd.read_csv(d/'validation_metrics.csv'),
        'simulation':pd.read_csv(d/'simulation_detail.csv',dtype={'stockcode':'string'},parse_dates=['week_start_monday']),
        'sku':pd.read_csv(d/'selected_50_skus_continuous.csv',dtype={'stockcode':'string'}),
        'weekly':pd.read_csv(d/'weekly_panel_50_skus_continuous.csv',dtype={'stockcode':'string'},parse_dates=['week_start_monday']),
        'audit':json.loads((d/'audit_report.json').read_text(encoding='utf8')),
        'protocol':json.loads((d/'simulation_metadata.json').read_text(encoding='utf8'))
    }
    return files


def assess_integrity(d):
    f=d['forecast'];s=d['simulation']; sku=d['sku']
    if len(sku)!=50 or sku['stockcode'].nunique()!=50:raise ValueError('SKU file is not frozen 50 SKU selection')
    if len(f)!=1800 or len(s)!=10800:raise ValueError('Prediction/simulation size mismatch')
    if f[['model','stockcode','week_start_monday']].duplicated().any():raise ValueError('Duplicate forecast keys')
    if s[['model','stockcode','week_start_monday','policy','shortage_penalty','excess_penalty']].duplicated().any():
        raise ValueError('Duplicate simulation keys')
    if set(f.model)!=set(MODELS) or set(s.model)!=set(MODELS):raise ValueError('Unexpected model')
    if set(s.policy)!=set(POLICIES):raise ValueError('Unexpected policy')
    if set(s.shortage_penalty)!={1,3,5} or set(s.excess_penalty)!={1}:raise ValueError('Unexpected penalty scenario')
    if f.week_start_monday.nunique()!=12 or f.stockcode.nunique()!=50:raise ValueError('Unexpected holdout shape')
    if d['protocol']['business_simulation_devised_after_phase3_holdout_was_seen'] is not True:
        raise ValueError('Research caveat missing')
    if (f['actual_units']<0).any() or (f['predicted_units']<0).any():raise ValueError('Negative forecast values')
    if (s['stock_capacity_target_units']<0).any():raise ValueError('Negative capacity')
    return True


def summary_for_scenario(sim, shortage=3, stockcode=None):
    x=sim[(sim.shortage_penalty==shortage)&(sim.excess_penalty==1)]
    if stockcode is not None:x=x[x.stockcode==stockcode]
    grouped=x.groupby(['model','policy'],sort=True).agg(
        loss=('simulated_loss_index','sum'),
        recorded_units=('actual_units','sum'),
        covered_units=('simulated_recorded_sales_covered_units','sum'),
        excess_units=('simulated_excess_capacity_units','sum'),
        uncovered_units=('simulated_uncovered_sales_units','sum'),
        capacity_units=('stock_capacity_target_units','sum'),
        observations=('stockcode','size')).reset_index()
    grouped['coverage_proxy_pct']=100*grouped['covered_units']/grouped['recorded_units']
    grouped['model_name']=grouped['model'].map(MODELS)
    grouped['policy_name']=grouped['policy'].map(POLICIES)
    grouped['display']=grouped['model_name']+' · '+grouped['policy_name']
    return grouped


def sku_weekly_frame(forecast,stockcode):
    x=forecast.loc[forecast.stockcode==stockcode,['model','week_start_monday','actual_units','predicted_units']]
    if x.empty:raise ValueError('Unknown SKU')
    return x.copy()
