// CATDAMS Analytics JavaScript - Phase 1, Step 1.4
// Safe implementation that doesn't interfere with existing dashboard functionality

// Analytics configuration
const ANALYTICS_CONFIG = {
    updateInterval: 5000, // 5 seconds
    chartColors: {
        primary: '#2563eb',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
        secondary: '#64748b'
    },
    apiEndpoints: {
        health: '/api/analytics/health',
        sessionsSummary: '/api/analytics/sessions/summary',
        tdcPerformance: '/api/analytics/tdc/performance',
        threatsPatterns: '/api/analytics/threats/patterns',
        realtimeCurrent: '/api/analytics/realtime/current',
        status: '/api/analytics/status',
        trendsPredictions: '/api/analytics/predictions/trends',
        anomalyDetection: '/api/analytics/predictions/anomalies'
    }
};

// Analytics state management
let analyticsState = {
    isEnabled: false,
    isInitialized: false,
    updateTimer: null,
    charts: {},
    lastUpdate: null
};

// Chart instances
let threatLevelChart = null;
let sourceChart = null;

// Initialize analytics dashboard
function initializeAnalytics() {
    console.log('[ANALYTICS] Initializing analytics dashboard...');
    
    try {
        // Initialize charts
        initializeCharts();
        
        // Load initial data
        loadAnalyticsData();
        
        // Set up real-time updates
        setupRealTimeUpdates();
        
        // Update status
        updateAnalyticsStatus('Analytics dashboard initialized successfully');
        
        analyticsState.isInitialized = true;
        console.log('[ANALYTICS] Analytics dashboard initialized successfully');
        
    } catch (error) {
        console.error('[ANALYTICS] Error initializing analytics:', error);
        updateAnalyticsStatus('Error initializing analytics: ' + error.message, 'error');
    }
}

// Initialize charts safely
function initializeCharts() {
    console.log('[ANALYTICS] Initializing charts...');
    
    try {
        // Threat Level Chart
        const threatLevelCtx = document.getElementById('threatLevelChart');
        if (threatLevelCtx) {
            threatLevelChart = new Chart(threatLevelCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            ANALYTICS_CONFIG.chartColors.danger,
                            ANALYTICS_CONFIG.chartColors.warning,
                            ANALYTICS_CONFIG.chartColors.info,
                            ANALYTICS_CONFIG.chartColors.success
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }
        
        // Source Chart
        const sourceCtx = document.getElementById('sourceChart');
        if (sourceCtx) {
            sourceChart = new Chart(sourceCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Events by Source',
                        data: [],
                        backgroundColor: ANALYTICS_CONFIG.chartColors.primary,
                        borderColor: ANALYTICS_CONFIG.chartColors.primary,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        
        console.log('[ANALYTICS] Charts initialized successfully');
        
    } catch (error) {
        console.error('[ANALYTICS] Error initializing charts:', error);
    }
}

// Load analytics data safely using real API endpoints
async function loadAnalyticsData() {
    console.log('[ANALYTICS] Loading analytics data from real API...');
    
    try {
        // Load session summary (main analytics data)
        const sessionsResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.sessionsSummary);
        if (sessionsResponse.ok) {
            const sessionsData = await sessionsResponse.json();
            updateMetricsDisplay(sessionsData);
            updateCharts(sessionsData);
        } else {
            console.warn('[ANALYTICS] Could not load sessions data, using fallback data');
            updateMetricsDisplay(getFallbackStats());
        }
        
        // Load threat patterns for enhanced charts
        const threatsResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.threatsPatterns);
        if (threatsResponse.ok) {
            const threatsData = await threatsResponse.json();
            updateThreatCharts(threatsData);
        }
        
        // Load real-time current activity
        const realtimeResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.realtimeCurrent);
        if (realtimeResponse.ok) {
            const realtimeData = await realtimeResponse.json();
            updateRealtimeDisplay(realtimeData);
        }
        
        // Load status information
        const statusResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.status);
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            updateStatusDisplay(statusData);
        }
        
        // Load ML predictions and trends
        const trendsResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.trendsPredictions);
        if (trendsResponse.ok) {
            const trendsData = await trendsResponse.json();
            updateTrendsDisplay(trendsData);
        }
        
        // Load anomaly detection
        const anomaliesResponse = await fetch(ANALYTICS_CONFIG.apiEndpoints.anomalyDetection);
        if (anomaliesResponse.ok) {
            const anomaliesData = await anomaliesResponse.json();
            updateAnomaliesDisplay(anomaliesData);
        }
        
        analyticsState.lastUpdate = new Date();
        
    } catch (error) {
        console.error('[ANALYTICS] Error loading analytics data:', error);
        updateAnalyticsStatus('Error loading data: ' + error.message, 'warning');
        
        // Use fallback data
        updateMetricsDisplay(getFallbackStats());
    }
}

// Update metrics display safely with real API data
function updateMetricsDisplay(data) {
    try {
        // Extract data from the new API structure
        const sessionAnalysis = data.session_analysis || {};
        const threatAnalysis = data.threat_analysis || {};
        
        // Update key metrics
        const totalEvents = document.getElementById('totalEvents');
        const uniqueSessions = document.getElementById('uniqueSessions');
        const aiInteractions = document.getElementById('aiInteractions');
        const avgMessageLength = document.getElementById('avgMessageLength');
        
        if (totalEvents) totalEvents.textContent = sessionAnalysis.total_events || 0;
        if (uniqueSessions) uniqueSessions.textContent = sessionAnalysis.total_sessions || 0;
        if (aiInteractions) aiInteractions.textContent = threatAnalysis.total_threats || 0;
        if (avgMessageLength) avgMessageLength.textContent = Math.round(sessionAnalysis.avg_events_per_session || 0);
        
        // Update analytics table with real data
        updateAnalyticsTable(data);
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating metrics display:', error);
    }
}

// Update threat charts with real API data
function updateThreatCharts(threatsData) {
    try {
        const escalationDistribution = threatsData.escalation_distribution || {};
        const threatScoreStats = threatsData.threat_score_stats || {};
        
        // Update threat level chart with real escalation data
        if (threatLevelChart) {
            const labels = Object.keys(escalationDistribution);
            const data = Object.values(escalationDistribution);
            
            threatLevelChart.data.labels = labels;
            threatLevelChart.data.datasets[0].data = data;
            threatLevelChart.update();
        }
        
        // Update threat score statistics
        const avgScore = document.getElementById('avgThreatScore');
        if (avgScore) avgScore.textContent = Math.round(threatScoreStats.avg_score || 0);
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating threat charts:', error);
    }
}

// Update real-time display with current activity
function updateRealtimeDisplay(realtimeData) {
    try {
        const currentActivity = realtimeData.current_activity || {};
        
        // Update active sessions count
        const activeSessions = document.getElementById('activeSessions');
        if (activeSessions) activeSessions.textContent = currentActivity.active_sessions || 0;
        
        // Update recent events count
        const recentEvents = document.getElementById('recentEvents');
        if (recentEvents) recentEvents.textContent = (currentActivity.recent_events || []).length;
        
        // Update recent threats count
        const recentThreats = document.getElementById('recentThreats');
        if (recentThreats) recentThreats.textContent = (currentActivity.recent_threats || []).length;
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating real-time display:', error);
    }
}

// Update status display with API status
function updateStatusDisplay(statusData) {
    try {
        const status = statusData.status || 'unknown';
        const dataAvailability = statusData.data_availability || {};
        
        // Update status indicator
        const statusIndicator = document.getElementById('analyticsStatus');
        if (statusIndicator) {
            statusIndicator.textContent = status === 'operational' ? 'Operational' : 'Error';
            statusIndicator.className = status === 'operational' ? 'fw-bold text-success' : 'fw-bold text-danger';
        }
        
        // Update data availability info
        const totalRecords = document.getElementById('totalRecords');
        if (totalRecords) totalRecords.textContent = dataAvailability.total_telemetry_records || 0;
        
            } catch (error) {
            console.error('[ANALYTICS] Error updating status display:', error);
        }
    }

// Update trends display with ML predictions
function updateTrendsDisplay(trendsData) {
    try {
        const currentMetrics = trendsData.current_metrics || {};
        const predictedMetrics = trendsData.predicted_metrics || {};
        const trends = trendsData.trends || {};
        const riskAssessment = trendsData.risk_assessment || {};
        
        // Update trend indicators
        const trendDirection = document.getElementById('trendDirection');
        if (trendDirection) {
            trendDirection.textContent = trends.trend_direction || 'stable';
            trendDirection.className = trends.trend_direction === 'increasing' ? 'text-danger' : 'text-success';
        }
        
        // Update risk level
        const riskLevel = document.getElementById('riskLevel');
        if (riskLevel) {
            riskLevel.textContent = riskAssessment.level || 'UNKNOWN';
            const riskClass = riskAssessment.level === 'HIGH' ? 'text-danger' : 
                             riskAssessment.level === 'MEDIUM' ? 'text-warning' : 'text-success';
            riskLevel.className = riskClass;
        }
        
        // Update prediction metrics
        const predictedThreats = document.getElementById('predictedThreats');
        if (predictedThreats) predictedThreats.textContent = Math.round(predictedMetrics.daily_threats || 0);
        
        const predictedScore = document.getElementById('predictedScore');
        if (predictedScore) predictedScore.textContent = Math.round(predictedMetrics.avg_threat_score || 0);
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating trends display:', error);
    }
}

// Update anomalies display
function updateAnomaliesDisplay(anomaliesData) {
    try {
        const anomalies = anomaliesData.anomalies || [];
        const statistics = anomaliesData.statistics || {};
        
        // Update anomaly count
        const anomalyCount = document.getElementById('anomalyCount');
        if (anomalyCount) anomalyCount.textContent = statistics.anomalies_detected || 0;
        
        // Update anomaly list if container exists
        const anomalyList = document.getElementById('anomalyList');
        if (anomalyList && anomalies.length > 0) {
            anomalyList.innerHTML = anomalies.slice(0, 5).map(anomaly => `
                <div class="alert alert-${anomaly.severity === 'high' ? 'danger' : 'warning'} alert-sm">
                    <small>
                        <strong>${anomaly.anomaly_type}</strong> - 
                        Score: ${anomaly.threat_score} - 
                        ${new Date(anomaly.timestamp).toLocaleString()}
                    </small>
                </div>
            `).join('');
        }
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating anomalies display:', error);
    }
}

// Update charts safely with real API data
function updateCharts(data) {
    try {
        // Update source chart with session data
        if (sourceChart) {
            // For now, use session analysis data for source chart
            // This can be enhanced later with more detailed source data
            const sessionAnalysis = data.session_analysis || {};
            const labels = ['Sessions', 'Events', 'Threats'];
            const values = [
                sessionAnalysis.total_sessions || 0,
                sessionAnalysis.total_events || 0,
                (data.threat_analysis || {}).total_threats || 0
            ];
            
            sourceChart.data.labels = labels;
            sourceChart.data.datasets[0].data = values;
            sourceChart.update('none');
        }
        
        // Note: Threat level chart is now updated by updateThreatCharts function
        // which is called separately with threat patterns data
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating charts:', error);
    }
}

// Update analytics table safely with real API data
function updateAnalyticsTable(data) {
    try {
        const tableBody = document.getElementById('analyticsTableBody');
        if (!tableBody) return;
        
        const sessionAnalysis = data.session_analysis || {};
        const threatAnalysis = data.threat_analysis || {};
        
        const rows = [
            ['Total Sessions', sessionAnalysis.total_sessions || 0, 'info'],
            ['Total Events', sessionAnalysis.total_events || 0, 'success'],
            ['Total Threats', threatAnalysis.total_threats || 0, 'danger'],
            ['Avg Events/Session', Math.round(sessionAnalysis.avg_events_per_session || 0), 'secondary'],
            ['Last Updated', new Date().toLocaleTimeString(), 'primary']
        ];
        
        tableBody.innerHTML = rows.map(([metric, value, status]) => `
            <tr>
                <td>${metric}</td>
                <td>${value}</td>
                <td><span class="badge bg-${status}">Active</span></td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating analytics table:', error);
    }
}

// Update performance display safely
function updatePerformanceDisplay(performance) {
    try {
        const perfContainer = document.getElementById('performanceMetrics');
        if (!perfContainer) return;
        
        perfContainer.innerHTML = `
            <div class="mb-3">
                <strong>Analytics Engine:</strong> 
                <span class="analytics-status ${performance.analytics_enabled ? 'online' : 'offline'}">
                    ${performance.analytics_enabled ? 'Online' : 'Offline'}
                </span>
            </div>
            <div class="mb-3">
                <strong>Total Metrics:</strong> ${performance.total_metrics_collected || 0}
            </div>
            <div class="mb-3">
                <strong>Memory Usage:</strong> ${(performance.memory_usage_estimate || 0).toFixed(2)} MB
            </div>
            <div class="mb-3">
                <strong>Status:</strong> 
                <span class="badge bg-${performance.status === 'healthy' ? 'success' : 'warning'}">
                    ${performance.status || 'Unknown'}
                </span>
            </div>
        `;
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating performance display:', error);
    }
}

// Update analytics status safely
function updateAnalyticsStatus(message, type = 'info') {
    try {
        const statusText = document.getElementById('analyticsStatusText');
        const alert = document.getElementById('analyticsAlert');
        
        if (statusText) {
            statusText.textContent = message;
        }
        
        if (alert) {
            // Remove existing classes
            alert.className = 'alert alert-dismissible fade show';
            
            // Add appropriate class
            if (type === 'error') {
                alert.classList.add('alert-danger');
            } else if (type === 'warning') {
                alert.classList.add('alert-warning');
            } else if (type === 'success') {
                alert.classList.add('alert-success');
            } else {
                alert.classList.add('alert-info');
            }
        }
        
    } catch (error) {
        console.error('[ANALYTICS] Error updating status:', error);
    }
}

// Setup real-time updates safely
function setupRealTimeUpdates() {
    const realTimeToggle = document.getElementById('realTimeUpdates');
    if (realTimeToggle) {
        realTimeToggle.addEventListener('change', function() {
            if (this.checked) {
                startRealTimeUpdates();
            } else {
                stopRealTimeUpdates();
            }
        });
        
        // Start if checked by default
        if (realTimeToggle.checked) {
            startRealTimeUpdates();
        }
    }
}

// Start real-time updates safely
function startRealTimeUpdates() {
    if (analyticsState.updateTimer) {
        clearInterval(analyticsState.updateTimer);
    }
    
    analyticsState.updateTimer = setInterval(() => {
        loadAnalyticsData();
    }, ANALYTICS_CONFIG.updateInterval);
    
    console.log('[ANALYTICS] Real-time updates started');
}

// Stop real-time updates safely
function stopRealTimeUpdates() {
    if (analyticsState.updateTimer) {
        clearInterval(analyticsState.updateTimer);
        analyticsState.updateTimer = null;
    }
    
    console.log('[ANALYTICS] Real-time updates stopped');
}

// Analytics control functions - using health check instead of enable/disable endpoints
async function enableAnalytics() {
    try {
        // Check if analytics API is healthy
        const response = await fetch(ANALYTICS_CONFIG.apiEndpoints.health);
        
        if (response.ok) {
            analyticsState.isEnabled = true;
            updateAnalyticsStatus('Analytics API is operational and enabled', 'success');
            loadAnalyticsData();
        } else {
            updateAnalyticsStatus('Analytics API is not available', 'error');
        }
    } catch (error) {
        console.error('[ANALYTICS] Error checking analytics health:', error);
        updateAnalyticsStatus('Error connecting to analytics API: ' + error.message, 'error');
    }
}

async function disableAnalytics() {
    try {
        analyticsState.isEnabled = false;
        updateAnalyticsStatus('Analytics disabled (API remains active)', 'warning');
        stopRealTimeUpdates();
    } catch (error) {
        console.error('[ANALYTICS] Error disabling analytics:', error);
        updateAnalyticsStatus('Error disabling analytics: ' + error.message, 'error');
    }
}

function refreshAnalytics() {
    console.log('[ANALYTICS] Refreshing analytics data...');
    loadAnalyticsData();
    updateAnalyticsStatus('Analytics data refreshed', 'success');
}

function exportAnalytics() {
    console.log('[ANALYTICS] Exporting analytics data...');
    
    // Create export data
    const exportData = {
        timestamp: new Date().toISOString(),
        analytics_state: analyticsState,
        last_update: analyticsState.lastUpdate
    };
    
    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `catdams-analytics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    updateAnalyticsStatus('Analytics data exported successfully', 'success');
}

// Fallback data for when API is not available
function getFallbackStats() {
    return {
        session_analysis: {
            total_sessions: 0,
            total_events: 0,
            avg_events_per_session: 0,
            session_duration_stats: {
                avg_duration_minutes: 0,
                max_duration_minutes: 0
            }
        },
        threat_analysis: {
            total_threats: 0,
            threat_distribution: {},
            avg_threat_score: 0
        },
        last_updated: new Date().toISOString()
    };
}

// Theme toggle function (safe wrapper)
function toggleDarkTheme() {
    try {
        // Check if main dashboard theme toggle exists
        if (typeof window.toggleDarkTheme === 'function') {
            window.toggleDarkTheme();
        } else {
            // Fallback theme toggle
            document.body.classList.toggle('dark-theme');
        }
    } catch (error) {
        console.error('[ANALYTICS] Error toggling theme:', error);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[ANALYTICS] DOM loaded, initializing analytics...');
    initializeAnalytics();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopRealTimeUpdates();
    console.log('[ANALYTICS] Analytics cleanup completed');
});

// Export functions for global access
window.analyticsFunctions = {
    enableAnalytics,
    disableAnalytics,
    refreshAnalytics,
    exportAnalytics,
    toggleDarkTheme
};

console.log('[ANALYTICS] Analytics JavaScript loaded successfully');
