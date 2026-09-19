import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json

def main():
    print("Loading crv_predictions.csv...")
    df = pd.read_csv('crv_predictions.csv')
    
    # Drop rows where any of the required columns are NaN
    cols = ['Monetary_Value', 'Recency', 'Frequency', 'Probabilistic_CRV']
    df_clean = df.dropna(subset=cols)
    
    # Filter out invalid values (e.g., negative or infinity)
    df_clean = df_clean[
        (df_clean['Probabilistic_CRV'] > 0) & 
        (df_clean['Probabilistic_CRV'] != np.inf)
    ]
    
    if len(df_clean) == 0:
        print("No valid data for training!")
        return

    X = df_clean[['Monetary_Value', 'Recency', 'Frequency']]
    y = df_clean['Probabilistic_CRV']
    
    print(f"Training simple linear regression on {len(X)} records...")
    model = LinearRegression()
    model.fit(X, y)
    
    factors = {
        "intercept": float(model.intercept_),
        "Monetary_Value": float(model.coef_[0]),
        "Recency": float(model.coef_[1]),
        "Frequency": float(model.coef_[2]),
        "r2_score": float(model.score(X, y))
    }
    
    print("Extracted Factors:")
    print(json.dumps(factors, indent=4))
    
    with open('crv_factors.json', 'w') as f:
        json.dump(factors, f, indent=4)
    print("Saved factors to crv_factors.json")

if __name__ == '__main__':
    main()
