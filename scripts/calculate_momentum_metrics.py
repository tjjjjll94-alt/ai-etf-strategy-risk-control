from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取动量策略回测结果
file_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_top2_backtest.csv"
)

df = pd.read_csv(file_path, encoding="utf-8-sig")

# 转换日期
df["date"] = pd.to_datetime(df["date"])

# 获取策略收益率
returns = df["strategy_return_after_cost"].dropna()

# 获取策略净值
net_value = df["strategy_net_value"].dropna()

# 交易日数量
trading_days = len(returns)

# 累计收益率
cumulative_return = net_value.iloc[-1] - 1

# 年化收益率
annual_return = (
    (1 + cumulative_return) ** (252 / trading_days) - 1
)

# 年化波动率
annual_volatility = returns.std() * np.sqrt(252)

# 计算回撤
running_max = net_value.cummax()
drawdown = net_value / running_max - 1

# 最大回撤
maximum_drawdown = drawdown.min()

# 夏普比率
sharpe_ratio = annual_return / annual_volatility

# 卡玛比率
calmar_ratio = annual_return / abs(maximum_drawdown)

# 胜率
win_rate = (returns > 0).mean()

# 换手次数
total_turnover = df["turnover"].sum()

# 样本年数
sample_years = trading_days / 252

# 年化换手次数
annual_turnover = total_turnover / sample_years

# 单次调仓成本假设
transaction_cost_rate = 0.001

# 总交易成本
total_transaction_cost = (
    total_turnover * transaction_cost_rate
)

# 输出结果
print("60日动量前2名ETF轮动策略")
print("-" * 40)
print(f"数据开始日期：{df['date'].min().date()}")
print(f"数据结束日期：{df['date'].max().date()}")
print(f"累计收益率：{cumulative_return:.2%}")
print(f"年化收益率：{annual_return:.2%}")
print(f"年化波动率：{annual_volatility:.2%}")
print(f"最大回撤：{maximum_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"卡玛比率：{calmar_ratio:.2f}")
print(f"胜率：{win_rate:.2%}")
print(f"累计换手次数：{total_turnover:.0f}")
print(f"年化换手次数：{annual_turnover:.2f}")
print(f"累计交易成本：{total_transaction_cost:.2%}")

# 计算回撤并保存
df["running_max"] = df["strategy_net_value"].cummax()
df["drawdown"] = (
    df["strategy_net_value"] / df["running_max"] - 1
)

save_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_top2_metrics.csv"
)

df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n指标数据已保存到：{save_path}")