# Multi-Model CRV Prediction System with Web Dashboard

A sophisticated Customer Relationship Value (CRV) prediction system that combines probabilistic modeling, machine learning, and dynamic ensemble optimization. Features a beautiful minimalist web interface for interactive data exploration.

## 🎯 Project Overview

This system evolved from a basic probabilistic CRV model to a comprehensive multi-model approach that delivers optimal prediction accuracy through:

- **Probabilistic Models**: BG/NBD + Gamma-Gamma for theoretical soundness
- **Machine Learning**: XGBoost with engineered features for empirical accuracy
- **Dynamic Optimization**: Data-driven ensemble weighting (90% XGBoost, 10% Probabilistic)
- **Interactive Dashboard**: Clean, minimalist web interface for data exploration

## 📁 Project Files & Functionality

### Core Model Files

| File | Purpose | Key Functionality |
|------|---------|-------------------|
| **`run_crv_model.py`** | Main CRV prediction engine | Orchestrates entire prediction pipeline from data loading to ensemble optimization |
| **`data.csv`** | Input transaction data | Raw customer transaction records (530K+ transactions, 4.3K customers) |
| **`crv_predictions.csv`** | Generated prediction results | 10-column comprehensive output with all model predictions |

### Web Dashboard Files

| File | Purpose | Key Functionality |
|------|---------|-------------------|
| **`index.html`** | Main dashboard interface | Clean, responsive HTML structure with semantic markup |
| **`styles.css`** | Minimalist styling | Helvetica typography, white background, rounded corners, soft shadows |
| **`script.js`** | Interactive functionality | CSV loading, search, sorting, pagination (5 records/page) |
| **`server.py`** | HTTP server | CORS-enabled server for static file serving |

### Documentation & Configuration

| File | Purpose | Key Functionality |
|------|---------|-------------------|
| **`model_study.md`** | Technical evolution analysis | Documents architectural iterations and performance improvements |
| **`dashboard_readme.md`** | Web interface documentation | Detailed dashboard features and customization guide |
| **`requirements.txt`** | Python dependencies | All required packages for model execution |

## 🚀 How to Run

### Option 1: Terminal Execution (Model Training)

**Prerequisites:**
```bash
pip install -r requirements.txt
```

**Run the CRV Model:**
```bash
python run_crv_model.py
```

**What Happens:**
1. **Data Loading**: Processes 530K+ transactions from `data.csv`
2. **Model Training**: Fits BG/NBD and Gamma-Gamma probabilistic models
3. **Feature Engineering**: Creates 8 XGBoost features from RFM data
4. **XGBoost Training**: Machine learning model with performance validation
5. **Ensemble Optimization**: Finds optimal weights (90% XGBoost, 10% Probabilistic)
6. **Output Generation**: Creates `crv_predictions.csv` with 10 analytical columns

**Expected Runtime**: ~2-3 minutes
**Output File**: `crv_predictions.csv` (272KB, 4,339 customers)

### Option 2: Web Dashboard (Interactive Exploration)

**Prerequisites:**
- Run the CRV model first (see Option 1) to generate `crv_predictions.csv`
- Ensure all web files are present in the project directory

**Start the Web Server:**
```bash
python server.py
```

**Access the Dashboard:**
- Server automatically opens: `http://localhost:8000`
- Manual access: Navigate to `http://localhost:8000` in your browser

**Dashboard Features:**
- **Summary Cards**: Key metrics (total customers, average CRV values)
- **Interactive Table**: Sortable, searchable customer data (5 records/page)
- **Search Functionality**: Filter by Customer ID or monetary value
- **Pagination**: Navigate through 868 pages of customer data
- **Visual Highlights**: Top 5% customers specially highlighted

## 📊 Output Data Structure

The `crv_predictions.csv` contains 10 analytical columns:

| Column | Description | Model/Source |
|--------|-------------|--------------|
| `CustomerID` | Unique customer identifier | Input data |
| `Frequency` | Historical purchase frequency | Input data |
| `Recency` | Days since last purchase | Input data |
| `T` | Customer age (days) | Input data |
| `Monetary_Value` | Total historical spending | Input data |
| `Expected_Transactions_12M` | Predicted future purchases | BG/NBD model |
| `Expected_Order_Value` | Predicted order value | Gamma-Gamma model |
| `Probabilistic_CRV` | Theoretical CRV prediction | BG/NBD + Gamma-Gamma |
| `XGBoost_CRV` | Machine learning prediction | XGBoost model |
| `Ensemble_CRV` | Optimal weighted prediction | 90% XGBoost + 10% Probabilistic |

## 🎯 Business Value & Applications

### For Marketing Teams
- **Customer Segmentation**: Identify high-value customers for targeted campaigns
- **Budget Allocation**: Focus marketing spend on customers with highest predicted value
- **Retention Strategies**: Prioritize customers most likely to churn vs. high future value

### For Sales Teams
- **Lead Prioritization**: Focus sales efforts on customers with highest CRV potential
- **Account Management**: Allocate account manager time based on predicted value
- **Upselling Opportunities**: Target customers with capacity for increased spending

### For Strategic Planning
- **Revenue Forecasting**: Predict future customer value for business planning
- **Resource Allocation**: Optimize team resources based on customer value distribution
- **Performance Metrics**: Track CRV prediction accuracy against actual outcomes

### Key Business Insights Delivered

**Customer Insights:**
- Top 5% of customers represent the highest-value segment
- Average Ensemble CRV: $3,649 per customer
- Optimal model weighting discovered through data-driven optimization

**Predictive Power:**
- Combines theoretical probabilistic modeling with empirical machine learning
- 12-month prediction horizon for strategic planning
- Continuous model improvement through ensemble optimization

**Operational Efficiency:**
- Automated prediction pipeline (2-3 minute execution)
- Interactive dashboard for stakeholder exploration
- Data-driven decision making vs. intuition-based approaches

## 🔧 Technical Architecture

### Model Pipeline
1. **Data Ingestion**: Load and validate 530K+ transaction records
2. **RFM Calculation**: Generate customer-level behavioral metrics
3. **Probabilistic Modeling**: BG/NBD (transactions) + Gamma-Gamma (monetary value)
4. **Feature Engineering**: Create 8 XGBoost features from RFM data
5. **XGBoost Training**: Machine learning model with cross-validation
6. **Ensemble Optimization**: Grid search for optimal model weighting
7. **Output Generation**: Comprehensive CSV with all model predictions

### Web Dashboard Architecture
1. **Static File Serving**: Python HTTP server with CORS support
2. **Dynamic CSV Loading**: JavaScript fetch API for data loading
3. **Interactive Components**: Search, sort, pagination functionality
4. **Responsive Design**: Mobile-friendly interface

## 🎨 Design Philosophy

The web dashboard embodies minimalist design principles:
- **Clean Typography**: Helvetica Neue for maximum readability
- **Generous Whitespace**: Focused, uncluttered layout
- **Subtle Visual Hierarchy**: Natural information flow
- **Responsive Interactions**: Smooth transitions and hover effects
- **Accessible Color Palette**: High contrast for readability

## 🚀 Performance & Scalability

- **Dataset Size**: Handles 530K+ transactions efficiently
- **Processing Speed**: Complete pipeline in 2-3 minutes
- **Memory Efficient**: Optimized for large customer bases
- **Web Performance**: Fast loading with pagination (5 records/page)
- **Scalable Architecture**: Easy to add new models or features

## 🔮 Future Enhancements

Potential expansions for enhanced business value:
- **Real-time Predictions**: Live model updates as new data arrives
- **Advanced Segmentation**: Demographic and behavioral customer clusters
- **Cohort Analysis**: Track CRV predictions over time periods
- **API Endpoints**: RESTful API for integration with other systems
- **Export Capabilities**: PDF reports and advanced data export options

---

*Built with precision engineering for maximum predictive accuracy and business impact* 🎯✨
