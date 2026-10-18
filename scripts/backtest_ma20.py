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

# 转换日期并排序
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# 计算ETF日收益率
df["asset_return"] = df["close"].pct_change()

# 计算60日移动平均线
df["ma60"] = df["close"].rolling(window=60).mean()

# 根据当天收盘价生成信号
# 收盘价高于60日均线时产生持有信号
df["signal"] = (df["close"] > df["ma60"]).astype(int)

# 信号下一天才执行，避免未来函数
df["position"] = df["signal"].shift(1)

# 第一行没有前一天信号，设为0
df["position"] = df["position"].fillna(0)

# 计算持仓变化
# position从0变1或从1变0时，turnover为1
df["turnover"] = df["position"].diff().abs().fillna(0)

# 设置交易成本假设
# 手续费和滑点合计按单次换仓的0.10%计算
transaction_cost = 0.001

# 计算策略每日收益
df["strategy_return_before_cost"] = (
    df["position"] * df["asset_return"]
)

df["strategy_return"] = (
    df["strategy_return_before_cost"]
    - df["turnover"] * transaction_cost
)

# 删除收益率为空的第一行
df = df.dropna(subset=["asset_return"]).reset_index(drop=True)

# 计算策略和基准的净值
df["strategy_net_value"] = (
    1 + df["strategy_return"]
).cumprod()

df["benchmark_net_value"] = (
    1 + df["asset_return"]
).cumprod()


def calculate_metrics(return_series, net_value_series):
    """
    根据每日收益率和净值计算主要绩效指标。
    """
    return_series = return_series.dropna()

    trading_days = len(return_series)

    cumulative_return = net_value_series.iloc[-1] - 1

    annual_return = (
        (1 + cumulative_return) ** (252 / trading_days) - 1
    )

    annual_volatility = return_series.std() * np.sqrt(252)

    running_max = net_value_series.cummax()

    drawdown = net_value_series / running_max - 1

    maximum_drawdown = drawdown.min()

    if annual_volatility != 0:
        sharpe_ratio = annual_return / annual_volatility
    else:
        sharpe_ratio = np.nan

    if maximum_drawdown != 0:
        calmar_ratio = annual_return / abs(maximum_drawdown)
    else:
        calmar_ratio = np.nan

    win_rate = (return_series > 0).mean()

    return {
        "累计收益率": cumulative_return,
        "年化收益率": annual_return,
        "年化波动率": annual_volatility,
        "最大回撤": maximum_drawdown,
        "夏普比率": sharpe_ratio,
        "卡玛比率": calmar_ratio,
        "胜率": win_rate,
    }


# 计算策略指标
strategy_metrics = calculate_metrics(
    df["strategy_return"],
    df["strategy_net_value"]
)

# 计算基准指标
benchmark_metrics = calculate_metrics(
    df["asset_return"],
    df["benchmark_net_value"]
)

# 输出策略结果
print("60日均线策略结果")
print("-" * 40)

for metric_name, metric_value in strategy_metrics.items():
    if metric_name in ["夏普比率", "卡玛比率"]:
        print(f"{metric_name}：{metric_value:.2f}")
    else:
        print(f"{metric_name}：{metric_value:.2%}")

# 输出基准结果
print("\n买入并持有基准结果")
print("-" * 40)

for metric_name, metric_value in benchmark_metrics.items():
    if metric_name in ["夏普比率", "卡玛比率"]:
        print(f"{metric_name}：{metric_value:.2f}")
    else:
        print(f"{metric_name}：{metric_value:.2%}")

# 输出换手信息
print("\n交易信息")
print("-" * 40)
print(f"累计换手次数：{df['turnover'].sum():.0f}")
print(f"总交易成本：{df['turnover'].sum() * transaction_cost:.2%}")

# 保存回测结果
result_path = (
    project_root / "data" / "processed" / "510300_ma60_backtest.csv"
)
df.to_csv(
    result_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n回测结果已保存到：{result_path}")