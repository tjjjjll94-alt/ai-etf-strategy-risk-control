from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取动量策略回测数据
input_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_top2_metrics.csv"
)

df = pd.read_csv(input_path, encoding="utf-8-sig")
df["date"] = pd.to_datetime(df["date"])

# 计算过去20个交易日的策略波动率
# shift(1)确保今天的过滤条件只使用昨天及以前的信息
df["volatility_20"] = (
    df["strategy_return_after_cost"]
    .rolling(20)
    .std()
    .shift(1)
    * np.sqrt(252)
)

# 设置波动率阈值
volatility_threshold = 0.30

# 波动率不超过30%时允许持仓
df["risk_on"] = (
    df["volatility_20"] <= volatility_threshold
).astype(int)

# 空仓状态变化也视为一次调仓
df["risk_switch"] = (
    df["risk_on"].diff().abs().fillna(0)
)

# 风险过滤后的策略收益
df["filtered_return_before_cost"] = (
    df["strategy_return_after_cost"]
    * df["risk_on"]
)

# 风险开关调仓成本
risk_switch_cost = 0.001

df["filtered_return"] = (
    df["filtered_return_before_cost"]
    - df["risk_switch"] * risk_switch_cost
)

# 第一段没有足够波动率数据，收益设为0
df.loc[df["volatility_20"].isna(), "filtered_return"] = 0

# 计算风险控制后的净值
df["filtered_net_value"] = (
    1 + df["filtered_return"]
).cumprod()

# 计算回撤
df["filtered_running_max"] = (
    df["filtered_net_value"].cummax()
)

df["filtered_drawdown"] = (
    df["filtered_net_value"]
    / df["filtered_running_max"]
    - 1
)

# 计算基础指标
returns = df["filtered_return"]
net_value = df["filtered_net_value"]

cumulative_return = net_value.iloc[-1] - 1

annual_return = (
    (1 + cumulative_return) ** (252 / len(returns)) - 1
)

annual_volatility = returns.std() * np.sqrt(252)

maximum_drawdown = df["filtered_drawdown"].min()

sharpe_ratio = annual_return / annual_volatility

calmar_ratio = annual_return / abs(maximum_drawdown)

win_rate = (returns > 0).mean()

print("波动率过滤后的动量策略")
print("-" * 40)
print(f"累计收益率：{cumulative_return:.2%}")
print(f"年化收益率：{annual_return:.2%}")
print(f"年化波动率：{annual_volatility:.2%}")
print(f"最大回撤：{maximum_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"卡玛比率：{calmar_ratio:.2f}")
print(f"胜率：{win_rate:.2%}")
print(f"风险开关次数：{df['risk_switch'].sum():.0f}")

# 保存结果
save_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_vol_filter_backtest.csv"
)

df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n结果已保存到：{save_path}")