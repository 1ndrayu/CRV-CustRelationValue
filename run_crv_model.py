#!/usr/bin/env python3
"""
Probabilistic CRV Prediction System using BG/NBD & Gamma-Gamma Models

This script implements a customer relationship value prediction system using the lifetimes library.
It combines two probabilistic models:
1. BG/NBD (Beta-Geometric/Negative Binomial Distribution) - predicts future transactions
2. Gamma-Gamma - predicts future monetary value

Date: October 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

from lifetimes.utils import summary_data_from_transaction_data
from lifetimes import BetaGeoFitter, GammaGammaFitter

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(file_path):
    print(f"Loading data from {file_path}...")

    df = pd.read_csv(file_path)

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%d-%m-%Y %H:%M')

    df['CustomerID'] = df['CustomerID'].astype(str)

    print("Filtering valid sales...")
    df = df[df['GrossValue'] > 0]
    df = df[df['CustomerID'].notna()]

    df['GrossValue'] = df['GrossValue'].astype(float)

    print(f"Loaded {len(df)} valid transactions from {df['CustomerID'].nunique()} unique customers")
    return df


def create_rfm_summary(transaction_data):
    print("Creating RFM summary table...")

    observation_period_end = transaction_data['InvoiceDate'].max()

    rfm_summary = summary_data_from_transaction_data(
        transaction_data,
        customer_id_col='CustomerID',
        datetime_col='InvoiceDate',
        monetary_value_col='GrossValue',
        observation_period_end=observation_period_end
    )

    print(f"RFM summary created for {len(rfm_summary)} customers")
    return rfm_summary


def fit_bg_nbd_model(rfm_summary):
    print("Fitting BG/NBD model...")

    bgf = BetaGeoFitter(penalizer_coef=0.1)

    bgf.fit(
        rfm_summary['frequency'],
        rfm_summary['recency'],
        rfm_summary['T']
    )

    print("BG/NBD Model Summary:")
    print(bgf.summary)

    return bgf


def check_gamma_gamma_assumption(rfm_summary):
    print("Checking Gamma-Gamma correlation assumption...")

    correlation = rfm_summary[['frequency', 'monetary_value']].corr().iloc[0, 1]
    print(f"Correlation between frequency and monetary_value: {correlation:.3f}")

    if abs(correlation) > 0.3:
        print("Warning: High correlation detected. Gamma-Gamma assumption may be violated.")
    else:
        print("Correlation is acceptable for Gamma-Gamma model.")


def fit_gamma_gamma_model(rfm_summary):
    print("Fitting Gamma-Gamma model...")

    check_gamma_gamma_assumption(rfm_summary)

    rfm_repeat = rfm_summary[rfm_summary['frequency'] > 0]
    print(f"Using {len(rfm_repeat)} repeat customers for Gamma-Gamma fitting")

    ggf = GammaGammaFitter(penalizer_coef=0.1)

    ggf.fit(
        rfm_repeat['frequency'],
        rfm_repeat['monetary_value']
    )

    print("Gamma-Gamma Model Summary:")
    print(ggf.summary)

    return ggf, rfm_repeat


def calculate_crv_predictions(bgf, ggf, rfm_summary, time_horizon=12, discount_rate=0.01):
    print(f"Calculating {time_horizon}-month CRV predictions...")

    crv_predictions = ggf.customer_lifetime_value(
        bgf,
        rfm_summary['frequency'],
        rfm_summary['recency'],
        rfm_summary['T'],
        rfm_summary['monetary_value'],
        time=time_horizon,
        discount_rate=discount_rate
    )

    print(f"Generated CRV predictions for {len(crv_predictions)} customers")
    print(f"CRV statistics:")
    print(f"- Mean CRV: ${crv_predictions.mean():.2f}")
    print(f"- Median CRV: ${crv_predictions.median():.2f}")
    print(f"- Max CRV: ${crv_predictions.max():.2f}")
    print(f"- Min CRV: ${crv_predictions.min():.2f}")

    return crv_predictions


def train_xgboost_model(rfm_summary, crv_predictions):
    print("Training XGBoost model...")

    features = rfm_summary[['frequency', 'recency', 'T', 'monetary_value']].copy()

    features['recency_to_T_ratio'] = features['recency'] / features['T']
    features['monetary_per_frequency'] = features['monetary_value'] / (features['frequency'] + 1)
    features['log_frequency'] = np.log1p(features['frequency'])
    features['log_monetary'] = np.log1p(features['monetary_value'])

    features = features.replace([np.inf, -np.inf], np.nan).fillna(0)

    target = crv_predictions.copy()

    target_clean = target.replace([np.inf, -np.inf], np.nan).dropna()

    features_clean = features.loc[target_clean.index]

    print(f"Original target size: {len(target)}")
    print(f"Cleaned target size: {len(target_clean)}")

    X_train, X_test, y_train, y_test = train_test_split(
        features_clean, target_clean, test_size=0.2, random_state=42
    )

    print(f"Training data shape: {X_train.shape}")
    print(f"Testing data shape: {X_test.shape}")

    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        objective='reg:squarederror'
    )

    xgb_model.fit(X_train, y_train)

    y_pred = xgb_model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("XGBoost Model Performance:")
    print(f"- Mean Absolute Error: ${mae:.2f}")
    print(f"- Root Mean Square Error: ${rmse:.2f}")

    feature_importance = pd.DataFrame({
        'feature': features_clean.columns,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("Top 5 Most Important Features:")
    print(feature_importance.head())

    return xgb_model, {'mae': mae, 'rmse': rmse}


def predict_with_xgboost(xgb_model, rfm_summary, probabilistic_crv=None):
    print("Generating XGBoost predictions...")

    features = rfm_summary[['frequency', 'recency', 'T', 'monetary_value']].copy()

    features['recency_to_T_ratio'] = features['recency'] / features['T']
    features['monetary_per_frequency'] = features['monetary_value'] / (features['frequency'] + 1)
    features['log_frequency'] = np.log1p(features['frequency'])
    features['log_monetary'] = np.log1p(features['monetary_value'])

    features = features.replace([np.inf, -np.inf], np.nan).fillna(0)

    if probabilistic_crv is not None:
        valid_customers = probabilistic_crv.replace([np.inf, -np.inf], np.nan).notna()
        features = features[valid_customers]
        print(f"Predicting for {len(features)} customers with valid probabilistic CRV")

    xgb_predictions = xgb_model.predict(features)

    xgb_predictions = np.maximum(xgb_predictions, 0)

    print(f"XGBoost predictions range: ${xgb_predictions.min():.2f} - ${xgb_predictions.max():.2f}")

    if probabilistic_crv is not None:
        full_predictions = pd.Series(index=rfm_summary.index, dtype=float)
        if len(xgb_predictions) > 0:
            full_predictions[valid_customers] = xgb_predictions
        else:
            full_predictions[:] = np.nan
        return full_predictions
    else:
        return pd.Series(xgb_predictions, index=features.index)


def find_optimal_ensemble_weights(probabilistic_crv, xgb_crv, rfm_summary, n_splits=5):
    print("Finding optimal ensemble weights using grid search...")

    valid_mask = (probabilistic_crv.replace([np.inf, -np.inf], np.nan).notna() &
                  xgb_crv.replace([np.inf, -np.inf], np.nan).notna())

    prob_clean = probabilistic_crv[valid_mask]
    xgb_clean = xgb_crv[valid_mask]

    print(f"Using {len(prob_clean)} customers with valid predictions for optimization")

    weight_combinations = []
    for prob_weight in np.arange(0.1, 1.0, 0.1):
        xgb_weight = 1.0 - prob_weight
        weight_combinations.append({
            'probabilistic': round(prob_weight, 1),
            'xgboost': round(xgb_weight, 1)
        })

    print(f"Testing {len(weight_combinations)} weight combinations...")

    results = []

    for weights in weight_combinations:
        ensemble_pred = (prob_clean * weights['probabilistic'] +
                        xgb_clean * weights['xgboost'])

        mae_prob = mean_absolute_error(prob_clean, ensemble_pred)
        mae_xgb = mean_absolute_error(xgb_clean, ensemble_pred)

        combined_metric = (mae_prob * weights['probabilistic'] +
                          mae_xgb * weights['xgboost'])

        results.append({
            'weights': weights,
            'combined_mae': combined_metric,
            'prob_mae': mae_prob,
            'xgb_mae': mae_xgb,
            'ensemble_mean': ensemble_pred.mean(),
            'ensemble_std': ensemble_pred.std()
        })

    best_result = min(results, key=lambda x: x['combined_mae'])

    print("\nOptimal Weights Found:")
    print(f"Probabilistic weight: {best_result['weights']['probabilistic']}")
    print(f"XGBoost weight: {best_result['weights']['xgboost']}")
    print(f"Combined MAE: ${best_result['combined_mae']:.2f}")
    print(f"Individual MAEs - Prob: ${best_result['prob_mae']:.2f}, XGB: ${best_result['xgb_mae']:.2f}")

    print("Fine-tuning around optimal weights...")
    best_prob = best_result['weights']['probabilistic']

    granular_weights = []
    for prob_weight in [max(0.1, best_prob - 0.15), best_prob - 0.1, best_prob - 0.05,
                       best_prob, best_prob + 0.05, best_prob + 0.1, min(0.9, best_prob + 0.15)]:
        if 0.1 <= prob_weight <= 0.9:
            xgb_weight = 1.0 - prob_weight
            granular_weights.append({
                'probabilistic': round(prob_weight, 2),
                'xgboost': round(xgb_weight, 2)
            })

    granular_weights = [dict(t) for t in {tuple(d.items()) for d in granular_weights}]

    for weights in granular_weights:
        if weights != best_result['weights']:
            ensemble_pred = (prob_clean * weights['probabilistic'] +
                           xgb_clean * weights['xgboost'])

            mae_prob = mean_absolute_error(prob_clean, ensemble_pred)
            mae_xgb = mean_absolute_error(xgb_clean, ensemble_pred)

            combined_metric = (mae_prob * weights['probabilistic'] +
                             mae_xgb * weights['xgboost'])

            if combined_metric < best_result['combined_mae']:
                best_result = {
                    'weights': weights,
                    'combined_mae': combined_metric,
                    'prob_mae': mae_prob,
                    'xgb_mae': mae_xgb,
                    'ensemble_mean': ensemble_pred.mean(),
                    'ensemble_std': ensemble_pred.std()
                }

    print("Final optimal weights confirmed!")
    print(f"Probabilistic: {best_result['weights']['probabilistic']}")
    print(f"XGBoost: {best_result['weights']['xgboost']}")

    return best_result


def create_ensemble_prediction(probabilistic_crv, xgb_crv, rfm_summary=None, weights=None):
    if weights is None and rfm_summary is not None:
        print("Finding optimal ensemble weights...")
        optimal_result = find_optimal_ensemble_weights(probabilistic_crv, xgb_crv, rfm_summary)
        weights = optimal_result['weights']
    elif weights is None:
        weights = {'probabilistic': 0.7, 'xgboost': 0.3}

    print("Creating ensemble prediction...")
    print(f"Using weights: Probabilistic={weights['probabilistic']}, XGBoost={weights['xgboost']}")

    ensemble_crv = (probabilistic_crv * weights['probabilistic']) + (xgb_crv * weights['xgboost'])

    print("Ensemble prediction statistics:")
    print(f"- Mean CRV: ${ensemble_crv.mean():.2f}")
    print(f"- Median CRV: ${ensemble_crv.median():.2f}")
    print(f"- Max CRV: ${ensemble_crv.max():.2f}")

    return ensemble_crv, weights


def save_crv_predictions(crv_predictions, rfm_summary, bgf, ggf, xgb_model=None, ensemble_crv=None, output_file='crv_predictions.csv'):
    print(f"Saving comprehensive CRV predictions to {output_file}...")

    print("Calculating individual model components...")

    expected_transactions = bgf.conditional_expected_number_of_purchases_up_to_time(
        t=12,
        frequency=rfm_summary['frequency'],
        recency=rfm_summary['recency'],
        T=rfm_summary['T']
    )

    repeat_customers = rfm_summary['frequency'] > 0
    expected_order_value = pd.Series(index=rfm_summary.index, dtype=float)

    if repeat_customers.sum() > 0:
        expected_order_value[repeat_customers] = ggf.conditional_expected_average_profit(
            rfm_summary['frequency'][repeat_customers],
            rfm_summary['monetary_value'][repeat_customers]
        )
        expected_order_value[~repeat_customers] = rfm_summary['monetary_value'][repeat_customers].mean()

    xgb_predictions = None
    if xgb_model is not None:
        xgb_predictions = predict_with_xgboost(xgb_model, rfm_summary, crv_predictions)

    output_data = {
        'CustomerID': rfm_summary.index,
        'Frequency': rfm_summary['frequency'],
        'Recency': rfm_summary['recency'],
        'T': rfm_summary['T'],
        'Monetary_Value': rfm_summary['monetary_value'],
        'Expected_Transactions_12M': expected_transactions.round(2),
        'Expected_Order_Value': expected_order_value.round(2),
        'Probabilistic_CRV': crv_predictions.round(2)
    }

    if xgb_predictions is not None:
        output_data['XGBoost_CRV'] = xgb_predictions.round(2)

    if ensemble_crv is not None:
        # Handle both Series and tuple cases
        if isinstance(ensemble_crv, tuple):
            ensemble_values, _ = ensemble_crv  # Unpack tuple to get the Series
        else:
            ensemble_values = ensemble_crv  # It's already a Series
        output_data['Ensemble_CRV'] = ensemble_values.round(2)

    output_df = pd.DataFrame(output_data)

    sort_column = 'Ensemble_CRV' if ensemble_crv is not None else 'Probabilistic_CRV'
    output_df = output_df.sort_values(sort_column, ascending=False)

    output_df.to_csv(output_file, index=False)

    print(f"Comprehensive CRV predictions saved to {output_file}")

    summary_cols = ['CustomerID', 'Frequency', 'Recency', 'Monetary_Value']
    if xgb_predictions is not None:
        summary_cols.extend(['Probabilistic_CRV', 'XGBoost_CRV'])
        if ensemble_crv is not None:
            summary_cols.append('Ensemble_CRV')

    print(f"\nTop 5 customers by {sort_column.replace('_', ' ')}:")
    print(output_df[summary_cols].head().to_string(index=False))

    print(f"\nModel Comparison Summary:")
    print(f"- Total customers analyzed: {len(output_df)}")

    if ensemble_crv is not None:
        print(f"- Average Ensemble CRV: ${output_df['Ensemble_CRV'].mean():.2f}")
        print(f"- Average Probabilistic CRV: ${output_df['Probabilistic_CRV'].mean():.2f}")
        print(f"- Average XGBoost CRV: ${output_df['XGBoost_CRV'].mean():.2f}")
    else:
        print(f"- Average Probabilistic CRV: ${output_df['Probabilistic_CRV'].mean():.2f}")
        if xgb_predictions is not None:
            print(f"- Average XGBoost CRV: ${output_df['XGBoost_CRV'].mean():.2f}")

    print(f"- Top 10% customers represent: ${output_df[sort_column].quantile(0.9):.2f}")


def main():
    print("Starting Probabilistic CRV Prediction System")
    print("=" * 60)

    data_file = 'data.csv'
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found in current directory")
        sys.exit(1)

    try:
        transaction_data = load_and_preprocess_data(data_file)

        rfm_summary = create_rfm_summary(transaction_data)

        bgf = fit_bg_nbd_model(rfm_summary)

        ggf, _ = fit_gamma_gamma_model(rfm_summary)

        crv_predictions = calculate_crv_predictions(
            bgf, ggf, rfm_summary,
            time_horizon=12,
            discount_rate=0.01
        )

        print("Step 6: Training XGBoost Model")
        xgb_model, xgb_metrics = train_xgboost_model(rfm_summary, crv_predictions)

        xgb_predictions = predict_with_xgboost(xgb_model, rfm_summary, crv_predictions)

        print("Step 8: Creating Ensemble Prediction")
        ensemble_crv, optimal_weights = create_ensemble_prediction(crv_predictions, xgb_predictions, rfm_summary)

        save_crv_predictions(crv_predictions, rfm_summary, bgf, ggf, xgb_model, ensemble_crv)

        print("=" * 60)
        print("CRV Prediction System completed successfully!")
        print("Check crv_predictions.csv for the results")

    except Exception as e:
        print(f"❌ Error during CRV prediction: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
