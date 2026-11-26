"""Withhold unvalidated sentiment; sample count is not semantic validation."""
REASON = '社区分类尚未通过语义验证，且未覆盖小红书、抖音和X；暂停社区分及综合分，交易因子单独展示。'

def withhold_sentiment(data):
    data['assessment'] = dict(status='withheld', validated=False, reason=REASON,
        missing_platforms=['小红书', '抖音', 'X'],
        release_requirements=['独立人工标注样本与误判审查', '未识别与真正中性分开', '跨平台按时间和中性关键词抽样并去重', '按平台披露覆盖与缺失，不按情绪结论选样'],
        note='下列多空和恐慌命中只供审阅；多空方向不等于情绪，未命中不等于中性。')
    data['summary'].update(score=None, community=None, coverage=REASON, sentiment_validated=False)
    data['intraday'].update(community=None, reliable=False, sentiment_validated=False)
    data['last_valid_daily'] = None
    for key in ['history', 'community_history']:
        for row in data.get(key, []):
            if 'score' in row: row['score'] = None
            if 'community' in row: row['community'] = None
            row['sentiment_validated'] = False
    for key in ['groups', 'intraday_groups', 'channels', 'intraday_channels']:
        for row in data.get(key, []):
            row['score'] = None
            row['reliable'] = False
            if 'bull' in row and 'bear' in row:
                row['unclassified_or_mixed'] = row['n'] - row['bull'] - row['bear']
                row['neutral'] = None
                row['directional_match_pct'] = 100 * (row['bull'] + row['bear']) / row['n'] if row['n'] else None
    return data
