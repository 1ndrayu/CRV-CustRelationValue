// CRV Customer Search - Simplified Version
class CRVSearch {
    constructor() {
        this.allData = [];
        this.searchResults = [];
        this.currentSearchField = 'CustomerID';
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.initializeApp();
    }

    initializeApp() {
        console.log('Starting CRV Search initialization...');
        this.loadDataSynchronously();
        this.setupCalculator();
        this.setupTabs();
    }

    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons and contents
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                // Add active class to clicked button and target content
                btn.classList.add('active');
                const targetId = btn.getAttribute('data-tab');
                document.getElementById(targetId).classList.add('active');
            });
        });
    }

    setupCalculator() {
        const calcBtn = document.getElementById('calc-btn');
        if (!calcBtn) return;
        
        calcBtn.addEventListener('click', () => {
            const m = parseFloat(document.getElementById('calc-monetary').value) || 0;
            const r = parseFloat(document.getElementById('calc-recency').value) || 0;
            const f = parseFloat(document.getElementById('calc-frequency').value) || 0;
            
            // Scalable factors from basic data analysis
            const factorM = 3.8116;
            const factorR = 8.9862;
            const factorF = 401.7575;
            
            const estimatedCrv = (m * factorM) + (r * factorR) + (f * factorF);
            
            const resultDiv = document.getElementById('calc-result');
            resultDiv.textContent = `Estimated CRV: $${estimatedCrv.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        });
    }

    loadDataSynchronously() {
        console.log('Loading CSV data...');
        const csvText = this.loadCSVFile();
        if (csvText) {
            this.allData = this.parseCSV(csvText);
            console.log(`Loaded ${this.allData.length} customer records`);
            this.setupEventListeners();
            this.showAllData();
        } else {
            this.showError('Failed to load CSV file');
        }
    }

    loadCSVFile() {
        try {
            // Use synchronous XMLHttpRequest for simplicity
            const xhr = new XMLHttpRequest();
            xhr.open('GET', 'crv_predictions.csv', false); // synchronous
            xhr.send();

            if (xhr.status === 200) {
                return xhr.responseText;
            } else {
                console.error('Failed to load CSV:', xhr.status);
                return null;
            }
        } catch (error) {
            console.error('Error loading CSV file:', error);
            return null;
        }
    }

    parseCSV(csvText) {
        const lines = csvText.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.trim());

        return lines.slice(1).map((line, index) => {
            const values = line.split(',').map(v => v.trim());

            const obj = {};
            headers.forEach((header, i) => {
                const value = values[i];

                // Handle numeric fields
                if (['Frequency', 'Recency', 'T', 'Monetary_Value', 'Probabilistic_CRV', 'XGBoost_CRV', 'Ensemble_CRV', 'Expected_Transactions_12M'].includes(header)) {
                    const num = parseFloat(value);
                    obj[header] = isNaN(num) ? 0 : num;
                } else {
                    obj[header] = value || '';
                }
            });

            return obj;
        }).filter(row => row.CustomerID && row.CustomerID !== 'nan');
    }

    setupEventListeners() {
        // Field selector
        const fieldSelect = document.getElementById('search-field');
        if (fieldSelect) {
            fieldSelect.addEventListener('change', (e) => {
                this.currentSearchField = e.target.value;
                this.currentPage = 1;
                this.displayResults(this.searchResults);
                this.updatePagination();
            });
        }

        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }

        // Search button
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch();
            });
        }

        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Pagination buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.displayResults(this.searchResults);
                    this.updatePagination();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(this.searchResults.length / this.itemsPerPage);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.displayResults(this.searchResults);
                    this.updatePagination();
                }
            });
        }
    }

    performSearch() {
        const searchInput = document.getElementById('search-input');
        const searchTerm = searchInput?.value?.trim();

        if (!searchTerm) {
            this.showAllData();
            return;
        }

        const results = this.allData.filter(customer => {
            const fieldValue = customer[this.currentSearchField];

            if (fieldValue === undefined || fieldValue === null) {
                return false;
            }

            const fieldStr = fieldValue.toString().toLowerCase();
            const searchStr = searchTerm.toLowerCase();

            return fieldStr.includes(searchStr);
        });

        this.searchResults = results;
        this.currentPage = 1;
        this.displayResults(results);
        this.updatePagination();
    }

    displayResults(results) {
        const tbody = document.getElementById('results-body');
        if (!tbody) return;

        if (results.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="no-data">No customers found</td>
                </tr>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = results.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        pageData.forEach(customer => {
            const row = document.createElement('tr');
            const cells = [
                customer.CustomerID || 'N/A',
                customer.Frequency || 0,
                customer.Recency || 0,
                `$${customer.Monetary_Value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${customer.Probabilistic_CRV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${customer.XGBoost_CRV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                `$${customer.Ensemble_CRV?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}`,
                (customer.Expected_Transactions_12M || 0).toFixed(2)
            ];

            cells.forEach(cellData => {
                const cell = document.createElement('td');
                cell.textContent = cellData;
                row.appendChild(cell);
            });

            tbody.appendChild(row);
        });
    }

    updatePagination() {
        const totalPages = Math.ceil(this.searchResults.length / this.itemsPerPage);
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, this.searchResults.length);

        const paginationInfo = document.getElementById('pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${this.searchResults.length} results`;
        }

        const currentPageSpan = document.querySelector('.current-page');
        if (currentPageSpan) {
            currentPageSpan.textContent = this.currentPage;
        }

        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1 || this.searchResults.length === 0;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage === totalPages || this.searchResults.length === 0;
        }
    }

    showAllData() {
        this.searchResults = [...this.allData];
        this.currentPage = 1;
        this.displayResults(this.allData);
        this.updatePagination();
    }

    clearSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        this.showAllData();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CRVSearch();
});
