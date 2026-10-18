from pathlib import Path
import pandas as pd


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取ETF配置
config_path = project_root / "config" / "etf_config.csv"
etf_config = pd.read_csv(config_path, encoding="utf-8-sig")

# 设置数据文件夹
processed_dir = project_root / "data" / "processed"

# 保存所有ETF的动量结果
momentum_results = []

for _, row in etf_config.iterrows():

    # 获取ETF代码
    symbol = str(row["symbol"]).zfill(6)

    # 读取清洗后的数据
    data_path = processed_dir / f"{symbol}_clean.csv"
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # 转换日期并排序
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 计算60日动量
    # 当前收盘价相对于60个交易日前收盘价的涨跌幅
    df["momentum_60"] = df["close"].pct_change(60)

    # 只保留有足够历史数据的记录
    df = df.dropna(subset=["momentum_60"])

    # 保留必要字段
    df["symbol"] = symbol
    df["name"] = row["name"]

    momentum_results.append(
        df[["date", "symbol", "name", "close", "momentum_60"]]
    )

# 合并所有ETF
momentum_df = pd.concat(momentum_results, ignore_index=True)

# 按日期和动量从高到低排序
momentum_df = momentum_df.sort_values(
    ["date", "momentum_60"],
    ascending=[True, False]
)

# 保存结果
save_path = processed_dir / "etf_momentum_60.csv"

momentum_df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"动量数据已保存到：{save_path}")
print(f"总记录数：{len(momentum_df)}")
print("\n最近一个交易日的动量排名：")

latest_date = momentum_df["date"].max()

print(
    momentum_df[
        momentum_df["date"] == latest_date
    ][
        ["symbol", "name", "momentum_60"]
    ].to_string(index=False)
)