from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取ETF配置
config = pd.read_csv(
    project_root / "config" / "etf_config.csv",
    encoding="utf-8-sig"
)

processed_dir = project_root / "data" / "processed"

price_data = []

# 读取所有ETF收盘价
for _, row in config.iterrows():
    symbol = str(row["symbol"]).zfill(6)

    file_path = processed_dir / f"{symbol}_clean.csv"
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    df["date"] = pd.to_datetime(df["date"])

    price_data.append(
        df[["date", "close"]].rename(
            columns={"close": symbol}
        ).set_index("date")
    )

# 合并所有ETF价格
prices = pd.concat(price_data, axis=1).sort_index()

# 计算每日收益率
returns = prices.pct_change()

# 读取月度前2名信号
signal_path = (
    processed_dir / "monthly_top2_momentum_signal.csv"
)

signals = pd.read_csv(signal_path, encoding="utf-8-sig")
signals["month"] = signals["month"].astype(str)

# 创建每日策略收益
strategy_returns = []
previous_holdings = set()

for date in returns.index:

    current_month = str(date.to_period("M"))

    # 使用上个月生成的信号，避免未来函数
    previous_month = str(
        (date.to_period("M") - 1)
    )

    month_signal = signals[
        signals["month"] == previous_month
    ]

    holdings = set(
        month_signal["symbol"]
        .astype(str)
        .str.zfill(6)
    )

    # 如果没有可用信号，则当天策略收益为0
    if len(holdings) == 0:
        strategy_returns.append({
            "date": date,
            "strategy_return": 0,
            "turnover": 0,
            "holdings": ""
        })
        continue

    # 两只ETF等权配置
    selected_returns = returns.loc[
        date,
        list(holdings)
    ].dropna()

    daily_return = selected_returns.mean()

    # 计算是否发生调仓
    turnover = len(holdings.symmetric_difference(previous_holdings)) / 2

    strategy_returns.append({
        "date": date,
        "strategy_return": daily_return,
        "turnover": turnover,
        "holdings": ",".join(sorted(holdings))
    })

    previous_holdings = holdings

# 转换为DataFrame
result = pd.DataFrame(strategy_returns)

# 设置交易成本
transaction_cost = 0.001

# 扣除调仓成本
result["strategy_return_after_cost"] = (
    result["strategy_return"]
    - result["turnover"] * transaction_cost
)

# 删除无效收益
result = result.dropna(
    subset=["strategy_return_after_cost"]
).reset_index(drop=True)

# 计算策略净值
result["strategy_net_value"] = (
    1 + result["strategy_return_after_cost"]
).cumprod()

# 计算510300基准收益
benchmark_returns = returns["510300"].reindex(
    pd.to_datetime(result["date"])
).fillna(0)

result["benchmark_return"] = benchmark_returns.values

result["benchmark_net_value"] = (
    1 + result["benchmark_return"]
).cumprod()

# 保存结果
save_path = (
    processed_dir / "momentum_top2_backtest.csv"
)

result.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"动量策略回测结果已保存到：{save_path}")
print(f"累计换手次数：{result['turnover'].sum():.0f}")
print(
    f"累计交易成本："
    f"{result['turnover'].sum() * transaction_cost:.2%}"
)
print(f"策略最终净值：{result['strategy_net_value'].iloc[-1]:.4f}")
print(
    f"基准最终净值："
    f"{result['benchmark_net_value'].iloc[-1]:.4f}"
)