import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import read_data,assess_integrity,summary_for_scenario,sku_weekly_frame

class DashboardDataTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.d=read_data()
 def test_data_integrity(self):self.assertTrue(assess_integrity(self.d))
 def test_frozen_holdout_models(self):
  g=self.d['forecast'].groupby('model').size()
  self.assertEqual(set(g.index),{'ridge','moving_average_4','hist_gradient_boosting'})
  self.assertTrue((g==600).all())
 def test_scenario_3_to_1_ma4(self):
  z=summary_for_scenario(self.d['simulation'],3)
  ma=z[(z.model=='moving_average_4')&(z.policy=='point_forecast')]
  adj=z[(z.model=='moving_average_4')&(z.policy=='validation_quantile_adjusted')]
  self.assertEqual(int(ma.loss.iloc[0]),277905)
  self.assertEqual(int(adj.loss.iloc[0]),256486)
  self.assertEqual(len(z),6)
 def test_different_sku_scope(self):
  s=sorted(self.d['sku'].stockcode)[0]
  self.assertEqual(len(sku_weekly_frame(self.d['forecast'],s)),36)
  z=summary_for_scenario(self.d['simulation'],3,s)
  self.assertTrue((z.observations==12).all())
 def test_validation_report_and_holdout_differ(self):
  a=self.d['validation_metrics'].set_index('model').loc['moving_average_4','wape_pct']
  b=self.d['metrics'].set_index('model').loc['moving_average_4','wape_pct']
  self.assertAlmostEqual(float(a),73.633446,places=5)
  self.assertAlmostEqual(float(b),54.09801107,places=5)
 def test_all_scenarios_have_same_sample(self):
  for ratio in (1,3,5):
   x=summary_for_scenario(self.d['simulation'],ratio)
   self.assertTrue((x.observations==600).all())
   self.assertTrue((x.recorded_units==243850).all())
 def test_baseline_description_never_currency(self):
  self.assertTrue(self.d['protocol']['all_reported_costs_are_unitless_penalty_indices_not_money'])

if __name__=='__main__':unittest.main()
