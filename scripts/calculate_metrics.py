from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取510300清洗后的数据
data_path = project_root / "data" / "processed" / "510300_clean.csv"

df = pd.read_csv(data_path, encoding="utf-8-sig")

# 将日期转换为日期类型
df["date"] = pd.to_datetime(df["date"])

# 按日期从早到晚排序
df = df.sort_values("date").reset_index(drop=True)

# 根据收盘价计算日收益率
# pct_change表示今天收盘价相对于昨天的变化比例
df["daily_return"] = df["close"].pct_change()

# 删除第一行，因为第一天没有前一天价格，收益率为空
df = df.dropna(subset=["daily_return"]).reset_index(drop=True)

# 计算累计净值
# 初始净值设为1
df["net_value"] = (1 + df["daily_return"]).cumprod()

# 区间累计收益率
cumulative_return = df["net_value"].iloc[-1] - 1

# 计算实际交易天数
trading_days = len(df)

# 年化收益率
# 假设一年约有252个交易日
annual_return = (1 + cumulative_return) ** (252 / trading_days) - 1

# 年化波动率
annual_volatility = df["daily_return"].std() * np.sqrt(252)

# 计算历史最高净值
df["running_max"] = df["net_value"].cummax()

# 计算每日回撤
df["drawdown"] = df["net_value"] / df["running_max"] - 1

# 最大回撤
maximum_drawdown = df["drawdown"].min()
# 假设无风险利率为0
risk_free_rate = 0

# 计算日均收益率
average_daily_return = df["daily_return"].mean()

# 计算日收益率标准差
daily_volatility = df["daily_return"].std()

# 计算夏普比率
# 夏普比率 = 年化收益率 / 年化波动率
sharpe_ratio = (
    annual_return - risk_free_rate
) / annual_volatility

# 计算卡玛比率
# 卡玛比率 = 年化收益率 / 最大回撤绝对值
calmar_ratio = annual_return / abs(maximum_drawdown)

# 计算胜率
# 这里的胜率定义为日收益率大于0的交易日占比
win_rate = (df["daily_return"] > 0).mean()
# 输出结果
print("510300沪深300ETF基准表现")
print("-" * 40)
print(f"数据开始日期：{df['date'].iloc[0].date()}")
print(f"数据结束日期：{df['date'].iloc[-1].date()}")
print(f"交易日数量：{trading_days}")
print(f"区间累计收益率：{cumulative_return:.2%}")
print(f"年化收益率：{annual_return:.2%}")
print(f"年化波动率：{annual_volatility:.2%}")
print(f"最大回撤：{maximum_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"卡玛比率：{calmar_ratio:.2f}")
print(f"日收益胜率：{win_rate:.2%}")

# 保存带有收益率和回撤的数据
result_path = project_root / "data" / "processed" / "510300_metrics_data.csv"

df.to_csv(
    result_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n计算结果数据已保存到：{result_path}")