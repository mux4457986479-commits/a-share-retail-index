import unittest
from publication_guard import withhold_sentiment

class PublicationGuard(unittest.TestCase):
 def fixture(self):
  return dict(summary=dict(score=46,community=53,trade=35.6),intraday=dict(community=53,reliable=True),last_valid_daily=dict(score=46),history=[dict(score=46,community=53,trade=35.6)],community_history=[dict(community=53)],groups=[dict(score=53,reliable=True)],intraday_groups=[],channels=[dict(n=100,bull=6,bear=4,neutral=90,score=51)],intraday_channels=[])
 def test_sufficient_count_cannot_enable_unvalidated_score(self):
  d=withhold_sentiment(self.fixture());self.assertIsNone(d['summary']['score']);self.assertIsNone(d['intraday']['community']);self.assertFalse(d['intraday']['reliable']);self.assertEqual(d['summary']['trade'],35.6)
 def test_unknown_is_not_neutral(self):
  r=withhold_sentiment(self.fixture())['channels'][0];self.assertIsNone(r['neutral']);self.assertEqual(r['unclassified_or_mixed'],90);self.assertEqual(r['directional_match_pct'],10)
 def test_history_and_last_valid_do_not_resurrect_invalid_score(self):
  d=withhold_sentiment(self.fixture());self.assertIsNone(d['last_valid_daily']);self.assertIsNone(d['history'][0]['score']);self.assertIsNone(d['community_history'][0]['community'])
 def test_missing_platforms_are_explicit(self):
  d=withhold_sentiment(self.fixture());self.assertEqual(d['assessment']['missing_platforms'],['小红书','抖音','X']);self.assertFalse(d['assessment']['validated'])
