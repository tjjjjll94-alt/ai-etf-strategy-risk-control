# 简历项目描述

## 中文版

### AI辅助ETF策略与风险控制系统

- 使用AkShare获取8只中国市场ETF日线行情，完成数据清洗、字段统一和可复现数据集构建；
- 构建MA20、MA60趋势策略和60日动量Top2 ETF轮动策略，加入手续费与滑点假设；
- 使用累计收益率、年化收益率、年化波动率、最大回撤、夏普比率、卡玛比率、胜率和换手次数评价策略；
- 设计20日波动率过滤模块，研究收益、交易成本与回撤之间的权衡；
- 按时间顺序划分训练集、验证集和测试集，使用逻辑回归预测510300未来5个交易日上涨概率；
- 使用Streamlit和Plotly搭建交互式策略回测与风险分析看板。

## English Version

### AI-Assisted ETF Strategy and Risk Control System

- Collected and cleaned daily historical data for eight China-market ETFs using AkShare;
- Implemented interpretable MA20, MA60, and 60-day Top-2 momentum rotation strategies with transaction-cost assumptions;
- Evaluated strategies using cumulative return, annualized return, volatility, maximum drawdown, Sharpe ratio, Calmar ratio, win rate, and turnover;
- Designed a 20-day volatility filter to study the trade-off between return, drawdown, and trading costs;
- Applied chronological train-validation-test splits and trained a logistic regression model to estimate the probability of a positive five-day forward return for the CSI 300 ETF;
- Built an interactive Streamlit and Plotly dashboard for strategy comparison, risk analysis, and monthly ETF rotation signals.

## 一句话版本

构建了一个从AkShare数据获取、策略回测、风险控制、机器学习预测到Streamlit可视化展示的完整ETF量化研究系统。
