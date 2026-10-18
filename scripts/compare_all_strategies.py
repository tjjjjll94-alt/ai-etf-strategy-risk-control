from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent

processed_dir = project_root / "data" / "processed"


def calculate_metrics(returns, net_value):
    # 删除空值
    returns = returns.dropna()
    net_value = net_value.dropna()

    # 累计收益率
    cumulative_return = net_value.iloc[-1] - 1

    # 年化收益率
    annual_return = (
        (1 + cumulative_return) ** (252 / len(returns)) - 1
    )

    # 年化波动率
    annual_volatility = returns.std() * np.sqrt(252)

    # 最大回撤
    running_max = net_value.cummax()
    drawdown = net_value / running_max - 1
    maximum_drawdown = drawdown.min()

    # 夏普比率
    sharpe_ratio = annual_return / annual_volatility

    # 卡玛比率
    calmar_ratio = annual_return / abs(maximum_drawdown)

    # 胜率
    win_rate = (returns > 0).mean()

    return {
        "累计收益率": cumulative_return,
        "年化收益率": annual_return,
        "年化波动率": annual_volatility,
        "最大回撤": maximum_drawdown,
        "夏普比率": sharpe_ratio,
        "卡玛比率": calmar_ratio,
        "胜率": win_rate,
    }


results = []


# 1. 读取动量结果文件，获得基准
momentum_df = pd.read_csv(
    processed_dir / "momentum_top2_metrics.csv",
    encoding="utf-8-sig"
)

benchmark_metrics = calculate_metrics(
    momentum_df["benchmark_return"],
    momentum_df["benchmark_net_value"]
)

benchmark_metrics["策略"] = "510300基准"
results.append(benchmark_metrics)


# 2. 读取MA20和MA60结果
for strategy_name, file_name in [
    ("MA20均线", "510300_ma20_backtest.csv"),
    ("MA60均线", "510300_ma60_backtest.csv"),
]:
    df = pd.read_csv(
        processed_dir / file_name,
        encoding="utf-8-sig"
    )

    metrics = calculate_metrics(
        df["strategy_return"],
        df["strategy_net_value"]
    )

    metrics["策略"] = strategy_name
    results.append(metrics)


# 3. 读取原始动量策略
momentum_metrics = calculate_metrics(
    momentum_df["strategy_return_after_cost"],
    momentum_df["strategy_net_value"]
)

momentum_metrics["策略"] = "60日动量Top2"
results.append(momentum_metrics)


# 4. 读取波动率过滤策略
vol_df = pd.read_csv(
    processed_dir / "momentum_vol_filter_backtest.csv",
    encoding="utf-8-sig"
)

vol_metrics = calculate_metrics(
    vol_df["filtered_return"],
    vol_df["filtered_net_value"]
)

vol_metrics["策略"] = "动量+波动率过滤"
results.append(vol_metrics)


# 转换为表格
comparison = pd.DataFrame(results)

# 调整列顺序
comparison = comparison[
    [
        "策略",
        "累计收益率",
        "年化收益率",
        "年化波动率",
        "最大回撤",
        "夏普比率",
        "卡玛比率",
        "胜率",
    ]
]

# 输出结果
print(comparison.to_string(index=False))

# 保存结果
save_path = (
    processed_dir / "all_strategy_comparison.csv"
)

comparison.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n比较表已保存到：{save_path}")