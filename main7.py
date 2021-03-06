import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

class UserPredictor:
    def __init__(self):
        self.estimator = LogisticRegression(fit_intercept=False)
        self.model = Pipeline([("std", StandardScaler()),
                               ("logr", self.estimator)
                              ])
        
    def fit(self, train_users, train_logs, train_y):
        result = train_users.merge(train_y, on='id', how='outer')
        
        time_on_page = train_logs.groupby("id")["minutes_on_page"].aggregate(["sum", "count"]).reset_index()
        url_dummies = pd.get_dummies(train_logs[["id", "url_visited"]], columns=["url_visited"])
        url_dummies = url_dummies.groupby("id").sum()
        result2 = result.merge(time_on_page, on="id").merge(url_dummies, on="id")
        
        X = pd.get_dummies(result2.drop(columns = ["id", "name", "y"]), columns=["badge"])
        self.features_ = X.columns 
        y = result2['y']
        
        self.model.fit(X,y)
    
    def predict(self, train_users, train_logs):
        time_on_page = train_logs.groupby("id")["minutes_on_page"].aggregate(["sum", "count"]).reset_index()
        url_dummies = pd.get_dummies(train_logs[["id", "url_visited"]], columns=["url_visited"])
        url_dummies = url_dummies.groupby("id").sum()
        
        result2 = train_users.merge(url_dummies, on="id", how="left").merge(time_on_page, on="id", how="left")
        
        X = pd.get_dummies(result2.drop(columns = ["id", "name"]), columns=["badge"])
        X = X[self.features_].fillna(0)
        
        return self.model.predict(X)