from pathlib import Path
import pandas as pd


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取60日动量数据
input_path = (
    project_root / "data" / "processed" / "etf_momentum_60.csv"
)

df = pd.read_csv(input_path, encoding="utf-8-sig")

# 转换日期
df["date"] = pd.to_datetime(df["date"])

# 创建月份字段
df["month"] = df["date"].dt.to_period("M")

# 每只ETF每个月只保留最后一个可用交易日
monthly_data = (
    df.sort_values("date")
      .groupby(["month", "symbol"], as_index=False)
      .tail(1)
)

# 在每个月内按照动量从高到低排名
monthly_data["rank"] = (
    monthly_data
    .groupby("month")["momentum_60"]
    .rank(method="first", ascending=False)
)

# 每个月选择动量排名前2的ETF
top2_signal = monthly_data[
    monthly_data["rank"] <= 2
].copy()

# 按月份和排名排序
top2_signal = top2_signal.sort_values(
    ["month", "rank"]
)

# 保存调仓信号
save_path = (
    project_root
    / "data"
    / "processed"
    / "monthly_top2_momentum_signal.csv"
)

top2_signal.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"月度动量信号已保存到：{save_path}")

print("\n最近三个月的调仓信号：")

recent_months = (
    top2_signal["month"]
    .drop_duplicates()
    .sort_values()
    .tail(3)
)

print(
    top2_signal[
        top2_signal["month"].isin(recent_months)
    ][
        ["month", "rank", "symbol", "name", "momentum_60"]
    ].to_string(index=False)
)

