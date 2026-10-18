from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取回测结果
data_path = (
    project_root / "data" / "processed" / "510300_ma20_backtest.csv"
)

df = pd.read_csv(data_path, encoding="utf-8-sig")

# 转换日期
df["date"] = pd.to_datetime(df["date"])

# 计算策略回撤
df["strategy_running_max"] = (
    df["strategy_net_value"].cummax()
)

df["strategy_drawdown"] = (
    df["strategy_net_value"]
    / df["strategy_running_max"]
    - 1
)

# 创建图片保存文件夹
figure_dir = project_root / "reports" / "figures"
figure_dir.mkdir(parents=True, exist_ok=True)

# 创建上下两个图
fig, axes = plt.subplots(
    2,
    1,
    figsize=(12, 8),
    sharex=True
)

# 绘制净值曲线
axes[0].plot(
    df["date"],
    df["strategy_net_value"],
    label="MA20 Strategy"
)

axes[0].plot(
    df["date"],
    df["benchmark_net_value"],
    label="Buy and Hold"
)

axes[0].set_title("510300 Strategy vs Benchmark")
axes[0].set_ylabel("Net Value")
axes[0].legend()
axes[0].grid(True)

# 绘制策略回撤
axes[1].fill_between(
    df["date"],
    df["strategy_drawdown"],
    0,
    alpha=0.3
)

axes[1].set_title("MA20 Strategy Drawdown")
axes[1].set_ylabel("Drawdown")
axes[1].set_xlabel("Date")
axes[1].grid(True)

# 自动调整布局
plt.tight_layout()

# 保存图片
save_path = figure_dir / "510300_ma20_backtest.png"
plt.savefig(save_path, dpi=150)

print(f"图表已保存到：{save_path}")

# 显示图表
plt.show()