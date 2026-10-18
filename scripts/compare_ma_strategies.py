from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


def calculate_metrics(file_path):
    # 读取回测结果
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 获取策略收益率和净值
    returns = df["strategy_return"].dropna()
    net_value = df["strategy_net_value"].dropna()

    # 计算累计收益率
    cumulative_return = net_value.iloc[-1] - 1

    # 计算年化收益率
    annual_return = (
        (1 + cumulative_return) ** (252 / len(returns)) - 1
    )

    # 计算年化波动率
    annual_volatility = returns.std() * np.sqrt(252)

    # 计算最大回撤
    running_max = net_value.cummax()
    drawdown = net_value / running_max - 1
    maximum_drawdown = drawdown.min()

    # 计算夏普比率
    sharpe_ratio = annual_return / annual_volatility

    # 计算卡玛比率
    calmar_ratio = annual_return / abs(maximum_drawdown)

    # 计算胜率
    win_rate = (returns > 0).mean()

    # 计算换手次数和交易成本
    turnover_count = df["turnover"].sum()
    transaction_cost = turnover_count * 0.001

    return {
        "累计收益率": cumulative_return,
        "年化收益率": annual_return,
        "年化波动率": annual_volatility,
        "最大回撤": maximum_drawdown,
        "夏普比率": sharpe_ratio,
        "卡玛比率": calmar_ratio,
        "胜率": win_rate,
        "换手次数": turnover_count,
        "交易成本": transaction_cost,
    }


# 比较20日和60日均线策略
files = {
    "MA20": project_root / "data" / "processed" / "510300_ma20_backtest.csv",
    "MA60": project_root / "data" / "processed" / "510300_ma60_backtest.csv",
}

results = []

for strategy_name, file_path in files.items():
    metrics = calculate_metrics(file_path)
    metrics["策略"] = strategy_name
    results.append(metrics)

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
        "换手次数",
        "交易成本",
    ]
]

# 输出结果
print(comparison.to_string(index=False))

# 保存比较结果
save_path = (
    project_root / "data" / "processed" / "ma_strategy_comparison.csv"
)

comparison.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n比较结果已保存到：{save_path}")