"""Independent market, community and leverage observations; no synthetic total."""
import math,statistics
from datetime import date

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def valid_series(rows,anchor):
    unique={}
    for row in rows:
        try:day=date.fromisoformat(row['date'])
        except (KeyError,ValueError,TypeError):continue
        if day.isoformat()<=anchor and finite(row.get('close')) and row['close']>0:unique[row['date']]=row
    return [unique[d] for d in sorted(unique)]

def rv20(rows,end):
    if end<20:return None
    returns=[math.log(rows[i]['close']/rows[i-1]['close']) for i in range(end-19,end+1)]
    return statistics.stdev(returns)*math.sqrt(252)*100

def build_panels(series,margin,anchor):
    benchmarks=[]
    for label in ['上证指数','沪深300','创业板指']:
        rows=valid_series(series.get(label,[]),anchor)
        if not rows or rows[-1]['date']!=anchor:
            benchmarks.append(dict(name=label,status='该完整交易日行情缺失',date=rows[-1]['date']if rows else None,return5_pct=None,drawdown20_pct=None,rv20_annual_pct=None,rv_percentile=None));continue
        close=rows[-1]['close'];vol=rv20(rows,len(rows)-1)
        baseline=[(rows[i]['date'],rv20(rows,i)) for i in range(20,len(rows)-1)][-252:]
        values=[v for _,v in baseline]
        pct=100*(sum(v<vol for v in values)+0.5*sum(v==vol for v in values))/len(values) if vol is not None and len(values)>=60 else None
        benchmarks.append(dict(name=label,status='行情可用',date=anchor,close=close,return5_pct=100*(close/rows[-6]['close']-1)if len(rows)>=6 else None,drawdown20_pct=100*(close/max(r['close']for r in rows[-20:])-1)if len(rows)>=20 else None,rv20_annual_pct=vol,rv_percentile=pct,rv_baseline_n=len(values),rv_baseline_start=baseline[0][0]if baseline else None,rv_baseline_end=baseline[-1][0]if baseline else None))
    unique={}
    for row in margin:
        try:day=date.fromisoformat(row['date'])
        except (KeyError,ValueError,TypeError):continue
        if day.isoformat()<=anchor and finite(row.get('balance')) and row['balance']>=0:unique[row['date']]=row
    eligible=[unique[d]for d in sorted(unique)]
    leverage=dict(date=None,status='融资数据缺失',unit='亿元',balance=None,net1=None,net5=None,change5_pct=None,buy=None,repay_estimated=None,buy_repay_ratio=None,lag_calendar_days=None)
    if eligible:
        last=eligible[-1];lag=(date.fromisoformat(anchor)-date.fromisoformat(last['date'])).days
        leverage.update(date=last['date'],lag_calendar_days=lag,status='可用（偿还为推算）'if lag<=4 else'数据过旧，停止展示当前指标')
        if lag<=4:
            net=last['balance']-eligible[-2]['balance']if len(eligible)>=2 else None
            buy=last.get('buy')if finite(last.get('buy'))and last['buy']>=0 else None
            repay=buy-net if buy is not None and net is not None and buy-net>=0 else None
            net5=last['balance']-eligible[-6]['balance']if len(eligible)>=6 else None
            leverage.update(balance=last['balance'],net1=net,net5=net5,change5_pct=100*net5/eligible[-6]['balance']if net5 is not None and eligible[-6]['balance']>0 else None,buy=buy,repay_estimated=repay,buy_repay_ratio=buy/repay if buy is not None and repay is not None and repay>0 else None)
    return dict(schema_version=1,asof=anchor,total_score=None,
        market=dict(benchmarks=benchmarks,source='腾讯指数日线',source_url='https://web.ifzq.gtimg.cn/',definition='20日对数收益样本标准差×√252；分位只对当前可用历史计算，至少60个既往有效观测，排除当日。已实现波动不是期权隐含波动，也不是VIX。',missing=['全市场涨跌广度','期权隐含波动率与Put/Call比','期货基差']),
        community=dict(status='暂停评分',reason='语义分类与跨平台代表性尚未验证；样本数、命中数与情绪强度分开。',total_score=None),
        leverage=dict(**leverage,source='同花顺沪深北两融汇总',source_url='https://data.10jqka.com.cn/market/rzrq/',definition='推算偿还=融资买入−融资余额日变化；余额变化反映未偿本金变化，不直接等于股价下跌。偿还不能区分主动还款与强平。',methodology_url='https://www.sse.com.cn/market/othersdata/margin/detail/index.shtml',missing=['实际强平金额','账户维持担保比例分布','场外杠杆规模']))
