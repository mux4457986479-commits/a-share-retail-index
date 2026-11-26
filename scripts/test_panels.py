import unittest,math
from datetime import date,timedelta
from diagnostic_panels import build_panels

class Panels(unittest.TestCase):
 def rows(self,n=81,constant=False):
  return [dict(date=(date(2026,1,1)+timedelta(days=i)).isoformat(),close=100 if constant else 100*math.exp(.001*i+.003*math.sin(i)))for i in range(n)]
 def test_realized_volatility_uses_twenty_returns_and_252_annualization(self):
  import statistics
  rows=self.rows();r=build_panels({'创业板指':rows},[],rows[-1]['date'])['market']['benchmarks'][2]
  expected=statistics.stdev([math.log(rows[i]['close']/rows[i-1]['close'])for i in range(61,81)])*math.sqrt(252)*100
  self.assertAlmostEqual(r['rv20_annual_pct'],expected);self.assertEqual(r['rv_baseline_n'],60)
 def test_today_is_excluded_from_percentile_and_minimum_history_is_enforced(self):
  rows=self.rows(80,True);r=build_panels({'上证指数':rows},[],rows[-1]['date'])['market']['benchmarks'][0];self.assertIsNone(r['rv_percentile'])
  rows=self.rows(81,True);r=build_panels({'上证指数':rows},[],rows[-1]['date'])['market']['benchmarks'][0];self.assertEqual(r['rv_percentile'],50);self.assertLess(r['rv_baseline_end'],r['date'])
 def test_missing_and_future_series_are_not_backfilled(self):
  rows=self.rows();r=build_panels({'上证指数':rows},[],rows[-2]['date']);self.assertEqual(r['market']['benchmarks'][0]['date'],rows[-2]['date']);self.assertIsNone(r['market']['benchmarks'][1]['rv20_annual_pct']);self.assertIsNone(r['total_score'])
 def test_balance_accounting_and_five_observation_change(self):
  margin=[dict(date=f'2026-01-0{i+1}',balance=100-2*i,buy=10)for i in range(6)]
  r=build_panels({},margin,'2026-01-06')['leverage'];self.assertEqual(r['net1'],-2);self.assertEqual(r['net5'],-10);self.assertEqual(r['repay_estimated'],12);self.assertAlmostEqual(r['buy_repay_ratio'],10/12)
 def test_stale_leverage_and_impossible_repayment_are_not_displayed(self):
  margin=[dict(date='2026-01-01',balance=100,buy=1),dict(date='2026-01-02',balance=200,buy=1)]
  r=build_panels({},margin,'2026-01-02')['leverage'];self.assertIsNone(r['repay_estimated'])
  r=build_panels({},margin,'2026-01-10')['leverage'];self.assertIsNone(r['balance']);self.assertEqual(r['lag_calendar_days'],8)
