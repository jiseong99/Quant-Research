import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import label_binarize
import shap
import warnings
import os

warnings.filterwarnings("ignore")


class MLModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.is_trained = False
        self.n_classes = 3

    def _build_model(self):
        is_prod = os.environ.get("RENDER", False)
        return XGBClassifier(
            n_estimators=100 if is_prod else 300,
            max_depth=3 if is_prod else 4,
            learning_rate=0.1 if is_prod else 0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            num_class=3,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=1,
        )

    def train(self, df: pd.DataFrame, feature_cols: list) -> dict:
        self.feature_cols = feature_cols
        n = len(df)
        fold_size = n // 4
        aucs = []

        # Walk-forward validation
        for i in range(1, 4):
            train_end  = fold_size * (i + 1)
            test_start = train_end
            test_end   = min(test_start + fold_size, n)

            train_df = df.iloc[:train_end]
            test_df  = df.iloc[test_start:test_end]
            if len(test_df) < 10:
                continue

            X_tr = self.scaler.fit_transform(train_df[feature_cols].values)
            X_te = self.scaler.transform(test_df[feature_cols].values)
            y_tr = train_df["target"].values
            y_te = test_df["target"].values

            model = self._build_model()
            model.fit(X_tr, y_tr, verbose=False)
            y_prob = model.predict_proba(X_te)

            # 3-class AUC (OvR)
            try:
                y_bin = label_binarize(y_te, classes=[0, 1, 2])
                auc = roc_auc_score(y_bin, y_prob, multi_class="ovr", average="macro")
                aucs.append(auc)
            except Exception:
                pass

        # 최종 모델: 전체 80% train
        split_idx = int(n * 0.8)
        train_df = df.iloc[:split_idx]
        test_df  = df.iloc[split_idx:]

        X_train = self.scaler.fit_transform(train_df[feature_cols].values)
        X_test  = self.scaler.transform(test_df[feature_cols].values)
        y_train = train_df["target"].values
        y_test  = test_df["target"].values

        self.model = self._build_model()
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        try:
            y_bin    = label_binarize(y_test, classes=[0, 1, 2])
            final_auc = roc_auc_score(
                y_bin, y_prob, multi_class="ovr", average="macro"
            )
        except Exception:
            final_auc = 0.0

        avg_wf_auc = float(np.mean(aucs)) if aucs else final_auc

        importance = dict(zip(
            feature_cols,
            self.model.feature_importances_.tolist()
        ))
        importance_sorted = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )

        return {
            "train_size": len(train_df),
            "test_size": len(test_df),
            "accuracy": round(accuracy, 4),
            "auc_roc": round(final_auc, 4),
            "walkforward_auc": round(avg_wf_auc, 4),
            "feature_importance": importance_sorted,
        }

    def predict(self, df: pd.DataFrame) -> dict:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")

        X = df[self.feature_cols].tail(1).values
        X_scaled = self.scaler.transform(X)

        pred_class = int(self.model.predict(X_scaled)[0])
        pred_prob  = self.model.predict_proba(X_scaled)[0].tolist()

        label_map = {0: "Down", 1: "Neutral", 2: "Up"}

# SHAP
        try:
            explainer   = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_scaled)

            # 3-class SHAP 형태 처리
            if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                # shape: (1, n_features, n_classes)
                sv = shap_values[0, :, pred_class]
            elif isinstance(shap_values, list):
                sv = np.array(shap_values[pred_class]).flatten()
            else:
                sv = np.array(shap_values).flatten()

            shap_dict = dict(zip(
                self.feature_cols,
                [round(float(v), 4) for v in sv]
            ))
        except Exception:
            shap_dict = {col: 0.0 for col in self.feature_cols}
            
        shap_sorted = dict(
            sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
        )

        return {
            "prediction": label_map[pred_class],
            "prob_down":    round(pred_prob[0], 4),
            "prob_neutral": round(pred_prob[1], 4),
            "prob_up":      round(pred_prob[2], 4),
            "shap_values":  dict(list(shap_sorted.items())[:10]),
        }

    def predict_all(self, df: pd.DataFrame) -> np.ndarray:
        X = self.scaler.transform(df[self.feature_cols].values)
        # 상승(2) 확률 반환
        return self.model.predict_proba(X)[:, 2]

    def train_and_predict(self, df: pd.DataFrame,
                          feature_cols: list) -> dict:
        train_result   = self.train(df, feature_cols)
        predict_result = self.predict(df)
        return {**train_result, **predict_result}