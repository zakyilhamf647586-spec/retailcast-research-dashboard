"""Generate a self-contained, read-only HTML results preview with embedded Plotly."""
from pathlib import Path
from html import escape
import plotly.express as px
import plotly.graph_objects as go
from core import read_data,assess_integrity,MODELS,summary_for_scenario

HERE=Path(__file__).resolve().parent
D=read_data();assess_integrity(D)
metrics=D['metrics'].copy();metrics['model']=metrics['model'].map(MODELS)
fig1=px.bar(metrics.sort_values('wape_pct'),x='wape_pct',y='model',orientation='h',text='wape_pct',
 labels={'model':'','wape_pct':'Holdout WAPE (%)'},color='model',
 color_discrete_sequence=['#2269eb','#749fe7','#9bb8dc'])
fig1.update_traces(texttemplate='%{x:.2f}%',textposition='outside')
fig1.update_layout(height=320,showlegend=False,yaxis={'categoryorder':'total descending'},xaxis_range=[0,70],margin=dict(l=0,r=20,t=15,b=30),paper_bgcolor='#ffffff',plot_bgcolor='#ffffff')
x=summary_for_scenario(D['simulation'],3)
fig2=px.bar(x.sort_values('loss'),x='loss',y='display',color='policy_name',orientation='h',
 labels={'display':'','loss':'Illustrative penalty index (unitless)','policy_name':'Rule'},
 color_discrete_map={'Raw forecast':'#174eaa','Validation-quantile adjusted':'#76a4ed'})
fig2.update_layout(height=420,yaxis={'categoryorder':'total descending'},margin=dict(l=0,r=30,t=15,b=30),legend=dict(orientation='h',y=-.22),paper_bgcolor='#ffffff',plot_bgcolor='#ffffff')
forecast=D['forecast'];w=forecast.groupby(['week_start_monday','model'],as_index=False)[['actual_units','predicted_units']].sum()
fig3=go.Figure()
actual=w[w.model=='moving_average_4']
fig3.add_trace(go.Scatter(x=actual.week_start_monday,y=actual.actual_units,name='Observed units',line=dict(color='#0b224b',width=3)))
for model,color in [('moving_average_4','#1d6aec'),('ridge','#6a98db'),('hist_gradient_boosting','#c99456')]:
 z=w[w.model==model];fig3.add_trace(go.Scatter(x=z.week_start_monday,y=z.predicted_units,name=MODELS[model],line=dict(color=color,width=2,dash='dash')))
fig3.update_layout(height=320,hovermode='x unified',xaxis_title='2011 week starting',yaxis_title='Sales units',margin=dict(l=20,r=20,t=15,b=25),legend=dict(orientation='h',y=-.3),paper_bgcolor='#ffffff',plot_bgcolor='#ffffff')
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>RETAILCAST · Research Preview</title><style>
*{box-sizing:border-box}body{font-family:Inter,"Segoe UI",Arial,sans-serif;margin:0;background:#f3f6fb;color:#102647}.wrap{max-width:1240px;margin:0 auto;padding:26px 26px 50px}
header{padding:38px 36px;border-radius:16px;background:linear-gradient(117deg,#0d2247,#155bb1);color:white;box-shadow:0 13px 35px #1a487d26}
header h1{font-size:clamp(2.6rem,6vw,4rem);line-height:1;letter-spacing:-.055em;margin:12px 0 15px}header h1 span{color:#7bd1ff}
.kicker{font-size:12px;font-weight:700;letter-spacing:.18em;color:#add5ff}header p{max-width:760px;color:#e0edfc;line-height:1.6}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}.stat,.panel{background:white;border:1px solid #dfe6f3;border-radius:13px;padding:18px;box-shadow:0 2px 8px #1829490a}.stat h2{font-size:26px;margin:0 0 5px}.stat p{font-size:12px;color:#62748d;margin:0}.twocol{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{margin-bottom:16px}.panel h2{margin:4px 0 9px;font-size:20px}.eyebrow{color:#1f6ade;font-weight:750;font-size:12px;letter-spacing:.16em}.warning{background:#eaf1ff;border-left:4px solid #266cea;border-radius:6px;padding:16px 20px;margin:19px 0;line-height:1.6}.fine{font-size:13px;color:#576c89;line-height:1.6}a{color:#2165c7}footer{padding-top:15px;font-size:12px;color:#6b7c98}
@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}.twocol{grid-template-columns:1fr}.wrap{padding:16px}header{padding:27px 22px}}
</style></head><body><div class="wrap"><header><div class="kicker">RETAILCAST / SCIENTIFIC PORTFOLIO DEMO · 2026</div><h1>RETAILCAST<span>.</span></h1><p>Retail sales forecasting and exploratory inventory decision simulation. Based on the historical UCI Online Retail II dataset; interactive analytical preview, not a live operational system.</p></header>
<div class="warning"><strong>RESEARCH ONLY.</strong> Recorded positive sales are not uncensored demand. Inventory quantities and financial savings have NOT been observed. Policy comparisons were designed after forecasting holdout analysis and are strictly exploratory.</div>
<div class="grid"><div class="stat"><h2>50</h2><p>Frozen SKU sample</p></div><div class="stat"><h2>12</h2><p>Holdout weeks</p></div><div class="stat"><h2>54.10%</h2><p>MA4 holdout WAPE</p></div><div class="stat"><h2>53.46%</h2><p>Ridge holdout WAPE</p></div></div>
<div class="twocol"><section class="panel"><div class="eyebrow">01 / FORECAST METHODS</div><h2>Forecast accuracy comparison</h2>'''
html+=fig1.to_html(full_html=False,include_plotlyjs=True,config={'responsive':True,'displaylogo':False})
html+='''<p class="fine">Ridge shows a modestly lower final holdout WAPE, but was not the prespecified winner of the earlier 40-week validation.</p></section><section class="panel"><div class="eyebrow">02 / DATA SERIES</div><h2>Rolling weekly prediction</h2>'''
html+=fig3.to_html(full_html=False,include_plotlyjs=False,config={'responsive':True,'displaylogo':False})
html+='''<p class="fine">This is a rolling one-week-ahead evaluation, not a single 12-week forecast.</p></section></div><section class="panel"><div class="eyebrow">03 / SIMULATION</div><h2>Capacity penalty index · illustrative shortage:excess ratio 3:1</h2>'''
html+=fig2.to_html(full_html=False,include_plotlyjs=False,config={'responsive':True,'displaylogo':False})
html+='''<p class="fine">MA4 with residual-quantile adjustment has lower observed index than raw MA4 in this selected scenario; no actual currency, actual stock availability, or confirmed operational cost benefits are measured.</p></section>
<section class="panel"><div class="eyebrow">04 / METHODS & QUALITY</div><h2>Transparency & boundary conditions</h2><p>Phase 2A data quality remains <b>conditional</b>: possible identical repeat transactions, bulk-order concentration, and special product-code exclusions cannot be conclusively reconciled with this public transaction export.</p><p>Historical United Kingdom retail records, 2009–2011. Source: Chen (2012), <a href="https://doi.org/10.24432/C5CG6D">UCI Online Retail II, DOI 10.24432/C5CG6D</a> (CC BY 4.0). No private customer-level rows are displayed.</p></section>
<footer>RETAILCAST Research Preview · Standalone, self-contained interactive HTML · Does not require Streamlit to open. This is a demonstration of frozen results, not the live dashboard.</footer></div></body></html>'''
out=HERE/'RETAILCAST_Research_Preview.html'
out.write_text(html,encoding='utf8')
print('HTML generated',out,'size',out.stat().st_size)
