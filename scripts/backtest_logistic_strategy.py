from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取模型预测结果
prediction_path = (
    project_root
    / "data"
    / "processed"
    / "logistic_test_predictions.csv"
)

predictions = pd.read_csv(
    prediction_path,
    encoding="utf-8-sig"
)

predictions["date"] = pd.to_datetime(
    predictions["date"]
)

# 读取510300价格数据
price_path = (
    project_root
    / "data"
    / "processed"
    / "510300_clean.csv"
)

prices = pd.read_csv(
    price_path,
    encoding="utf-8-sig"
)

prices["date"] = pd.to_datetime(prices["date"])

# 合并预测结果和价格
df = predictions.merge(
    prices[["date", "close"]],
    on="date",
    how="inner"
)

df = df.sort_values("date").reset_index(drop=True)

# 计算ETF日收益率
df["asset_return"] = df["close"].pct_change()

# 预测概率超过0.5时产生持有信号
df["signal"] = (
    df["predicted_probability"] >= 0.5
).astype(int)

# 下一交易日才执行，避免未来函数
df["position"] = df["signal"].shift(1).fillna(0)

# 计算持仓变化
df["turnover"] = (
    df["position"].diff().abs().fillna(0)
)

# 计算交易前收益
df["strategy_return_before_cost"] = (
    df["position"] * df["asset_return"]
)

# 设置交易成本
transaction_cost = 0.001

# 扣除交易成本
df["strategy_return"] = (
    df["strategy_return_before_cost"]
    - df["turnover"] * transaction_cost
)

# 删除第一行空收益
df = df.dropna(
    subset=["asset_return"]
).reset_index(drop=True)

# 计算策略和基准净值
df["strategy_net_value"] = (
    1 + df["strategy_return"]
).cumprod()

df["benchmark_net_value"] = (
    1 + df["asset_return"]
).cumprod()

# 计算策略回撤
df["strategy_running_max"] = (
    df["strategy_net_value"].cummax()
)

df["strategy_drawdown"] = (
    df["strategy_net_value"]
    / df["strategy_running_max"]
    - 1
)

# 计算指标
returns = df["strategy_return"]
net_value = df["strategy_net_value"]

cumulative_return = net_value.iloc[-1] - 1

annual_return = (
    (1 + cumulative_return)
    ** (252 / len(returns))
    - 1
)

annual_volatility = returns.std() * np.sqrt(252)

maximum_drawdown = df["strategy_drawdown"].min()

sharpe_ratio = annual_return / annual_volatility

calmar_ratio = annual_return / abs(maximum_drawdown)

win_rate = (returns > 0).mean()

# 输出结果
print("逻辑回归预测策略")
print("-" * 40)
print(f"测试集累计收益率：{cumulative_return:.2%}")
print(f"测试集年化收益率：{annual_return:.2%}")
print(f"测试集年化波动率：{annual_volatility:.2%}")
print(f"测试集最大回撤：{maximum_drawdown:.2%}")
print(f"测试集夏普比率：{sharpe_ratio:.2f}")
print(f"测试集卡玛比率：{calmar_ratio:.2f}")
print(f"测试集胜率：{win_rate:.2%}")
print(f"累计换手次数：{df['turnover'].sum():.0f}")

# 保存结果
save_path = (
    project_root
    / "data"
    / "processed"
    / "logistic_strategy_backtest.csv"
)

df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n机器学习策略结果已保存到：{save_path}")