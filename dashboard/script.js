const API_KEY = "4f8c0e0e9d4a4b25ad9173ce49fb2c7a7d13d6c32b3c7fd914d18d39d3a7e9f2"; // Replace this with the actual API key provided by your backend

function toggleNav() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('show-nav');
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function showLoginSignupPopup() {
    if (!sessionStorage.getItem('popupShown')) {
        document.getElementById('loginSignupPopup').style.display = 'flex';
    }
}

function hideLoginSignupPopup() {
    document.getElementById('loginSignupPopup').style.display = 'none';
    sessionStorage.setItem('popupShown', 'true'); // Set a flag to ensure popup doesn't reappear
}

function redirectToLogin() {
    hideLoginSignupPopup();
    window.location.href = '/login';
}

function redirectToSignup() {
    hideLoginSignupPopup();
    window.location.href = '/signup';
}

function stayLoggedOut() {
    hideLoginSignupPopup();
    alert("You have chosen to stay logged out. Proceed with limited features.");
}

async function fetchAgent(type, query = "") {
    const resultElement = document.getElementById('result'); // Ensure this ID matches your HTML
    resultElement.textContent = "Loading...";
    document.getElementById('loadingSpinner').style.display = 'block';

    try {
        let response, data;

        if (type === 'ask-me') {
            // Handle "Ask Me" queries
            if (!query) {
                throw new Error("Query parameter is required for 'Ask Me' functionality.");
            }
            const encodedQuery = encodeURIComponent(query);
            response = await fetch(`/api/ask-me?query=${encodedQuery}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': API_KEY
                }
            });
        } else {
            // Handle other agents
            response = await fetch(`/api/${type}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': API_KEY
                }
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        data = await response.json();

        // Process the response based on the agent type
        switch (type) {
            case 'ask-me':
                const askMeOutput = document.getElementById("askMeOutput");
                askMeOutput.textContent = JSON.stringify(data, null, 2); // Display the response
                break;

            case 'demand':
                resultElement.textContent = JSON.stringify(data.demand_predictions, null, 2); // Display raw data as text
                createDemandChart(data.demand_predictions);
                break;
                
            case 'inventory':
                resultElement.textContent = JSON.stringify(data.inventory_data, null, 2); // Display raw data as text
                createInventoryChart(data.inventory_data);
                break;
                
            case 'pricing':
                resultElement.textContent = JSON.stringify(data.pricing_suggestions, null, 2); // Display raw data as text
                createPricingChart(data.pricing_suggestions);
                break;

            case 'coordination':
                if (data.coordination_suggestions) {
                    resultElement.textContent = JSON.stringify(data.coordination_suggestions, null, 2);
                } else {
                    resultElement.textContent = "No coordination suggestions found.";
                }
                break;

            case 'supplier':
                if (data.supplier_recommendation || data.supplier_recommendations) {
                    const recommendations = Array.isArray(data.supplier_recommendations)
                        ? data.supplier_recommendations
                        : [data.supplier_recommendation];

                    const formattedOutput = recommendations.map(rec => `
                        <div style="background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <p><strong>Product:</strong> ${rec.product}</p>
                            <p><strong>Expected Demand:</strong> ${rec.expected_demand}</p>
                            <p><strong>Recommended Order Quantity:</strong> ${rec.recommended_order_qty}</p>
                            <p><strong>Supplier:</strong> ${rec.supplier_details.supplier}</p>
                        </div>
                    `).join("");

                    resultElement.innerHTML = formattedOutput;
                } else {
                    resultElement.textContent = "No supplier recommendations found.";
                }
                break;
        
            default:
                resultElement.textContent = JSON.stringify(data, null, 2);
        }
    } catch (error) {
        // Show detailed error message
        resultElement.textContent = `❌ Error: ${error.message}`;
    } finally {
        // Hide loading spinner
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

async function fetchScrape() {
    const resultElement = document.getElementById("result");
    resultElement.textContent = "Scraping latest data...";
    try {
        const response = await fetch('/api/scrape');
        const data = await response.json();
        resultElement.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        resultElement.textContent = `❌ Error: ${err.message}`;
    }
}

async function sendChat() {
    const query = document.getElementById("userQuery").value;
    const chatOutput = document.getElementById("chatOutput");

    if (!query) {
        chatOutput.textContent = "❌ Please enter a question.";
        return;
    }

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        chatOutput.textContent = data.response || data.error;
    } catch (err) {
        chatOutput.textContent = `❌ Error: ${err.message}`;
    }
}

let demandChartInstance = null;
let inventoryChartInstance = null;
let pricingChartInstance = null;

function createDemandChart(data) {
    const ctx = document.getElementById('demandChart').getContext('2d');
    const labels = data.map(item => `Product ${item['Product ID']}`);
    const values = data.map(item => item['Predicted Demand']);

    if (demandChartInstance) {
        demandChartInstance.data.labels = labels;
        demandChartInstance.data.datasets[0].data = values;
        demandChartInstance.update();
    } else {
        demandChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Predicted Demand',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function createInventoryChart(data) {
    const ctx = document.getElementById('inventoryChart').getContext('2d');
    const labels = data.map(item => `Product ${item['Product ID']}`);
    const values = data.map(item => item['Stock Levels']);

    if (inventoryChartInstance) {
        inventoryChartInstance.data.labels = labels;
        inventoryChartInstance.data.datasets[0].data = values;
        inventoryChartInstance.update();
    } else {
        inventoryChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stock Levels',
                    data: values,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function createPricingChart(data) {
    const ctx = document.getElementById('pricingChart').getContext('2d');
    const labels = data.map(item => `Product ${item['Product ID']}`);
    const values = data.map(item => item['suggested_price']);

    if (pricingChartInstance) {
        pricingChartInstance.data.labels = labels;
        pricingChartInstance.data.datasets[0].data = values;
        pricingChartInstance.update();
    } else {
        pricingChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Suggested Prices',
                    data: values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

async function filterProducts() {
    const filterCount = document.getElementById('filterCount').value;
    const resultElement = document.getElementById('result');
    if (!filterCount || isNaN(filterCount) || parseInt(filterCount) <= 0) {
        alert("Please enter a valid filter count!");
        return;
    }

    try {
        const response = await fetch(`/api/coordination`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY
            },
            body: JSON.stringify({ filter: filterCount }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        if (data.filtered_products) {
            resultElement.textContent = JSON.stringify(data.filtered_products, null, 2);
        } else {
            resultElement.textContent = "No products found for the given filter.";
        }
    } catch (error) {
        resultElement.textContent = `❌ Error: ${error.message}`;
    }
}

function handleAskMe() {
    const query = document.getElementById("userQuery").value;
    const askMeOutput = document.getElementById("askMeOutput");
    if (!query) {
        alert("Please enter a query!");
        return;
    }
    askMeOutput.textContent = "Loading..."; // Show loading indicator

    fetch(`/api/ask-me?query=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': API_KEY
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            askMeOutput.textContent = `❌ Error: ${data.error}`;
        } else {
            askMeOutput.textContent = JSON.stringify(data, null, 2);
        }
    })
    .catch(error => {
        askMeOutput.textContent = `❌ Error: ${error.message}`;
    });
}