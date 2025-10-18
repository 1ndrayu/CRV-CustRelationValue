// CLV Dashboard JavaScript
class CLVDashboard {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.itemsPerPage = 5;
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
    }

    async loadData() {
        try {
            this.showLoading();
            console.log('Attempting to fetch CSV file...');

            const response = await fetch('clv_predictions.csv');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const csvText = await response.text();
            console.log('CSV loaded successfully, length:', csvText.length);

            if (!csvText.trim()) {
                throw new Error('CSV file is empty');
            }

            this.data = this.parseCSV(csvText);
            console.log('Parsed data:', this.data.length, 'rows');

            if (this.data.length === 0) {
                throw new Error('No valid data found in CSV');
            }

            this.filteredData = [...this.data];
            console.log('Data loaded successfully');

            this.updateSummaryCards();
            this.renderTable();
            this.hideLoading();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError(`Failed to load CLV data: ${error.message}`);
        }
    }

    parseCSV(csvText) {
        try {
            const lines = csvText.split('\n').filter(line => line.trim());
            console.log('Total lines in CSV:', lines.length);

            if (lines.length < 2) {
                throw new Error('CSV must have at least header and one data row');
            }

            const headers = lines[0].split(',').map(header => header.trim());
            console.log('Headers:', headers);

            const data = lines.slice(1).map((line, index) => {
                try {
                    const values = line.split(',').map(value => value.trim());

                    if (values.length !== headers.length) {
                        console.warn(`Row ${index + 2} has ${values.length} columns, expected ${headers.length}`);
                        return null; // Skip malformed rows
                    }

                    const obj = {};
                    headers.forEach((header, colIndex) => {
                        const value = values[colIndex];

                        // Handle numeric columns
                        if (header.includes('CLV') || header.includes('Value') ||
                            header.includes('Transactions') || header.includes('Frequency') ||
                            header.includes('Recency') || header.includes('T')) {
                            const numValue = parseFloat(value);
                            obj[header] = isNaN(numValue) ? 0 : numValue;
                        } else {
                            obj[header] = value || '';
                        }
                    });

                    return obj;
                } catch (rowError) {
                    console.warn(`Error parsing row ${index + 2}:`, rowError);
                    return null; // Skip problematic rows
                }
            }).filter(row => row !== null && row.CustomerID !== '');

            console.log('Successfully parsed', data.length, 'valid rows');
            return data;

        } catch (error) {
            console.error('CSV parsing error:', error);
            throw new Error(`Failed to parse CSV: ${error.message}`);
        }
    }

    updateSummaryCards() {
        if (this.data.length === 0) return;

        const totalCustomers = this.data.length;

        const avgEnsemble = this.calculateAverage('Ensemble_CLV');
        const avgProbabilistic = this.calculateAverage('Probabilistic_CLV');
        const avgXGBoost = this.calculateAverage('XGBoost_CLV');

        this.updateElement('total-customers', totalCustomers.toLocaleString());
        this.updateElement('avg-ensemble', `$${avgEnsemble.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
        this.updateElement('avg-probabilistic', `$${avgProbabilistic.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
        this.updateElement('avg-xgboost', `$${avgXGBoost.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
    }

    calculateAverage(column) {
        if (this.data.length === 0) return 0;
        const sum = this.data.reduce((acc, row) => acc + (row[column] || 0), 0);
        return sum / this.data.length;
    }

    renderTable() {
        const tableBody = document.getElementById('table-body');
        if (!tableBody) {
            console.error('Table body not found');
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        tableBody.innerHTML = '';

        pageData.forEach((row, index) => {
            const tr = document.createElement('tr');

            // Highlight top customers (top 5% by ensemble CLV)
            const topThreshold = this.calculatePercentile(95, 'Ensemble_CLV');
            if (row.Ensemble_CLV >= topThreshold) {
                tr.classList.add('top-customer');
            }

            const cellData = [
                row.CustomerID || 'N/A',
                row.Frequency || 0,
                row.Recency || 0,
                `$${row.Monetary_Value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${row.Probabilistic_CLV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${row.XGBoost_CLV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${row.Ensemble_CLV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                row.Expected_Transactions_12M?.toFixed(2) || '0.00'
            ];

            cellData.forEach((data, cellIndex) => {
                const td = document.createElement('td');
                td.textContent = data;

                // Highlight search results
                const searchTerm = document.getElementById('search-input')?.value?.toLowerCase();
                if (searchTerm && data.toString().toLowerCase().includes(searchTerm)) {
                    td.classList.add('highlight');
                }

                tr.appendChild(td);
            });

            tableBody.appendChild(tr);
        });

        this.updatePagination();
    }

    updatePagination() {
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (!pageInfo || !prevBtn || !nextBtn) {
            console.error('Pagination elements not found');
            return;
        }

        const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);

        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;

        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages || totalPages === 0;
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        const searchBtn = document.getElementById('search-btn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterData(e.target.value);
            });
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.filterData(searchInput?.value || '');
            });
        }

        // Sort functionality
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortData(e.target.value);
            });
        }

        // Pagination
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.renderTable();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.renderTable();
                }
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadData();
            });
        }
    }

    filterData(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredData = [...this.data];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredData = this.data.filter(row => {
                return (row.CustomerID && row.CustomerID.toString().toLowerCase().includes(term)) ||
                       (row.Monetary_Value && row.Monetary_Value.toString().toLowerCase().includes(term));
            });
        }

        this.currentPage = 1;
        this.renderTable();
    }

    sortData(sortBy) {
        const sortColumn = this.getSortColumn(sortBy);

        this.filteredData.sort((a, b) => {
            const aVal = a[sortColumn] || 0;
            const bVal = b[sortColumn] || 0;

            if (typeof aVal === 'string') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal - aVal; // Descending for numeric values
            }
        });

        this.renderTable();
    }

    getSortColumn(sortBy) {
        const columnMap = {
            'ensemble': 'Ensemble_CLV',
            'probabilistic': 'Probabilistic_CLV',
            'xgboost': 'XGBoost_CLV',
            'monetary': 'Monetary_Value'
        };
        return columnMap[sortBy] || 'Ensemble_CLV';
    }

    calculatePercentile(percentile, column) {
        if (this.data.length === 0) return 0;

        const values = this.data.map(row => row[column] || 0).sort((a, b) => a - b);
        const index = (percentile / 100) * (values.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);

        if (lower === upper) {
            return values[lower];
        }

        return values[lower] * (upper - index) + values[upper] * (index - lower);
    }

    showLoading() {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Loading CLV data...</p>
                </div>
            `;
        } else {
            console.error('Table container not found');
        }
    }

    hideLoading() {
        // Loading is hidden when renderTable() is called
    }

    showError(message) {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="loading" style="color: #e74c3c;">
                    <p>⚠️ ${message}</p>
                    <button onclick="dashboard.loadData()" style="margin-top: 15px; padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 20px; cursor: pointer;">Retry</button>
                </div>
            `;
        } else {
            console.error('Table container not found for error display');
            // Fallback: try to show error in console or alert
            alert(`Error: ${message}`);
        }
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new CLVDashboard();
});
