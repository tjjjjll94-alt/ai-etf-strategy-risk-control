from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="AI辅助ETF策略与风险控制系统",
    page_icon=":material/monitoring:",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_csv(filename):
    """读取项目中的CSV数据，并缓存结果。"""
    return pd.read_csv(PROCESSED_DIR / filename, encoding="utf-8-sig")


st.title("AI辅助ETF策略与风险控制系统")
st.caption("基于历史行情的模拟研究看板，不构成投资建议，不使用真实资金。")

comparison = load_csv("all_strategy_comparison.csv")
momentum = load_csv("momentum_top2_metrics.csv")
volatility = load_csv("momentum_vol_filter_backtest.csv")
signals = load_csv("monthly_top2_momentum_signal.csv")

momentum["date"] = pd.to_datetime(momentum["date"])
volatility["date"] = pd.to_datetime(volatility["date"])

with st.sidebar:
    st.header("研究设置")
    selected_strategy = st.selectbox(
        "选择展示策略",
        ["60日动量Top2", "动量+波动率过滤"],
    )
    st.info(
        "历史回测结果会受到样本区间、交易成本和参数设定影响。",
        title="研究提示",
    )

if selected_strategy == "60日动量Top2":
    selected_data = momentum
    net_value_column = "strategy_net_value"
    drawdown_column = "drawdown"
else:
    selected_data = volatility
    net_value_column = "filtered_net_value"
    drawdown_column = "filtered_drawdown"

selected_metrics = comparison[comparison["策略"] == selected_strategy]

st.subheader(f"{selected_strategy}：核心指标")
if not selected_metrics.empty:
    row = selected_metrics.iloc[0]
    with st.container(horizontal=True):
        st.metric("累计收益率", f"{row['累计收益率']:.2%}", border=True)
        st.metric("年化收益率", f"{row['年化收益率']:.2%}", border=True)
        st.metric("年化波动率", f"{row['年化波动率']:.2%}", border=True)
        st.metric("最大回撤", f"{row['最大回撤']:.2%}", border=True)
        st.metric("夏普比率", f"{row['夏普比率']:.2f}", border=True)

st.subheader("净值曲线")
curve_data = selected_data[["date", net_value_column, "benchmark_net_value"]].copy()
curve_data = curve_data.rename(
    columns={
        net_value_column: selected_strategy,
        "benchmark_net_value": "510300基准",
    }
)
curve_long = curve_data.melt(
    id_vars="date", var_name="策略", value_name="净值"
)
figure = px.line(
    curve_long,
    x="date",
    y="净值",
    color="策略",
    title=f"{selected_strategy}与510300基准净值对比",
)
figure.update_layout(legend_title_text="")
st.plotly_chart(figure, width="stretch", config={"displaylogo": False})

st.subheader("回撤曲线")
drawdown_data = selected_data[["date", drawdown_column]].copy()
drawdown_data = drawdown_data.rename(columns={drawdown_column: selected_strategy})
benchmark_running_max = selected_data["benchmark_net_value"].cummax()
drawdown_data["510300基准"] = (
    selected_data["benchmark_net_value"] / benchmark_running_max - 1
)
drawdown_long = drawdown_data.melt(
    id_vars="date", var_name="策略", value_name="回撤"
)
drawdown_figure = px.area(
    drawdown_long,
    x="date",
    y="回撤",
    color="策略",
    title="历史回撤对比",
)
drawdown_figure.update_layout(legend_title_text="")
st.plotly_chart(
    drawdown_figure,
    width="stretch",
    config={"displaylogo": False},
)

with st.container(border=True):
    st.subheader("策略表现比较")
    display_columns = [
        "策略",
        "累计收益率",
        "年化收益率",
        "年化波动率",
        "最大回撤",
        "夏普比率",
        "卡玛比率",
        "胜率",
    ]
    st.dataframe(
        comparison[display_columns],
        hide_index=True,
        column_config={
            "累计收益率": st.column_config.NumberColumn(format="%.2f%%"),
            "年化收益率": st.column_config.NumberColumn(format="%.2f%%"),
            "年化波动率": st.column_config.NumberColumn(format="%.2f%%"),
            "最大回撤": st.column_config.NumberColumn(format="%.2f%%"),
            "夏普比率": st.column_config.NumberColumn(format="%.2f"),
            "卡玛比率": st.column_config.NumberColumn(format="%.2f"),
            "胜率": st.column_config.NumberColumn(format="%.2f%%"),
        },
        alt="不同ETF策略的历史绩效比较",
    )

latest_month = signals["month"].max()
with st.container(border=True):
    st.subheader(f"{latest_month}月度动量调仓信号")
    st.dataframe(
        signals[signals["month"] == latest_month][
            ["month", "rank", "symbol", "name", "momentum_60"]
        ],
        hide_index=True,
        column_config={
            "momentum_60": st.column_config.NumberColumn(
                "60日动量", format="%.2f%%"
            )
        },
        alt="最新月份的ETF动量排名和调仓信号",
    )

st.caption("数据来源：AkShare历史行情接口；交易成本和滑点为研究假设。")
