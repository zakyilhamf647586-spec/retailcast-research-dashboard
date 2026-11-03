"""Exercises Streamlit top-level paths using fake UI only; not a browser/runtime test."""
import os,sys,types,subprocess,unittest
from pathlib import Path

class DashboardSmokeTest(unittest.TestCase):
 def test_all_tabs_execute_without_streamlit_runtime(self):
  code=r'''
import types,sys,importlib.util
from pathlib import Path

class Fake:
 def __enter__(self): return self
 def __exit__(self,*a):return False
 def __getattr__(self,name):
  def f(*args,**kwargs):return None
  return f
 def metric(self,*args,**kwargs): pass
 def selectbox(self,label,options,**kwargs):return options[kwargs.get('index',0)]
fake=Fake()
m=types.ModuleType('streamlit')
m.sidebar=fake
m.cache_data=lambda **kwargs:lambda fn:fn
m.columns=lambda items,**kwargs:[Fake() for _ in range(items if isinstance(items,int) else len(items))]
m.tabs=lambda labels:[Fake() for _ in labels]
m.selectbox=lambda label,options,**kwargs:options[kwargs.get('index',0)]
m.plotly_chart=lambda plot,**kwargs:assert_plot(plot)
m.set_page_config=lambda **kwargs:None
m.stop=lambda :(_ for _ in ()).throw(RuntimeError('st.stop called'))
def assert_plot(fig):
 assert len(fig.data)>0,'empty plot'
for name in ['markdown','info','caption','divider','subheader','warning','error','exception','dataframe']:
 setattr(m,name,lambda *a,**kw:None)
sys.modules['streamlit']=m
import app
assert app.ma>50 and app.ridge>50
'''
  p=subprocess.run([sys.executable,'-c',code],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr)
