from pathlib import Path
import pandas as pd


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取动量策略结果
input_path = (
    project_root
    / "data"
    / "processed"
    / "momentum_vol_filter_backtest.csv"
)

df = pd.read_csv(input_path, encoding="utf-8-sig")

# 转换日期并排序
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# 计算时间切分位置
n = len(df)

train_end = int(n * 0.60)
validation_end = int(n * 0.80)

# 按时间顺序切分
train = df.iloc[:train_end].copy()
validation = df.iloc[train_end:validation_end].copy()
test = df.iloc[validation_end:].copy()

# 创建输出文件夹
split_dir = project_root / "data" / "processed" / "splits"
split_dir.mkdir(parents=True, exist_ok=True)

# 保存三个数据集
train.to_csv(
    split_dir / "train.csv",
    index=False,
    encoding="utf-8-sig"
)

validation.to_csv(
    split_dir / "validation.csv",
    index=False,
    encoding="utf-8-sig"
)

test.to_csv(
    split_dir / "test.csv",
    index=False,
    encoding="utf-8-sig"
)

# 输出切分结果
print("时间序列数据切分完成")
print("-" * 40)
print(
    f"训练集：{train['date'].min().date()} "
    f"至 {train['date'].max().date()}，"
    f"共{len(train)}行"
)
print(
    f"验证集：{validation['date'].min().date()} "
    f"至 {validation['date'].max().date()}，"
    f"共{len(validation)}行"
)
print(
    f"测试集：{test['date'].min().date()} "
    f"至 {test['date'].max().date()}，"
    f"共{len(test)}行"
)