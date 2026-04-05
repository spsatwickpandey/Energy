// recommendations.js
// Handles AJAX call to /get-recommendations, UI updates, and interactivity

// --- DOM event listeners ---
document.addEventListener('DOMContentLoaded', function() {
    const recSection = document.getElementById('recommendation-section');
    const recSpinner = document.getElementById('recommendation-spinner');
    const recContent = document.getElementById('recommendation-content');
    const recForm = document.getElementById('recommendation-form');

    if (recForm) {
        recForm.addEventListener('submit', function(e) {
            e.preventDefault();
            recSpinner.style.display = 'block';
            recContent.innerHTML = '';
            // Gather user data and predictions from form or JS state
            const userData = window.userData || {};
            const predictions = window.predictions || {};
            
            // Debug logging
            console.log('Sending recommendations request:', { userData, predictions });
            
            if (!userData || Object.keys(userData).length === 0) {
                recSpinner.style.display = 'none';
                recContent.innerHTML = '<div class="alert alert-warning">Please calculate your energy consumption first before getting recommendations.</div>';
                return;
            }
            
            if (!predictions || !predictions.appliance_breakdown || predictions.appliance_breakdown.length === 0) {
                recSpinner.style.display = 'none';
                recContent.innerHTML = '<div class="alert alert-warning">No appliance data available. Please calculate your energy consumption first.</div>';
                return;
            }
            
            fetch('/get-recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_data: userData,
                    predictions: predictions,
                    session_id: window.currentSessionId || null
                })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                recSpinner.style.display = 'none';
                window.lastRecommendations = data;  // cache for PDF report
                console.log('Received recommendations response:', data);
                renderRecommendations(data);
            })
            .catch(err => {
                recSpinner.style.display = 'none';
                console.error('Error fetching recommendations:', err);
                recContent.innerHTML = '<div class="alert alert-danger">Failed to load recommendations. Please try again.</div>';
            });
        });
    }

    function renderRecommendations(data) {
        const recContent = document.getElementById('recommendation-content');
        
        // Check for error responses first
        if (data && data.error) {
            const errorMsg = data.personalized_tips && data.personalized_tips.length > 0 
                ? data.personalized_tips[0].action 
                : data.error || 'Sorry, we could not generate recommendations due to a data or server error.';
            recContent.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>${errorMsg}</div>`;
            console.error('Recommendations error:', data.error);
            return;
        }
        
        // If only personalized_tips and it's a long string, show as a visible tip
        if (data && data.personalized_tips && Array.isArray(data.personalized_tips) && data.personalized_tips.length === 1) {
            const tip = data.personalized_tips[0];
            const tipText = typeof tip === 'string' ? tip : (tip.action || '');
            // Check if it's an error message (contains "error" or "sorry")
            if (tipText.toLowerCase().includes('error') || tipText.toLowerCase().includes('sorry')) {
                recContent.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>${tipText}</div>`;
                return;
            }
            // If it's a long string, show as formatted AI response
            if (typeof tipText === 'string' && tipText.length > 100) {
                recContent.innerHTML = `<div class="recommendation-card mb-3"><div class="recommendation-header d-flex align-items-center"><i class="fas fa-robot me-2"></i><h5 class="mb-0">AI Recommendation</h5></div><div class="recommendation-body"><pre style='white-space:pre-wrap; background: #232323; color: #ffd600; border-radius: 8px; padding: 1em; font-size: 1em;'>${tipText}</pre></div></div>`;
                return;
            }
        }
        
        if (!data || (!data.priority_actions && !data.appliance_replacements && !data.usage_optimization && !data.long_term_investments && !data.personalized_tips && !data.behavioral_changes)) {
            recContent.innerHTML = '<div class="alert alert-warning">No recommendations available.</div>';
            return;
        }
        let html = '';
        // --- AI Explanation (if present as .explanation or .ai_explanation or .explanation_text) ---
        if (data.explanation || data.ai_explanation || data.explanation_text) {
            const explanation = data.explanation || data.ai_explanation || data.explanation_text;
            html += `<div class="ai-explanation-box">${explanation}</div>`;
        } else if (data.raw && typeof data.raw === 'string' && data.raw.length < 600) {
            html += `<div class="ai-explanation-box">${data.raw}</div>`;
        }
        html += renderCategory('Quick Wins', data.priority_actions, 'priority_actions', 'fa-bolt', 'recommendation-priority-high');
        html += renderCategory('Appliance Replacements', data.appliance_replacements, 'appliance_replacements', 'fa-sync-alt', 'recommendation-priority-medium');
        html += renderCategory('Usage Optimization', data.usage_optimization, 'usage_optimization', 'fa-sliders-h', 'recommendation-priority-low');
        html += renderCategory('Long-term Investments', data.long_term_investments, 'long_term_investments', 'fa-piggy-bank', 'recommendation-priority-longterm');
        html += renderCategory('Personalized Tips', data.personalized_tips, 'personalized_tips', 'fa-lightbulb', 'recommendation-priority-personal');
        recContent.innerHTML = html;
    }

    function renderCategory(title, items, key, icon, badgeClass) {
        if (!items || !items.length) return '';
        let html = `<div class="recommendation-card mb-3"><div class="recommendation-header d-flex align-items-center"><i class="fas ${icon} me-2"></i><h5 class="mb-0">${title}</h5></div><div class="recommendation-body">`;
        items.forEach((item, idx) => {
            html += `<div class="mb-3 p-2 rounded" style="background: #232323; border-left: 4px solid #ffd600;">
            <strong>${item.action || item.appliance || item.change || item.investment || ''}</strong><br>`;
            if (item.reason) html += `<span>${item.reason}</span><br>`;
            if (item.potential_savings) html += `<span class="badge bg-success">Savings: ${item.potential_savings}</span> `;
            if (item.urgency) html += `<span class="badge ${badgeClass}">${item.urgency}</span> `;
            if (item.payback_period) html += `<span class="badge bg-info">Payback: ${item.payback_period}</span> `;
            if (item.savings) html += `<span class="badge bg-success">${item.savings}</span> `;
            if (item.tips) html += `<div><em>Tip: ${item.tips}</em></div>`;
            if (item.impact) html += `<span class="badge bg-primary">Impact: ${item.impact}</span> `;
            if (item.difficulty) html += `<span class="badge bg-secondary">Difficulty: ${item.difficulty}</span> `;
            if (item.cost) html += `<span class="badge bg-warning">Cost: ${item.cost}</span> `;
            if (item.annual_savings) html += `<span class="badge bg-success">Annual Savings: ${item.annual_savings}</span> `;
            if (item.roi_period) html += `<span class="badge bg-info">ROI: ${item.roi_period}</span> `;
            html += `<button class="btn btn-sm btn-outline-success ms-2 mark-done-btn" data-key="${key}" data-idx="${idx}"><i class="fas fa-check"></i> Mark as Done</button>`;
            html += `</div>`;
        });
        html += '</div></div>';
        return html;
    }

    function urgencyClass(urgency) {
        if (!urgency) return '';
        if (urgency.toLowerCase() === 'high') return 'recommendation-priority-high';
        if (urgency.toLowerCase() === 'medium') return 'recommendation-priority-medium';
        if (urgency.toLowerCase() === 'low') return 'recommendation-priority-low';
        return '';
    }

    // Mark as Done handler
    recContent.addEventListener('click', function(e) {
        if (e.target.classList.contains('mark-done-btn') || e.target.closest('.mark-done-btn')) {
            const btn = e.target.closest('.mark-done-btn');
            btn.parentElement.classList.add('recommendation-done');
            btn.disabled = true;
        }
    });
});

// --- Global functions (must be available immediately) ---
window.showDetailedAnalysis = function() {
    const analysisSection = document.getElementById('analysisSection');
    analysisSection.style.display = analysisSection.style.display === 'none' ? 'block' : 'none';
    if (analysisSection.style.display === 'block') {
        if (window.updateCharts) window.updateCharts();
        // Only trigger recommendations, do not render charts here
        const recContent = document.getElementById('recommendation-content');
        if (recContent && recContent.innerHTML.trim() === '') {
            document.getElementById('recommendation-form').dispatchEvent(new Event('submit'));
        }
    }
};

window.setAnalysisData = function(predictionResults) {
    // Set global variables for charts (optional, but not used for rendering anymore)
    window.applianceLabels = (predictionResults.appliance_breakdown || []).map(a => a.type || a.appliance_type || '');
    window.applianceConsumptions = (predictionResults.appliance_breakdown || []).map(a => a.consumption || 0);
    window.applianceLoads = (predictionResults.appliance_breakdown || []).map(a => a.load_kw || 0);
}; 
