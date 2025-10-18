# Probabilistic CLV Prediction System

This project implements a Customer Lifetime Value (CLV) prediction system using probabilistic models from the `lifetimes` library.

## Overview

The system combines two key probabilistic models:
- **BG/NBD (Beta-Geometric/Negative Binomial Distribution)**: Predicts future transaction behavior
- **Gamma-Gamma**: Predicts future monetary value per transaction

## Requirements

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the CLV prediction script:
```bash
python run_clv_model.py
```

### What the script does:

1. **Data Ingestion**: Loads transaction data from `data.csv`
2. **Preprocessing**: Filters valid sales, parses dates, handles data types
3. **RFM Summary**: Creates customer-level summary using `lifetimes.utils.summary_data_from_transaction_data`
4. **Model Fitting**:
   - Fits BG/NBD model to predict future transactions
   - Fits Gamma-Gamma model to predict monetary value (repeat customers only)
5. **CLV Calculation**: Combines both models to predict 12-month CLV
6. **Output**: Generates `clv_predictions.csv` with customer rankings

## Input Data Format

The script expects a CSV file (`data.csv`) with these columns:
- `InvoiceDate`: Date in DD-MM-YYYY HH:MM format
- `InvoiceNo`: Transaction ID
- `CustomerID`: Customer identifier
- `Quantity`: Number of items purchased
- `UnitPrice`: Price per item
- `GrossValue`: Total transaction value

## Output

The script generates `clv_predictions.csv` with:
- `CustomerID`: Customer identifier
- `Predicted_CLV_12_Months`: 12-month CLV prediction (sorted descending)

## Configuration

You can modify these parameters in the script:
- `time_horizon`: Months to predict (default: 12)
- `discount_rate`: Monthly discount rate (default: 0.01)
- `penalizer_coef`: Regularization parameter for models (default: 0.1)

## Model Assumptions

- **BG/NBD**: Models customer "alive" probability and purchase frequency
- **Gamma-Gamma**: Assumes frequency and monetary value are uncorrelated (correlation < 0.3 is ideal)

The script includes correlation checking and will warn if assumptions are violated.
