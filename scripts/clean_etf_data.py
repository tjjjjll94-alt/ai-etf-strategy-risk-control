from pathlib import Path
import pandas as pd


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent

# 设置输入和输出文件夹
raw_dir = project_root / "data" / "raw"
processed_dir = project_root / "data" / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

# 找到所有原始ETF文件
raw_files = raw_dir.glob("*_raw.csv")

for raw_file in raw_files:
    # 读取原始数据
    df = pd.read_csv(raw_file, encoding="utf-8-sig")

    # 将日期转换为日期类型
    df["date"] = pd.to_datetime(df["date"])

    # 按日期从早到晚排序
    df = df.sort_values("date").reset_index(drop=True)

    # 只保留后续研究需要的字段
    df = df[[
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount"
    ]]

    # 删除收盘价缺失的行
    df = df.dropna(subset=["close"])

    # 获取ETF代码
    symbol = raw_file.name.replace("_raw.csv", "")

    # 保存清洗后的数据
    save_path = processed_dir / f"{symbol}_clean.csv"
    df.to_csv(save_path, index=False, encoding="utf-8-sig")

    print(f"{symbol} 清洗完成，共{len(df)}行")

print("全部数据清洗完成。")