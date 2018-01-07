# coding: utf-8
"""Simple lightGBM model

1. Split train data into offline train set and test set
2. Use all train data to train a new lightGBM model
3. Predict the value of test data
"""

import sys

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

sys.path.append('../')
from util.feature import add_feature

train = pd.read_csv('../data/d_train_20180102.csv')
train = add_feature(train)

# splits into male and female
train_m = train.loc[train['性别'] == 0, :]
train_f = train.loc[train['性别'] == 1, :]
log = tuple()
scaler = StandardScaler()

for sets in [train_m, train_f]:
    XALL = sets.loc[:, [column for column in train.columns if column not in 
                    ['id', '性别', '体检日期', '血糖', '乙肝表面抗原', '乙肝表面抗体', '乙肝e抗原', '乙肝e抗体', '乙肝核心抗体']]]
    
    XALL.fillna(XALL.median(), inplace=True)
    columns = XALL.columns

    scaler.fit(XALL)
    XALL = scaler.transform(XALL)
    XALL = pd.DataFrame(XALL, columns=columns)

    yALL = sets.loc[:, '血糖']

    X_train, X_test, y_train, y_test = train_test_split(XALL, yALL,
                                                        test_size=0.3, random_state=2018)

    train_set = lgb.Dataset(X_train, label=y_train)
    test_set = lgb.Dataset(X_test, label=y_test, reference=train_set)

    params = {
        'objective': 'regression',
        'boosting': 'gbdt',
        'learning_rate': 0.01,
        'num_leaves': 15,
        # 'max_depth': 5,
        'num_threads': 2,
        'lambda_l1': 0.01,
        'lambda_l2': 0.01,
        'metric': 'mse',
        'verbose': 1,
        'feature_fraction': 1.0,
        'feature_fraction_seed': 2018,
        'bagging_fraction': 1.0,
        'bagging_freq': 5,
        'bagging_seed': 2018,
    }

    # gbm = lgb.train(params, train_set,
    #                 num_boost_round=5000,
    #                 valid_sets=[test_set, train_set],
    #                 valid_names=['test', 'train'],
    #                 early_stopping_rounds=100)
    gbm = lgb.cv(params, train_set,
                num_boost_round=500,
                nfold=5,
                stratified=False,
                early_stopping_rounds=100,
                verbose_eval=10,
                seed=2018)
    
#     log += ((gbm.best_score['test']['l2'], gbm.best_iteration), )
    
# for score, iteration in log:
#     print('The best score {0} is at iteration {1}'.format(score, iteration))
