# 导入时间模块，用于控制请求间隔
import time

# 导入Path，用于处理文件路径
from pathlib import Path

# 导入pandas，用于读取配置文件和处理数据
import pandas as pd

# 导入AkShare，用于获取ETF历史行情
import akshare as ak


# 从当前文件所在位置开始，逐级向上查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent

print(f"项目根目录：{project_root}")

# 设置配置文件路径
config_path = project_root / "config" / "etf_config.csv"

# 设置原始数据保存文件夹
raw_data_dir = project_root / "data" / "raw"

# 如果文件夹不存在，就自动创建
raw_data_dir.mkdir(parents=True, exist_ok=True)

# 读取ETF配置文件
etf_config = pd.read_csv(config_path, encoding="utf-8-sig")

# 逐只下载ETF
for _, row in etf_config.iterrows():

    # 将代码转换为字符串，并补齐6位
    symbol = str(row["symbol"]).zfill(6)

    # 目前8只ETF均为上海市场，使用sh前缀
    sina_symbol = "sh" + symbol

    print(f"正在下载：{symbol} {row['name']}")

    try:
        # 获取ETF历史行情
        df = ak.fund_etf_hist_sina(
            symbol=sina_symbol
        )

        # 设置保存路径
        save_path = raw_data_dir / f"{symbol}_raw.csv"

        # 保存原始数据
        df.to_csv(
            save_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"下载成功，共{len(df)}行，保存到：{save_path}")

    except Exception as error:
        # 如果某只ETF失败，记录错误并继续下载其他ETF
        print(f"下载失败：{symbol}")
        print(f"错误信息：{error}")

    # 每次请求间隔2秒，降低接口压力
    time.sleep(2)

print("全部下载任务结束。")
