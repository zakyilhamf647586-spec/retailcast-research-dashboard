"""RETAILCAST Research Dashboard | read-only, historical, exploratory.
Run: streamlit run app.py
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from core import MODELS, POLICIES, assess_integrity, read_data, summary_for_scenario, sku_weekly_frame

st.set_page_config(page_title='RETAILCAST | Research Dashboard',page_icon='📊',layout='wide',initial_sidebar_state='expanded')

@st.cache_data(show_spinner=False)
def load():
    d=read_data();assess_integrity(d);return d

try:
    d=load()
except (FileNotFoundError,ValueError,KeyError) as exc:
    st.error('The dashboard could not verify its frozen research data. Check data/ files.');st.exception(exc);st.stop()

st.markdown('''<style>
:root{--navy:#0d224a;--azure:#2269eb;--muted:#66758b}
.block-container{padding-top:1.6rem;max-width:1400px}
.hero{background:linear-gradient(125deg,#0b2047 0%,#0d3771 57%,#1468d2 100%);border-radius:14px;padding:28px 34px;color:#fff;margin-bottom:16px;position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;right:-55px;top:-100px;width:300px;height:310px;border:42px solid #ffffff17;transform:rotate(22deg)}
.hero .eyebrow{font-size:.78rem;letter-spacing:.2em;color:#b9dcff;font-weight:750}
.hero h1{font-size:2.65rem;line-height:1.06;letter-spacing:-.055em;margin:.3rem 0 .6rem;font-weight:850;color:#fff}
.hero p{color:#e1edff;max-width:730px;font-size:.95rem;margin:0}
.divider-word{font-size:.78rem;letter-spacing:.13em;text-transform:uppercase;color:#62718a;font-weight:760}
.caution{background:#f2f6ff;border-left:4px solid #266be8;border-radius:5px;padding:13px 16px;color:#1f3e67;margin:.8rem 0}
[data-testid="stSidebar"]{background-color:#f3f6fc}
</style>''',unsafe_allow_html=True)

st.markdown('''<section class="hero"><div class="eyebrow">RESEARCH EDITION / 2026 · DATA SCIENCE × DECISION SUPPORT</div>
<h1>RETAILCAST<span style="color:#7fc6ff">.</span></h1>
<p>Intelligent Retail Sales Forecasting &amp; Exploratory Inventory Decision Simulation<br>
Historical retail evidence · 50 SKUs · 2009–2011 · Read-only research prototype</p></section>''',unsafe_allow_html=True)

st.info('**RESEARCH DEMO — NOT AN OPERATIONAL INVENTORY SYSTEM.** Forecasts represent recorded positive sales, not uncensored customer demand. Simulated loss is a dimensionless index (not money), and policies were explored after the final holdout results were viewed.',icon='ℹ️')

with st.sidebar:
    st.markdown('### RETAILCAST / RESEARCH')
    st.caption('Frozen inputs · no retraining · no purchasing')
    st.markdown('**Dataset**  Online Retail II — UCI')
    st.markdown('**Forecast**  Rolling 1-week-ahead')
    st.markdown('**Holdout**  12 weeks · 2011')
    st.markdown('**Product set**  50 SKUs')
    st.divider()
    st.markdown('**Methodological flags**')
    st.caption('Phase 2A: conditional data-quality audit. Phase 4: exploratory/post-hoc policy design.')
    st.markdown('[UCI source and license](https://archive.ics.uci.edu/dataset/502/online+retail+ii)')
    st.caption('Chen (2012) · DOI: 10.24432/C5CG6D · CC BY 4.0')

metrics=d['metrics'].copy();metrics['model_name']=metrics.model.map(MODELS)
ma=float(metrics.loc[metrics.model=='moving_average_4','wape_pct'].iloc[0]); ridge=float(metrics.loc[metrics.model=='ridge','wape_pct'].iloc[0])
cols=st.columns(4)
cols[0].metric('PRODUCTS IN STUDY','50 SKU')
cols[1].metric('HOLDOUT WINDOW','12 weeks')
cols[2].metric('MA4 · HOLDOUT WAPE',f'{ma:.2f}%')
cols[3].metric('RIDGE · HOLDOUT WAPE',f'{ridge:.2f}%')

overview,per_sku,simulation,research=st.tabs(['01 / Forecast comparison','02 / Product analysis','03 / Inventory scenarios','04 / Research & limitations'])

with overview:
    st.subheader('How did the forecasting models compare?')
    st.caption('One-week-ahead predictions for 50 SKUs × 12 holdout weeks. Lower WAPE is better. The model choice was frozen on the earlier validation window.')
    left,right=st.columns([1,1.2],gap='large')
    with left:
        vals=metrics.sort_values('wape_pct').copy()
        fig=px.bar(vals,x='wape_pct',y='model_name',orientation='h',text='wape_pct',labels={'wape_pct':'WAPE (%)','model_name':''},color='model_name',
            color_discrete_map={MODELS['moving_average_4']:'#1c61d5',MODELS['ridge']:'#6d8cbb',MODELS['hist_gradient_boosting']:'#b9c9df'})
        fig.update_traces(texttemplate='%{x:.2f}%',textposition='outside',cliponaxis=False)
        fig.update_layout(showlegend=False,height=320,margin=dict(l=0,r=55,b=15,t=25),xaxis_range=[0,67],yaxis={'categoryorder':'total descending'},plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,width='stretch')
    with right:
        t=d['forecast'].groupby(['week_start_monday','model'],as_index=False)[['actual_units','predicted_units']].sum()
        actual=t[t.model=='moving_average_4'][['week_start_monday','actual_units']]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=actual.week_start_monday,y=actual.actual_units,name='Recorded sales',mode='lines+markers',line=dict(color='#0d224a',width=3)))
        for model,col in [('moving_average_4','#2269eb'),('ridge','#7596ce'),('hist_gradient_boosting','#b0c1d5')]:
            q=t[t.model==model]
            fig.add_trace(go.Scatter(x=q.week_start_monday,y=q.predicted_units,name=MODELS[model],mode='lines',line=dict(color=col,width=2,dash='dash' if model!='moving_average_4' else 'solid')))
        fig.update_layout(title='Weekly portfolio sales vs. rolling forecasts',xaxis_title='Week starting',yaxis_title='Units',height=320,margin=dict(l=0,r=0,b=15,t=40),legend=dict(orientation='h',y=-.28),hovermode='x unified')
        st.plotly_chart(fig,width='stretch')
    st.markdown('<div class="caution"><b>Interpretation:</b> Ridge has a slightly lower observed holdout WAPE than MA4, but the short-window uncertainty analysis does not establish superiority. MA4 remains the prespecified validation-selected method.</div>',unsafe_allow_html=True)
    st.dataframe(metrics[['model_name','wape_pct','mae','rmse','macro_mase']].rename(columns={'model_name':'Model','wape_pct':'WAPE (%)','mae':'MAE (units)','rmse':'RMSE','macro_mase':'Macro-MASE'}).round(3),hide_index=True,width='stretch')

with per_sku:
    st.subheader('Investigate one product across the 12 holdout weeks')
    stockcodes=sorted(d['sku'].stockcode.astype(str).tolist())
    code=st.selectbox('StockCode',stockcodes,key='product_sku')
    frame=sku_weekly_frame(d['forecast'],code)
    i=frame[frame.model=='moving_average_4']
    st.caption('A stock code identifies a catalog item. The dashboard does not infer SKU descriptions or prices from model inputs.')
    c1,c2,c3=st.columns(3)
    c1.metric('Recorded sales units',f'{i.actual_units.sum():,.0f}')
    c2.metric('MA4 total predicted units',f'{i.predicted_units.sum():,.0f}')
    c3.metric('MA4 absolute errors total',f'{abs(i.actual_units-i.predicted_units).sum():,.0f}')
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=i.week_start_monday,y=i.actual_units,mode='lines+markers',name='Observed units',line=dict(color='#0c224a',width=3)))
    for model,col in [('moving_average_4','#276ce9'),('ridge','#7ca0d2'),('hist_gradient_boosting','#d09046')]:
        q=frame[frame.model==model]
        fig.add_trace(go.Scatter(x=q.week_start_monday,y=q.predicted_units,mode='lines+markers',name=MODELS[model],line=dict(color=col,width=2,dash='dot')))
    fig.update_layout(height=380,margin=dict(l=0,r=0,b=40,t=25),xaxis_title='Week starting',yaxis_title='Units',hovermode='x unified')
    st.plotly_chart(fig,width='stretch')
    st.dataframe(frame.assign(model=frame.model.map(MODELS)).rename(columns={'model':'Model','week_start_monday':'Week','actual_units':'Recorded units','predicted_units':'Predicted units'}),hide_index=True,width='stretch')

with simulation:
    st.subheader('Inventory capacity scenarios — illustrative, not actionable orders')
    st.caption('Each week is an independent hypothetical capacity decision. No stock-on-hand, carryover, supplier lead time, or real purchasing costs are modeled.')
    left,right=st.columns(2)
    shortage=left.selectbox('Assumed shortage : excess penalty',['1 : 1','3 : 1','5 : 1'],index=1)
    ratio=int(shortage[0]);selected_sku=right.selectbox('SKU scope',['All 50 SKUs']+sorted(d['sku'].stockcode.astype(str).tolist()))
    code=None if selected_sku=='All 50 SKUs' else selected_sku
    x=summary_for_scenario(d['simulation'],ratio,code).sort_values('loss')
    baseline=float(x.loc[(x.model=='moving_average_4')&(x.policy=='point_forecast'),'loss'].iloc[0])
    best=x.iloc[0]
    k1,k2,k3=st.columns(3)
    k1.metric('Lowest observed penalty index',f'{best.loss:,.0f}')
    k2.metric('Reference MA4 raw index',f'{baseline:,.0f}')
    k3.metric('Difference vs reference',f'{100*(best.loss/baseline-1):+.2f}%' if baseline>0 else 'N/A · zero baseline')
    fig=px.bar(x,y='display',x='loss',orientation='h',labels={'display':'','loss':'Simulated penalty index (dimensionless)'},color='policy_name',
        color_discrete_map={'Raw forecast':'#174eaa','Validation-quantile adjusted':'#6c9eeb'})
    fig.update_layout(height=400,margin=dict(l=0,r=20,b=10,t=20),legend_title_text='Policy',yaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig,width='stretch')
    st.dataframe(x[['model_name','policy_name','loss','coverage_proxy_pct','excess_units','uncovered_units','capacity_units']].rename(columns={
        'model_name':'Model','policy_name':'Policy','loss':'Penalty index','coverage_proxy_pct':'Recorded-sales coverage proxy (%)','excess_units':'Excess capacity (units)',
        'uncovered_units':'Uncovered recorded sales (units)','capacity_units':'Capacity target (units)'}).round(2),hide_index=True,width='stretch')
    st.warning('The smallest observed scenario loss is descriptive only. These policy choices were investigated after holdout forecast results were inspected. The figures are NOT realized financial savings, real inventory service levels, or purchase recommendations.')

with research:
    st.subheader('Research protocol, data provenance, and open limitations')
    r=d['audit'];s=d['protocol']
    ca,cb,cc=st.columns(3)
    ca.metric('Original line items',f"{r['rows']:,}")
    cb.metric('Exact duplicates flagged',f"{r['exact_duplicate_rows_FLAG_ONLY_NOT_REMOVED']:,}")
    cc.metric('Original distinct StockCodes',f"{r['distinct_stockcodes']:,}")
    st.markdown('**Evaluation protocol**')
    st.markdown('- First 52 complete weeks: exploratory SKU selection; 40 subsequent weeks: model selection and residual calibration; last 12 weeks: final forecast holdout.\n- Model evaluation is a sequential, rolling **one-week-ahead** test. Actual observations from an earlier holdout week may be used for subsequent forecast origins.\n- Final forecast model: **MA4** remained the prespecified validation-selected incumbent, despite a small favorable Ridge point estimate in the holdout.')
    st.markdown('**Open quality-audit exceptions (Phase 2A)**')
    st.markdown('- The 34,335 identical raw line items were **flagged, not automatically deleted**; genuine independent purchases can appear identical.\n- Cancellation/return invoices were excluded from the positive recorded-sales target, so this is not net customer demand.\n- Nonstandard StockCodes were excluded using a documented heuristic; it can omit legitimate items.\n- Large orders/outlying quantities were not automatically corrected. A retrospective follow-up is documented separately.')
    st.markdown('**Business-simulation assumptions**')
    st.markdown('- One-week hypothetical capacity target with weekly resets and zero lead time.\n- Excess penalty index fixed at 1, shortage penalty index set to 1, 3, or 5.\n- Adjustments use validation-only residual quantiles, but the policy comparison was devised **after** the holdout was revealed.\n- No current inventory, actual lead times, lost demand, or real unit economics are available.')
    st.markdown('**Data citation**')
    st.markdown('Chen, D. (2012). *Online Retail II*. UCI Machine Learning Repository. [DOI: 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D). CC BY 4.0. Historical UK transactions (2009–2011).')
    st.caption('Dashboard renders frozen research CSV outputs. It does not fetch customer-level data, retrain models, submit purchase orders, or call external business APIs.')

st.divider()
st.caption('RETAILCAST / Research Prototype · Historical Data · No operational warranty · 2026')
