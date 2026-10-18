# 导入AkShare，用于获取金融市场数据
import akshare as ak
from pathlib import Path

# 导入pandas，用于处理和保存表格数据
import pandas as pd

# 获取510300沪深300ETF的历史行情
# 新浪接口需要带交易所前缀：sh表示上海
df = ak.fund_etf_hist_sina(
    symbol="sh510300"
)

# 查看前5行数据
print("前5行数据：")
print(df.head())

# 查看数据列名
print("\n数据列名：")
print(df.columns.tolist())

# 查看数据行列数量
print("\n数据形状：")
print(df.shape)

# 保存原始数据
# 获取当前Python文件所在位置
project_root = Path(__file__).resolve().parents[2]

# 创建项目根目录下的data/raw文件夹
raw_data_dir = project_root / "data" / "raw"
raw_data_dir.mkdir(parents=True, exist_ok=True)

# 设置保存路径
save_path = raw_data_dir / "510300_raw.csv"

# 保存数据
df.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n数据已经保存到：{save_path}")

print("\n数据已经保存到：data/raw/510300_raw.csv")
