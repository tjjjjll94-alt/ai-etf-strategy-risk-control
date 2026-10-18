from pathlib import Path
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score


# 自动查找项目根目录
project_root = Path(__file__).resolve()

while not (project_root / "config" / "etf_config.csv").exists():
    project_root = project_root.parent


# 读取机器学习特征
file_path = (
    project_root
    / "data"
    / "processed"
    / "ml_features_510300.csv"
)

df = pd.read_csv(file_path, encoding="utf-8-sig")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# 特征列
feature_columns = [
    "momentum_5",
    "momentum_20",
    "ma20_distance",
    "volatility_20"
]

# 按日期划分数据
train = df[df["date"] <= "2021-01-05"].copy()

validation = df[
    (df["date"] >= "2021-01-06")
    & (df["date"] <= "2023-11-23")
].copy()

test = df[df["date"] >= "2023-11-24"].copy()

# 准备特征和标签
X_train = train[feature_columns]
y_train = train["target"]

X_validation = validation[feature_columns]
y_validation = validation["target"]

X_test = test[feature_columns]
y_test = test["target"]

# 建立模型流水线
# 标准化和模型训练只使用训练集
model = Pipeline([
    ("scaler", StandardScaler()),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    )
])

# 训练模型
model.fit(X_train, y_train)

# 预测验证集概率
validation_probability = model.predict_proba(
    X_validation
)[:, 1]

# 使用0.5作为初始分类阈值
validation_prediction = (
    validation_probability >= 0.5
).astype(int)

# 评估验证集
validation_accuracy = accuracy_score(
    y_validation,
    validation_prediction
)

validation_auc = roc_auc_score(
    y_validation,
    validation_probability
)

# 预测测试集
test_probability = model.predict_proba(
    X_test
)[:, 1]

test_prediction = (
    test_probability >= 0.5
).astype(int)

# 评估测试集
test_accuracy = accuracy_score(
    y_test,
    test_prediction
)

test_auc = roc_auc_score(
    y_test,
    test_probability
)

# 输出结果
print("逻辑回归模型结果")
print("-" * 40)
print(f"训练集样本数：{len(train)}")
print(f"验证集样本数：{len(validation)}")
print(f"测试集样本数：{len(test)}")
print(f"验证集准确率：{validation_accuracy:.2%}")
print(f"验证集AUC：{validation_auc:.3f}")
print(f"测试集准确率：{test_accuracy:.2%}")
print(f"测试集AUC：{test_auc:.3f}")

# 保存测试集预测结果
test["predicted_probability"] = test_probability
test["predicted_label"] = test_prediction

save_path = (
    project_root
    / "data"
    / "processed"
    / "logistic_test_predictions.csv"
)

test.to_csv(
    save_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n测试集预测结果已保存到：{save_path}")