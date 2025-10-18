# CLV Prediction Dashboard

## Overview

A minimalist, clean web interface for visualizing Customer Lifetime Value (CLV) predictions. The dashboard displays multi-model CLV predictions in an interactive, easy-to-navigate format with modern design principles.

## Features

### 🎨 Design Philosophy
- **Minimalist Interface**: Clean white background with Helvetica typography
- **Natural Aesthetics**: Soft rounded corners and gentle shadows
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UX**: Smooth transitions and hover effects

### 📊 Data Visualization
- **Summary Cards**: Key metrics at a glance (total customers, average CLV values)
- **Interactive Table**: Sortable, searchable customer data
- **Real-time Search**: Filter customers by ID or monetary value
- **Pagination**: Navigate through large datasets efficiently
- **Visual Highlights**: Top customers highlighted with special styling

### 🔧 Technical Features
- **Multi-Model Display**: Shows Probabilistic, XGBoost, and Ensemble predictions
- **Component Breakdown**: Expected transactions and order values
- **Sorting Options**: Sort by any model prediction or monetary value
- **Responsive Search**: Instant filtering as you type

## File Structure

```
CLVv11/
├── index.html          # Main dashboard page
├── styles.css          # Minimalist styling
├── script.js           # Interactive functionality
├── server.py           # Simple HTTP server
├── clv_predictions.csv # CLV prediction data
├── model_study.md      # Technical documentation
└── requirements.txt    # Python dependencies
```

## Usage

### Option 1: Run the Python Server (Recommended)

```bash
# Navigate to the project directory
cd "d:\documents\ANN projects\CLVv11"

# Start the web server
python server.py
```

The server will automatically:
- Start on `http://localhost:8080`
- Open your default browser
- Serve all static files

### Option 2: Direct File Access

1. Open `index.html` directly in your browser
2. Ensure all files are in the same directory
3. Note: Some features may be limited without a server

## Dashboard Sections

### Header
- **Title**: "Customer Lifetime Value Dashboard"
- **Subtitle**: Multi-model predictions with optimal weighting

### Summary Cards
Display key metrics:
- **Total Customers**: Number of customers analyzed
- **Avg Ensemble CLV**: Average ensemble prediction
- **Avg Probabilistic CLV**: Average probabilistic model prediction
- **Avg XGBoost CLV**: Average machine learning prediction

### Interactive Table
Shows detailed customer data:
- **Customer ID**: Unique customer identifier
- **Frequency**: Historical purchase frequency
- **Recency**: Days since last purchase
- **Monetary Value**: Total historical spending
- **Probabilistic CLV**: BG/NBD + Gamma-Gamma prediction
- **XGBoost CLV**: Machine learning prediction
- **Ensemble CLV**: Optimal weighted combination
- **Expected Transactions**: Predicted future purchases (12 months)

### Controls
- **Search Box**: Filter customers by ID or monetary value
- **Sort Dropdown**: Sort by different CLV predictions or monetary value
- **Refresh Button**: Reload data from CSV file
- **Pagination**: Navigate through pages of results

## Data Interpretation

### Color Coding
- **Standard rows**: Regular customer data
- **Highlighted rows**: Top 5% of customers by Ensemble CLV (special styling)
- **Search highlights**: Matching text highlighted in yellow

### Model Comparison
- **Probabilistic CLV**: Theoretically sound, interpretable predictions
- **XGBoost CLV**: Data-driven, pattern-based predictions
- **Ensemble CLV**: Optimal combination (90% XGBoost, 10% Probabilistic)

### Top Customers
Customers are ranked by Ensemble CLV. The top tier represents customers with the highest predicted lifetime value, making them prime targets for retention and growth strategies.

## Technical Notes

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- JavaScript ES6+ features used
- CSS Grid and Flexbox for responsive layout

### Performance
- Optimized for large datasets (tested with 4,000+ customers)
- Pagination prevents UI freezing
- Efficient search and sorting algorithms

### Customization
- Colors and fonts easily customizable in `styles.css`
- Table columns configurable in `script.js`
- Server port changeable in `server.py`

## Troubleshooting

### Common Issues

**CSV file not loading**:
- Ensure `clv_predictions.csv` exists in the same directory
- Check file permissions and format

**Server not starting**:
- Port 8080 might be in use
- Try stopping other servers or use a different port

**Styling not loading**:
- Ensure `styles.css` is in the same directory as `index.html`
- Check browser console for 404 errors

**Data not displaying**:
- Verify CSV format matches expected structure
- Check browser console for JavaScript errors

## Architecture

The dashboard follows a modern web architecture:

- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)
- **Backend**: Simple Python HTTP server
- **Data**: Static CSV file (generated by `run_clv_model.py`)
- **Styling**: Custom CSS with minimalist design principles

This approach ensures:
- Fast loading times
- No external dependencies
- Easy deployment
- Maximum compatibility

## Future Enhancements

Potential improvements for future versions:
- **Data Visualization**: Charts and graphs for CLV distributions
- **Export Features**: Download filtered data as CSV/PDF
- **Real-time Updates**: Auto-refresh when CSV data changes
- **Advanced Filters**: Date ranges, CLV thresholds, customer segments
- **Dark Mode**: Alternative color scheme for low-light environments

---

*Built with ❤️ for clean, effective CLV visualization*
