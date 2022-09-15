#!/usr/bin/env python2.7
import matplotlib
matplotlib.use('Agg')

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

def load_data():
    h = pd.read_csv('historical.csv')
    n = pd.read_csv('new_data.csv')
    categorical_mapping = pd.read_csv('categorical_mapping.csv')
    return h, n, categorical_mapping

def train_models(data, categorical_mapping,
                 abs_correlation_cutoff=0.15,
                 test_fraction=0.30,
    random_state=5123):
    assert 0.0 < abs_correlation_cutoff < 1.0
    assert 0.0 < test_fraction < 1.0
    print "training models (random forest, linear regression, mean model)"    
    random_forest = RandomForestRegressor(n_estimators=10,
                                          criterion="mse",
                                          max_features=None,
                                          max_depth=95,
                                          bootstrap=False,
                                          oob_score=False,
                                          random_state=random_state,
                                          verbose=0)
    linear_reg = LinearRegression(fit_intercept=True)

    print "head of data:"
    print data.head(3)
    print "head of categorical mapping (mapping from category string to additional X values):"
    print categorical_mapping.head(3)    
    ## Want to extend X matrix to include values in categorical_mapping.csv
    # data = pd.concat(data, categorical_mapping)  # Get predictor variables associated with data["category"]
    # np.mean(pd.isnull(data))
    # data.shape  # TODO Something is wrong, number of rows increased and there are lots of NAs, what's going on?
    
    X, y = data.drop('y', axis=1), data['y'].values.flatten()
    print "head of X:"
    print X.head(3)
    
    print "selecting Xs that are correlated with y (abs correlation > {})".format(abs_correlation_cutoff)
    corr_y_X = data.corr()['y'][:-1]
    predictor_indices = np.where(np.abs(corr_y_X) > abs_correlation_cutoff)[0]
    predictor_indices_string = ", ".join([str(x) for x in predictor_indices])                                         
    print " selected {} predictors (columns of X): indices {}".format(len(predictor_indices),
                                                                      predictor_indices_string)
        
    X_selected = X.iloc[:, predictor_indices]
    X_selected_train, X_selected_test, y_train, y_test = train_test_split(X_selected,
                                                                          y,
                                                                          test_size=test_fraction,
                                                                          random_state=random_state)

    print "fitting random forest to training data"
    random_forest.fit(X=X_selected_train, y=y_train)
    print "random forest feature importance (top 20 predictors by importance):"
    importance = pd.DataFrame({"importance":random_forest.feature_importances_,
                               "predictor_index":predictor_indices,
                               "predictor_name":X.columns[predictor_indices],
                               "corr_with_y":np.array(corr_y_X)[predictor_indices]})
    print importance.sort_values("importance", ascending=False).head(20)

    print "fitting linear regression to training data"
    linear_reg.fit(X=X_selected_train, y=y_train)

    print "fitting mean model to training data (mean of training data)"
    mean_model = np.mean(y_train)
    
    rf_predictions_train = random_forest.predict(X=X_selected_train)
    rf_predictions_test = random_forest.predict(X=X_selected_test)

    mean_predictions_train = np.ones_like(rf_predictions_train) * mean_model
    mean_predictions_test = np.ones_like(rf_predictions_test) * mean_model

    linear_predictions_train = linear_reg.predict(X=X_selected_train)
    linear_predictions_test = linear_reg.predict(X=X_selected_test)

    mse_estimates = {"rf_train":mean_squared_error(y_train, rf_predictions_train),
                     "rf_test":mean_squared_error(y_test, rf_predictions_test),
                     
                     "linear_train":mean_squared_error(y_train, linear_predictions_train),
                     "linear_test":mean_squared_error(y_test, linear_predictions_test),
                     
                     "mean_model_train":mean_squared_error(y_train, mean_predictions_train),
                     "mean_model_test":mean_squared_error(y_test, mean_predictions_test)}

    mse_std_errors = {"rf_train":np.std((y_train - rf_predictions_train) ** 2) / np.sqrt(len(y_train)),
                      "rf_test":np.std((y_test - rf_predictions_test) ** 2) / np.sqrt(len(y_test)),
                      
                      "linear_train":np.std((y_train - linear_predictions_train) ** 2) / np.sqrt(len(y_train)),
                      "linear_test":np.std((y_test - linear_predictions_test) ** 2) / np.sqrt(len(y_test)),
                      
                      "mean_model_train":np.std((y_train - mean_predictions_train) ** 2) / np.sqrt(len(y_train)),
                      "mean_model_test":np.std((y_test - mean_predictions_test) ** 2) / np.sqrt(len(y_test))}
           
    return random_forest, linear_reg, mean_model, predictor_indices, mse_estimates, mse_std_errors

def get_predictions(random_forest, linear_reg, mean_model, predictor_indices, data):
    X_selected = data.iloc[:, predictor_indices]
    rf_predictions = random_forest.predict(X_selected)
    linear_predictions = linear_reg.predict(X_selected)
    mean_model_predictions = mean_model * np.ones_like(rf_predictions)
    return (rf_predictions, linear_predictions, mean_model_predictions)

def save_plot_mse_estimates(mse_estimates, mse_std_errors,
    outfile="mse_by_model.png"):
    fig, ax = plt.subplots(figsize=(20, 10))
    mse_train_test_new = {"random forest":[mse_estimates["rf_train"],
                                           mse_estimates["rf_test"],
                                           mse_estimates["rf_new_data"]],
                          "linear model":[mse_estimates["linear_train"],
                                          mse_estimates["linear_test"],
                                          mse_estimates["linear_new_data"]],
                          "mean model":[mse_estimates["mean_model_train"],
                                        mse_estimates["mean_model_test"],
                                        mse_estimates["mean_model_new_data"]]}
    std_errors = {"random forest":[mse_std_errors["rf_train"],
                                   mse_std_errors["rf_test"],
                                   mse_std_errors["rf_new_data"]],
                  "linear model":[mse_std_errors["linear_train"],
                                  mse_std_errors["linear_test"],
                                  mse_std_errors["linear_new_data"]],
                  "mean model":[mse_std_errors["mean_model_train"],
                                mse_std_errors["mean_model_test"],
                                mse_std_errors["mean_model_new_data"]]}
    for model, errors in mse_train_test_new.iteritems():
        plt.plot(range(len(errors)), errors, "-o", label=model, linewidth=1.5, ms=9.0)
        ax.errorbar(range(len(errors)), errors, yerr=std_errors[model], ls='none')

    plt.xlim(-0.2, len(errors) - 1 + 0.2)
    plt.xlabel("0 = train, 1 = test, 2 = new data")
    plt.ylabel("MSE")
    plt.title("Error Estimates (Mean Squared Error) by Model\nWith 95% Confidence Intervals")
    ax.grid(color='grey', linestyle='--', alpha=0.50)
    plt.legend(loc=4)
    plt.savefig(outfile)
    plt.close("all")
    return
    
def main():
    historical_data, new_data, categorical_mapping = load_data()
    n_obs, n_features = historical_data.drop('y', axis=1).shape
    print "Training data: {} observations of {} predictors.".format(n_obs, n_features)
    
    (random_forest,
     linear_reg,
     mean_model,
     predictor_indices,
     mse_estimates,
     mse_std_errors) = train_models(historical_data, categorical_mapping,
                                    test_fraction=0.25, abs_correlation_cutoff=0.10)

    (rf_predictions,
     linear_predictions,
     mean_model_predictions) = get_predictions(random_forest, linear_reg, mean_model,
                                               predictor_indices, new_data.drop('y', axis=1))

    mse_estimates["rf_new_data"] = mean_squared_error(new_data["y"], rf_predictions)
    mse_estimates["linear_new_data"] = mean_squared_error(new_data["y"], linear_predictions)
    mse_estimates["mean_model_new_data"] = mean_squared_error(new_data["y"], mean_model_predictions)

    sqrt_len_new_y = np.sqrt(len(new_data["y"]))
    mse_std_errors["rf_new_data"] = np.std((new_data["y"] - rf_predictions) ** 2) / sqrt_len_new_y
    mse_std_errors["linear_new_data"] = np.std((new_data["y"] - linear_predictions) ** 2) / sqrt_len_new_y
    mse_std_errors["mean_model_new_data"] = np.std((new_data["y"] - mean_model_predictions) ** 2) / sqrt_len_new_y
    
    corr_y_rf_prediction = np.corrcoef(new_data["y"], rf_predictions)[0, 1]
    print "corr(y, rf_predictions) on new data: {}".format(corr_y_rf_prediction)
    corr_y_linear_prediction = np.corrcoef(new_data["y"], linear_predictions)[0, 1]
    print "corr(y, linear_predictions) on new data: {}".format(corr_y_linear_prediction)       

    print "error estimates by model:"
    print " linear regression: train {}, test {}, new data {}".format(mse_estimates["linear_train"],
                                                                      mse_estimates["linear_test"],
                                                                      mse_estimates["linear_new_data"])
    print " random forest: train {}, test {}, new data {}".format(mse_estimates["rf_train"],
                                                                  mse_estimates["rf_test"],
                                                                  mse_estimates["rf_new_data"])
    print " mean model : train {}, test {}, new data {}".format(mse_estimates["mean_model_train"],
                                                                mse_estimates["mean_model_test"],
                                                                mse_estimates["mean_model_new_data"])

    save_plot_mse_estimates(mse_estimates, mse_std_errors)
    
    print "all done"

if __name__ == "__main__":
    main()
