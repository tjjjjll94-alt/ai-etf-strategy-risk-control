from pathlib import Path
import pandas as pd
import numpy as np


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取510300清洗后的数据
file_path = (
    project_root
    / "data"
    / "processed"
    / "510300_clean.csv"
)

df = pd.read_csv(file_path, encoding="utf-8-sig")

# 转换日期并排序
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# 计算历史特征
df["momentum_5"] = df["close"].pct_change(5)
df["momentum_20"] = df["close"].pct_change(20)

# 计算20日均线距离
ma20 = df["close"].rolling(20).mean()
df["ma20_distance"] = df["close"] / ma20 - 1

# 计算20日历史波动率
daily_return = df["close"].pct_change()
df["volatility_20"] = (
    daily_return.rolling(20).std() * np.sqrt(252)
)

# 构造预测标签
# 使用未来5个交易日收益率判断下一期是否上涨
future_return_5d = df["close"].shift(-5) / df["close"] - 1

df["target"] = (future_return_5d > 0).astype(int)

# 删除特征或标签不完整的行
df = df.dropna(
    subset=[
        "momentum_5",
        "momentum_20",
        "ma20_distance",
        "volatility_20"
    ]
)

# 保留机器学习需要的字段
feature_columns = [
    "date",
    "momentum_5",
    "momentum_20",
    "ma20_distance",
    "volatility_20",
    "target"
]

ml_df = df[feature_columns].copy()

# 保存机器学习特征
save_path = (
    project_root
    / "data"
    / "processed"
    / "ml_features_510300.csv"
)

ml_df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"机器学习特征已保存到：{save_path}")
print(f"数据行数：{len(ml_df)}")
print(f"上涨标签比例：{ml_df['target'].mean():.2%}")