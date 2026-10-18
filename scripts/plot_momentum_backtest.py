from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取动量策略回测结果
file_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_top2_metrics.csv"
)

df = pd.read_csv(file_path, encoding="utf-8-sig")

# 转换日期
df["date"] = pd.to_datetime(df["date"])

# 计算基准回撤
df["benchmark_running_max"] = (
    df["benchmark_net_value"].cummax()
)

df["benchmark_drawdown"] = (
    df["benchmark_net_value"]
    / df["benchmark_running_max"]
    - 1
)

# 创建图片文件夹
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
    label="Momentum Top2"
)

axes[0].plot(
    df["date"],
    df["benchmark_net_value"],
    label="510300 Benchmark"
)

axes[0].set_title(
    "Momentum Top2 Strategy vs 510300 Benchmark"
)

axes[0].set_ylabel("Net Value")
axes[0].legend()
axes[0].grid(True)

# 绘制动量策略回撤
axes[1].plot(
    df["date"],
    df["drawdown"],
    label="Momentum Drawdown"
)

# 绘制基准回撤
axes[1].plot(
    df["date"],
    df["benchmark_drawdown"],
    label="Benchmark Drawdown"
)

axes[1].set_title("Drawdown Comparison")
axes[1].set_ylabel("Drawdown")
axes[1].set_xlabel("Date")
axes[1].legend()
axes[1].grid(True)

# 自动调整布局
plt.tight_layout()

# 保存图像
save_path = (
    figure_dir / "momentum_top2_backtest.png"
)

plt.savefig(save_path, dpi=150)

print(f"图表已保存到：{save_path}")

# 显示图表
plt.show()