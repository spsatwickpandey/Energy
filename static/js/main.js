// main.js
// All main UI logic moved from inline script in index.html

// Utility functions
function generateColors(count) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#2ECC71', '#E74C3C', '#9B59B6', '#1ABC9C'
    ];
    return colors.slice(0, count);
}
function determineHouseholdType(members) {
    if (members === 1) return 'bachelor';
    if (members === 2) return 'couple';
    if (members <= 4) return 'nuclear';
    return 'joint';
}

const applianceBrands = window.applianceBrands || {};
let applianceCount = 0;
let currentAnalysisData = null;
window.currentSessionId = null;   // set after /predict succeeds
window.lastRecommendations = null; // set after AI recommendations load

function addAppliance() {
    const appliancesList = document.getElementById('appliancesList');
    const applianceDiv = document.createElement('div');
    applianceDiv.className = 'appliance-card position-relative';
    applianceDiv.innerHTML = `
        <div class="row">
            <div class="col-md-3 mb-3">
                <label class="form-label">Appliance Type</label>
                <select class="form-select" onchange="updateBrands(this)" required>
                    <option value="">Select type...</option>
                    ${Object.keys(applianceBrands).map(type => `<option value="${type}">${type}</option>`).join('')}
                </select>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Brand</label>
                <select class="form-select" onchange="updateModels(this)" required>
                    <option value="">Select brand...</option>
                </select>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Model</label>
                <select class="form-select" required>
                    <option value="">Select model...</option>
                </select>
            </div>
            <div class="col-md-3 mb-3">
                <label class="form-label">Quantity</label>
                <input type="number" class="form-control" required min="1" value="1" onchange="updateUsageHours(this)">
            </div>
        </div>
        <div class="row usage-hours-container" id="usageHours${applianceCount}">
            <div class="col-md-3 mb-3">
                <label class="form-label">Usage Hours (Unit 1)</label>
                <input type="number" class="form-control usage-hours" required min="0" max="24" step="0.1">
            </div>
        </div>
        <button type="button" class="btn btn-danger btn-remove" onclick="this.parentElement.remove()">
            <i class="fas fa-trash me-1"></i>Remove
        </button>
    `;
    appliancesList.appendChild(applianceDiv);
    applianceCount++;
}
window.addAppliance = addAppliance;

function updateBrands(select) {
    const brandSelect = select.parentElement.nextElementSibling.querySelector('select');
    const modelSelect = brandSelect.parentElement.nextElementSibling.querySelector('select');
    const selectedType = select.value;
    const brands = Object.keys(applianceBrands[selectedType] || {});
    brandSelect.innerHTML = '<option value="">Select brand...</option>' + brands.map(brand => `<option value="${brand}">${brand}</option>`).join('');
    modelSelect.innerHTML = '<option value="">Select model...</option>';
}
window.updateBrands = updateBrands;

function updateModels(select) {
    const applianceType = select.parentElement.previousElementSibling.querySelector('select').value;
    const brand = select.value;
    const modelSelect = select.parentElement.nextElementSibling.querySelector('select');
    const models = applianceBrands[applianceType][brand] || [];
    modelSelect.innerHTML = '<option value="">Select model...</option>' + models.map(model => `<option value="${model}">${model}</option>`).join('');
}
window.updateModels = updateModels;

function updateUsageHours(quantityInput) {
    const container = quantityInput.closest('.row').nextElementSibling;
    const quantity = parseInt(quantityInput.value) || 1;
    container.innerHTML = '';
    for (let i = 0; i < quantity; i++) {
        container.innerHTML += `
            <div class="col-md-3 mb-3">
                <label class="form-label">Usage Hours (Unit ${i + 1})</label>
                <input type="number" class="form-control usage-hours" required min="0" max="24" step="0.1">
            </div>
        `;
    }
}
window.updateUsageHours = updateUsageHours;

function destroyExistingCharts() {
    try {
        ['consumptionChart', 'loadChart', 'peakHourChart', 'seasonalChart'].forEach(id => {
            const canvas = document.getElementById(id);
            if (canvas) {
                const chart = Chart.getChart(canvas);
                if (chart) {
                    chart.destroy();
                }
            }
        });
    } catch (error) {
        console.error('Error destroying charts:', error);
    }
}

function displayResults(result) {
    const resultsCard = document.getElementById('resultsCard');
    const applianceResults = document.getElementById('applianceResults');
    const totalConsumption = document.getElementById('totalConsumption');
    const totalLoad = document.getElementById('totalLoad');
    applianceResults.innerHTML = '';
    totalConsumption.textContent = result.total_consumption;
    totalLoad.textContent = result.total_load_kw;
    result.appliance_predictions.forEach(prediction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prediction.type}</td>
            <td>${prediction.load_kw} kW</td>
            <td>${prediction.consumption} units</td>
            <td>₹${prediction.total_charges}</td>
        `;
        applianceResults.appendChild(row);
    });
    document.getElementById('contractedLoad').textContent = result.bill_details.contracted_load;
    document.getElementById('totalConsumptionBill').textContent = result.total_consumption;
    document.getElementById('slab1').textContent = parseFloat(result.bill_details.consumption_slabs['0-150']).toFixed(2);
    document.getElementById('slab2').textContent = parseFloat(result.bill_details.consumption_slabs['151-300']).toFixed(2);
    document.getElementById('slab3').textContent = parseFloat(result.bill_details.consumption_slabs['above_300']).toFixed(2);
    document.getElementById('fixedCharges').textContent = result.bill_details.fixed_charges;
    document.getElementById('energyCharges').textContent = result.bill_details.energy_charges;
    document.getElementById('electricityDuty').textContent = result.bill_details.electricity_duty;
    document.getElementById('totalBill').textContent = result.bill_details.total_bill;
    // Capture session_id from MongoDB
    if (result.session_id) { window.currentSessionId = result.session_id; }

    currentAnalysisData = {
        familyDetails: {
            totalMembers: parseInt(document.getElementById('totalMembers').value),
            maleMembers: parseInt(document.getElementById('maleMembers').value),
            femaleMembers: parseInt(document.getElementById('femaleMembers').value),
            children: parseInt(document.getElementById('children').value),
            householdType: determineHouseholdType(parseInt(document.getElementById('totalMembers').value))
        },
        appliances: result.appliances,
        appliance_predictions: result.appliance_predictions.map(p => ({
            ...p,
            type: p.type.split(' (')[0]
        })),
        total_consumption: result.total_consumption,
        total_load_kw: result.total_load_kw
    };
    // --- Ensure AI recommendations use latest data ---
    window.userData = {
        totalMembers: parseInt(document.getElementById('totalMembers').value),
        maleMembers: parseInt(document.getElementById('maleMembers').value),
        femaleMembers: parseInt(document.getElementById('femaleMembers').value),
        children: parseInt(document.getElementById('children').value),
        householdType: determineHouseholdType(parseInt(document.getElementById('totalMembers').value))
    };
    window.predictions = {
        ...result,
        appliance_breakdown: result.appliance_predictions
    };
    // Set chart data for analysis
    if (window.setAnalysisData) {
        window.setAnalysisData({
            appliance_breakdown: result.appliance_predictions.map(p => ({
                type: p.type,
                consumption: p.consumption,
                load_kw: p.load_kw
            }))
        });
    }
    resultsCard.style.display = 'block';
    document.getElementById('showAnalysisBtn').style.display = 'block';
    const analysisSection = document.getElementById('analysisSection');
    if (analysisSection.style.display === 'block') {
        updateCharts();
    }
    document.querySelector('.loading-spinner').style.display = 'none';
}
window.displayResults = displayResults;

let consumptionChartInstance = null;
let loadChartInstance = null;

function resetCanvas(canvasId) {
    const oldCanvas = document.getElementById(canvasId);
    if (oldCanvas) {
        const newCanvas = document.createElement('canvas');
        newCanvas.id = canvasId;
        newCanvas.width = 400;
        newCanvas.height = 250;
        oldCanvas.parentNode.replaceChild(newCanvas, oldCanvas);
    }
}

function resetChartContainer(containerId, canvasId) {
    const container = document.getElementById(containerId);
    if (container) {
        // Remove all children
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
        // Create and append a new canvas
        const newCanvas = document.createElement('canvas');
        newCanvas.id = canvasId;
        newCanvas.width = 400;
        newCanvas.height = 250;
        newCanvas.style.width = '400px';
        newCanvas.style.height = '250px';
        container.appendChild(newCanvas);
    }
}

function createConsumptionChart() {
    resetChartContainer('consumptionChartContainer', 'consumptionChart');
    const canvas = document.getElementById('consumptionChart');
    canvas.width = 400;
    canvas.height = 250;
    const ctx = canvas.getContext('2d');
    if (window.consumptionChartInstance) {
        window.consumptionChartInstance.destroy();
    }
    const colorList = generateColors(currentAnalysisData.appliance_predictions.length);
    window.consumptionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: currentAnalysisData.appliance_predictions.map(a => a.type),
            datasets: [{
                data: currentAnalysisData.appliance_predictions.map(a => a.consumption),
                backgroundColor: colorList,
                borderColor: '#232323',
                borderWidth: 2
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#ffd600' } },
                title: { display: true, text: 'Monthly Consumption Distribution (Units)' }
            }
        }
    });
}

function createLoadChart() {
    console.log('createLoadChart called, data:', currentAnalysisData.appliance_predictions.map(a => a.load_kw));
    resetChartContainer('loadChartContainer', 'loadChart');
    const canvas = document.getElementById('loadChart');
    canvas.width = 400;
    canvas.height = 250;
    const ctx = canvas.getContext('2d');
    if (window.loadChartInstance) {
        window.loadChartInstance.destroy();
    }
    const colorList = generateColors(currentAnalysisData.appliance_predictions.length);
    window.loadChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: currentAnalysisData.appliance_predictions.map(a => a.type),
            datasets: [{
                label: 'Load (kW)',
                data: currentAnalysisData.appliance_predictions.map(a => a.load_kw),
                backgroundColor: colorList,
                borderColor: '#232323',
                borderWidth: 2
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#ffd600' } },
                title: { display: true, text: 'Connected Load Distribution (kW)' }
            }
        }
    });
}

function updateCharts() {
    try {
        if (window.consumptionChartInstance) window.consumptionChartInstance.destroy();
        if (window.loadChartInstance) window.loadChartInstance.destroy();
        updateHouseholdInfo();
        createConsumptionChart();
        createLoadChart();
    } catch (error) {
        console.error('Error in updateCharts:', error);
    }
}
window.updateCharts = updateCharts;

function updateHouseholdInfo() {
    const section = document.getElementById('householdInfoSection');
    if (!section) return;
    const details = window.userData || {};
    let html = `<div class='household-profile-box'>`;
    html += `<span style='font-size:1.2em; font-weight:600;'><i class='fas fa-home me-2'></i>Household Profile</span><br>`;
    html += `<span>Family Members: <b>${details.totalMembers || '-'}</b></span> &nbsp;|&nbsp; `;
    html += `<span>Male: <b>${details.maleMembers || '-'}</b></span> &nbsp;|&nbsp; `;
    html += `<span>Female: <b>${details.femaleMembers || '-'}</b></span> &nbsp;|&nbsp; `;
    html += `<span>Children: <b>${details.children || '-'}</b></span> &nbsp;|&nbsp; `;
    html += `<span>Type: <b>${details.householdType || '-'}</b></span>`;
    html += `</div>`;
    section.innerHTML = html;
}
window.updateHouseholdInfo = updateHouseholdInfo;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Show loading spinner during calculation
    document.getElementById('predictionForm').addEventListener('submit', function () {
        document.querySelector('.loading-spinner').style.display = 'block';
    });

    // Add validation for family members
    document.querySelectorAll('#totalMembers, #maleMembers, #femaleMembers, #children').forEach(input => {
        input.addEventListener('change', () => {
            const total = document.getElementById('totalMembers');
            const male = document.getElementById('maleMembers');
            const female = document.getElementById('femaleMembers');
            const children = document.getElementById('children');
            const sum = parseInt(male.value || 0) + parseInt(female.value || 0) + parseInt(children.value || 0);
            if (sum > parseInt(total.value)) {
                alert('Sum of male, female and children cannot exceed total members!');
                input.value = '';
            }
        });
    });

    try {
        document.getElementById('predictionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const totalMembers = parseInt(document.getElementById('totalMembers').value);
                const householdType = determineHouseholdType(totalMembers);
                const familyDetails = {
                    totalMembers: document.getElementById('totalMembers').value,
                    maleMembers: document.getElementById('maleMembers').value,
                    femaleMembers: document.getElementById('femaleMembers').value,
                    children: document.getElementById('children').value,
                    householdType: householdType
                };
                const totalCalculated = parseInt(familyDetails.maleMembers) +
                    parseInt(familyDetails.femaleMembers) +
                    parseInt(familyDetails.children);
                if (totalCalculated !== parseInt(familyDetails.totalMembers)) {
                    alert('Total members should equal sum of male, female and children!');
                    return;
                }
                document.querySelector('.loading-spinner').style.display = 'block';
                const appliances = Array.from(document.querySelectorAll('.appliance-card')).map(card => {
                    const usageHours = Array.from(card.querySelectorAll('.usage-hours'))
                        .map(input => parseFloat(input.value));
                    return {
                        type: card.querySelector('select').value,
                        brand: card.querySelectorAll('select')[1].value,
                        model: card.querySelectorAll('select')[2].value,
                        quantity: parseInt(card.querySelectorAll('input')[0].value),
                        avgUsageHours: usageHours.reduce((a, b) => a + b, 0) / usageHours.length
                    };
                })
                // Filter out incomplete appliances
                .filter(appl => appl.type && appl.brand && appl.model && appl.quantity && !isNaN(appl.avgUsageHours));
                const formData = {
                    familyDetails,
                    appliances
                };
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();
                if (result.success) {
                    displayResults(result);
                } else {
                    document.querySelector('.loading-spinner').style.display = 'none';
                    alert(result.error || 'Error making prediction');
                }
            } catch (error) {
                document.querySelector('.loading-spinner').style.display = 'none';
                console.error('Error:', error);
                alert('An error occurred while processing your request.');
            }
        });
    } catch (e) {
        console.error('Could not attach form handler:', e);
    }
});

// ── Download PDF Report ──────────────────────────────────────────────────────
async function downloadReport() {
    const btn = document.getElementById('downloadReportBtn');
    const orig = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating PDF…';
    try {
        const payload = {
            session_id: window.currentSessionId || null,
            family_details: window.userData || {},
            results: window.predictions || {},
            ai_recommendations: window.lastRecommendations || null
        };
        const res = await fetch('/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Report generation failed');
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href = url;
        a.download = `energy_report_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Failed to generate report. Please try again.');
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = orig;
    }
}
window.downloadReport = downloadReport; 