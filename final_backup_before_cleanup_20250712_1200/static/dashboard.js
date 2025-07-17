// CATDAMS Combined Dashboard JavaScript

// Global variables
let websocket = null;
let charts = {};
let currentSessionId = null;
let threatData = [];
let sessionData = [];
let tdcModules = {};
let filterPresets = {};
let searchScope = 'all';
let viewMode = 'cards';

// TDC Module configurations for 11 modules
const TDC_MODULES = {
    'TDC-AI1': {
        name: 'User Susceptibility Analysis',
        description: 'Risk Analysis - Overall threat assessment combining user and AI analysis',
        icon: 'bi-shield-exclamation',
        color: 'primary'
    },
    'TDC-AI2': {
        name: 'AI Manipulation Tactics',
        description: 'AI Response - Detects manipulative AI responses using Azure OpenAI',
        icon: 'bi-robot',
        color: 'danger'
    },
    'TDC-AI3': {
        name: 'Sentiment Analysis',
        description: 'User Vulnerability - Temporal analysis of user susceptibility across timeframes',
        icon: 'bi-heart-pulse',
        color: 'info'
    },
    'TDC-AI4': {
        name: 'Prompt Attack Detection',
        description: 'Deep Synthesis - Comprehensive threat synthesis from all modules',
        icon: 'bi-bug',
        color: 'warning'
    },
    'TDC-AI5': {
        name: 'Multimodal Threat Detection',
        description: 'LLM Influence - Detects subtle AI manipulation and conditioning',
        icon: 'bi-camera-video',
        color: 'secondary'
    },
    'TDC-AI6': {
        name: 'Long-term Influence Conditioning',
        description: 'Pattern Classification - Sentiment and pattern analysis for both user and AI',
        icon: 'bi-clock-history',
        color: 'dark'
    },
    'TDC-AI7': {
        name: 'Agentic Threats Detection',
        description: 'Explainability - Generates human-readable explanations and evidence',
        icon: 'bi-cpu',
        color: 'success'
    },
    'TDC-AI8': {
        name: 'Synthesis & Integration',
        description: 'Synthesis - Final synthesis and actionable recommendations',
        icon: 'bi-diagram-3',
        color: 'primary'
    },
    'TDC-AI9': {
        name: 'Explainability & Evidence',
        description: 'Explainability Evidence - Detailed evidence and reasoning',
        icon: 'bi-search',
        color: 'info'
    },
    'TDC-AI10': {
        name: 'Psychological Manipulation',
        description: 'Psychological Manipulation - Cognitive bias and psychological tactics',
        icon: 'bi-brain',
        color: 'warning'
    },
    'TDC-AI11': {
        name: 'Intervention Response',
        description: 'Intervention Response - Recommended actions and countermeasures',
        icon: 'bi-shield-check',
        color: 'success'
    }
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    initializeWebSocket();
    initializeCharts();
    // initializeTDCModules(); // Removed - now called from initializeDashboard
    initializeTooltips();
    initializeEventListeners();
    loadInitialData();
});

// Initialize dashboard components
function initializeDashboard() {
    console.log('Initializing CATDAMS Combined Dashboard...');
    
    // Set initial theme
    const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Initialize TDC modules with a slight delay to ensure DOM is ready
    setTimeout(() => {
        initializeTDCModules();
    }, 100);
}

// Initialize WebSocket connection
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function(event) {
            console.log('WebSocket connected');
            updateConnectionStatus(true);
        };
        
        websocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        websocket.onclose = function(event) {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);
            // Attempt to reconnect after 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
        
        websocket.onerror = function(error) {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        updateConnectionStatus(false);
    }
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    console.log('Received WebSocket message:', data);
    
    // Check if this is a heartbeat response
    if (data.type === 'heartbeat_response') {
        console.log('Heartbeat response received');
        return;
    }
    
    // The data from backend doesn't have a 'type' field - it's the full dashboard data
    // Handle it as a threat event with all the data
    if (data.session_id || data.timestamp) {
        console.log('Processing dashboard data:', data);
        
        // Update threat events
        handleThreatEvent(data);
        
        // Update TDC modules if they have actual analysis data
        const tdcModulesData = {};
        let hasTdcData = false;
        
        // Check each TDC module for actual data
        const tdcModules = [
            'tdc_ai1_user_susceptibility',
            'tdc_ai2_ai_manipulation_tactics', 
            'tdc_ai3_sentiment_analysis',
            'tdc_ai4_prompt_attack_detection',
            'tdc_ai5_multimodal_threat',
            'tdc_ai6_longterm_influence_conditioning',
            'tdc_ai7_agentic_threats',
            'tdc_ai8_synthesis_integration',
            'tdc_ai9_explainability_evidence',
            'tdc_ai10_psychological_manipulation',
            'tdc_ai11_intervention_response'
        ];
        
        tdcModules.forEach((moduleKey, index) => {
            const moduleId = `TDC-AI${index + 1}`;
            const moduleData = data[moduleKey];
            
            if (moduleData && Object.keys(moduleData).length > 0) {
                // Module has actual data - set to online
                tdcModulesData[moduleId] = {
                    status: 'online',
                    score: moduleData.score || moduleData.threat_score || 0,
                    threats: moduleData.threats || moduleData.threat_count || 0,
                    details: moduleData.analysis || moduleData.description || 'Analysis complete'
                };
                hasTdcData = true;
                console.log(`${moduleId} has data - setting to online`);
            } else {
                // Module has no data - keep offline
                tdcModulesData[moduleId] = {
                    status: 'offline',
                    score: 0,
                    threats: 0,
                    details: 'No analysis data available'
                };
            }
        });
        
        if (hasTdcData) {
            console.log('Updating TDC modules with real data:', tdcModulesData);
            handleTDCUpdate(tdcModulesData);
        }
        
        // Update session info
        if (data.session_id) {
            handleSessionUpdate({
                current_session: data.session_id,
                active_sessions: 1
            });
        }
        
        // Update chat messages if available
        if (data.message || data.raw_user || data.raw_ai) {
            handleChatMessage({
                sender: data.raw_user ? 'user' : 'ai',
                content: data.raw_user || data.raw_ai || data.message,
                timestamp: data.timestamp,
                session_id: data.session_id,
                threat_detected: data.severity && data.severity !== 'Low'
            });
        }
        
        // Update system status
        handleSystemStatus({
            websocket_connected: true,
            pending_alerts: data.severity && data.severity !== 'Low' ? 1 : 0
        });
    } else {
        console.log('Unknown message format:', data);
    }
}

// Initialize charts
function initializeCharts() {
    // Threat Level Distribution Chart
    const threatLevelCtx = document.getElementById('threatLevelChart');
    if (threatLevelCtx) {
        charts.threatLevel = new Chart(threatLevelCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#dc3545',
                        '#ffc107',
                        '#17a2b8',
                        '#28a745'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
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
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Threat Vector Chart
    const threatVectorCtx = document.getElementById('threatVectorChart');
    if (threatVectorCtx) {
        charts.threatVector = new Chart(threatVectorCtx, {
            type: 'bar',
            data: {
                labels: ['AI Manipulation', 'Elicitation', 'Insider Threat', 'Sentiment Manipulation', 'Grooming'],
                datasets: [{
                    label: 'Threat Count',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(108, 117, 125, 0.8)',
                        'rgba(40, 167, 69, 0.8)'
                    ],
                    borderColor: [
                        '#dc3545',
                        '#ffc107',
                        '#17a2b8',
                        '#6c757d',
                        '#28a745'
                    ],
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
    
    // Analytics Chart
    const analyticsCtx = document.getElementById('analyticsChart');
    if (analyticsCtx) {
        charts.analytics = new Chart(analyticsCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Threat Score',
                    data: [],
                    borderColor: '#0077b6',
                    backgroundColor: 'rgba(0, 119, 182, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
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
}

// Initialize TDC modules
function initializeTDCModules() {
    console.log('Initializing TDC modules...');
    const container = document.getElementById('tdcModulesContainer');
    const grid = document.getElementById('tdcModulesGrid');
    
    if (container) {
        console.log('Creating TDC modules for sidebar container...');
        Object.keys(TDC_MODULES).forEach(moduleId => {
            const module = TDC_MODULES[moduleId];
            const moduleElement = createTDCModuleElement(moduleId, module);
            container.appendChild(moduleElement);
        });
    } else {
        console.warn('TDC modules container not found');
    }
    
    if (grid) {
        console.log('Creating TDC modules for grid view...');
        Object.keys(TDC_MODULES).forEach(moduleId => {
            const module = TDC_MODULES[moduleId];
            const moduleCard = createTDCModuleCard(moduleId, module);
            grid.appendChild(moduleCard);
        });
    } else {
        console.warn('TDC modules grid not found');
    }
    
    // TDC modules will remain offline until they receive actual data
    console.log('TDC modules initialized - they will show as online when they receive data');
}

// Create TDC module element for sidebar
function createTDCModuleElement(moduleId, module) {
    const div = document.createElement('div');
    div.className = 'tdc-module';
    div.id = `tdc-module-${moduleId}`;
    div.setAttribute('data-module-id', moduleId);
    div.style.cursor = 'pointer';
    
    div.innerHTML = `
        <div class="tdc-module-header">
            <div class="tdc-module-info">
                <h6 class="tdc-module-title">${module.name}</h6>
                <small class="text-muted">${module.description}</small>
            </div>
            <span class="tdc-module-status offline">Offline</span>
        </div>
        <div class="tdc-module-content d-none">
            <div class="tdc-module-metrics">
                <div class="metric-item">
                    <div class="metric-value" id="${moduleId}-score">0</div>
                    <div class="metric-label">Score</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="${moduleId}-threats">0</div>
                    <div class="metric-label">Threats</div>
                </div>
            </div>
            <div class="tdc-module-details" id="${moduleId}-details">
                <small class="text-muted">No analysis data available</small>
            </div>
        </div>
    `;
    
    div.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleTDCModule(moduleId);
    });
    return div;
}

// Create TDC module card for grid view
function createTDCModuleCard(moduleId, module) {
    const div = document.createElement('div');
    div.className = 'col-md-6 col-lg-4';
    
    div.innerHTML = `
        <div class="tdc-module-card" id="tdc-card-${moduleId}" data-module-id="${moduleId}" style="cursor: pointer;">
            <div class="tdc-module-header">
                <div class="tdc-module-icon offline">
                    <i class="bi ${module.icon}"></i>
                </div>
                <div class="tdc-module-info">
                    <h6 class="tdc-module-name">${module.name}</h6>
                    <p class="tdc-module-description">${module.description}</p>
                </div>
            </div>
            <div class="tdc-module-content d-none">
                <div class="tdc-module-metrics">
                    <div class="metric-item">
                        <div class="metric-value" id="${moduleId}-card-score">0</div>
                        <div class="metric-label">Score</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="${moduleId}-card-threats">0</div>
                        <div class="metric-label">Threats</div>
                    </div>
                </div>
                <div class="tdc-module-details" id="${moduleId}-card-details">
                    <small class="text-muted">No analysis data available</small>
                </div>
            </div>
        </div>
    `;
    
    const card = div.querySelector('.tdc-module-card');
    card.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleTDCModuleCard(moduleId);
    });
    return div;
}

// Toggle TDC module expansion
function toggleTDCModule(moduleId) {
    console.log(`Toggling TDC module: ${moduleId}`);
    const module = document.getElementById(`tdc-module-${moduleId}`);
    if (!module) {
        console.warn(`TDC module ${moduleId} not found`);
        return;
    }
    
    const content = module.querySelector('.tdc-module-content');
    
    if (content.classList.contains('d-none')) {
        content.classList.remove('d-none');
        module.classList.add('active');
        console.log(`Expanded module: ${moduleId}`);
    } else {
        content.classList.add('d-none');
        module.classList.remove('active');
        console.log(`Collapsed module: ${moduleId}`);
    }
}

// Toggle TDC module card expansion
function toggleTDCModuleCard(moduleId) {
    console.log(`Toggling TDC module card: ${moduleId}`);
    const card = document.getElementById(`tdc-card-${moduleId}`);
    if (!card) {
        console.warn(`TDC module card ${moduleId} not found`);
        return;
    }
    
    const content = card.querySelector('.tdc-module-content');
    
    if (content.classList.contains('d-none')) {
        content.classList.remove('d-none');
        card.classList.add('expanded');
        console.log(`Expanded module card: ${moduleId}`);
    } else {
        content.classList.add('d-none');
        card.classList.remove('expanded');
        console.log(`Collapsed module card: ${moduleId}`);
    }
}

// Expand all TDC modules
function expandAllModules() {
    document.querySelectorAll('.tdc-module').forEach(module => {
        const content = module.querySelector('.tdc-module-content');
        content.classList.remove('d-none');
        module.classList.add('active');
    });
    
    document.querySelectorAll('.tdc-module-card').forEach(card => {
        const content = card.querySelector('.tdc-module-content');
        content.classList.remove('d-none');
        card.classList.add('expanded');
    });
}

// Collapse all TDC modules
function collapseAllModules() {
    document.querySelectorAll('.tdc-module').forEach(module => {
        const content = module.querySelector('.tdc-module-content');
        content.classList.add('d-none');
        module.classList.remove('active');
    });
    
    document.querySelectorAll('.tdc-module-card').forEach(card => {
        const content = card.querySelector('.tdc-module-content');
        content.classList.add('d-none');
        card.classList.remove('expanded');
    });
}

// Initialize tooltips
function initializeTooltips() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Global search
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', handleGlobalSearch);
    }
    
    // Filter controls
    const filters = ['threatFilter', 'threatLevelFilter', 'tdcModuleFilter', 'timeFilter', 'sortFilter', 'viewMode'];
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', applyFilters);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Handle global search
function handleGlobalSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    filterContent(searchTerm);
}

// Filter content based on search term
function filterContent(searchTerm) {
    const threatRows = document.querySelectorAll('#threatEventsTable tbody tr');
    const tdcModules = document.querySelectorAll('.tdc-module, .tdc-module-card');
    
    // Filter threat events
    threatRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Filter TDC modules
    tdcModules.forEach(module => {
        const text = module.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            module.style.display = '';
        } else {
            module.style.display = 'none';
        }
    });
}

// Apply filters
function applyFilters() {
    const threatFilter = document.getElementById('threatFilter').value;
    const threatLevelFilter = document.getElementById('threatLevelFilter').value;
    const tdcModuleFilter = document.getElementById('tdcModuleFilter').value;
    const timeFilter = document.getElementById('timeFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    const viewMode = document.getElementById('viewMode').value;
    
    // Apply filters to threat events
    filterThreatEvents(threatFilter, threatLevelFilter, tdcModuleFilter, timeFilter, sortFilter);
    
    // Apply view mode
    applyViewMode(viewMode);
}

// Filter threat events
function filterThreatEvents(threatType, severity, tdcModule, timeRange, sortBy) {
    const tableBody = document.querySelector('#threatEventsTable tbody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    rows.forEach(row => {
        let show = true;
        
        // Apply filters
        if (threatType !== 'All' && !row.dataset.threatType?.includes(threatType)) {
            show = false;
        }
        
        if (severity !== 'All' && row.dataset.severity !== severity) {
            show = false;
        }
        
        if (tdcModule !== 'All' && !row.dataset.tdcModules?.includes(tdcModule)) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
    
    // Apply sorting
    sortThreatEvents(sortBy);
}

// Sort threat events
function sortThreatEvents(sortBy) {
    const tableBody = document.querySelector('#threatEventsTable tbody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        switch (sortBy) {
            case 'timestamp-desc':
                return new Date(b.dataset.timestamp) - new Date(a.dataset.timestamp);
            case 'timestamp-asc':
                return new Date(a.dataset.timestamp) - new Date(b.dataset.timestamp);
            case 'severity-desc':
                return getSeverityValue(b.dataset.severity) - getSeverityValue(a.dataset.severity);
            case 'severity-asc':
                return getSeverityValue(a.dataset.severity) - getSeverityValue(b.dataset.severity);
            case 'session-id':
                return a.dataset.sessionId.localeCompare(b.dataset.sessionId);
            default:
                return 0;
        }
    });
    
    // Reorder rows
    rows.forEach(row => tableBody.appendChild(row));
}

// Get severity value for sorting
function getSeverityValue(severity) {
    const values = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
    return values[severity] || 0;
}

// Apply view mode
function applyViewMode(mode) {
    const container = document.querySelector('.container-fluid');
    
    switch (mode) {
        case 'cards':
            container.classList.remove('table-view', 'compact-view');
            container.classList.add('cards-view');
            break;
        case 'table':
            container.classList.remove('cards-view', 'compact-view');
            container.classList.add('table-view');
            break;
        case 'compact':
            container.classList.remove('cards-view', 'table-view');
            container.classList.add('compact-view');
            break;
    }
}

// Handle threat events
function handleThreatEvent(data) {
    // Add to threat data array
    threatData.push(data);
    
    // Update summary cards
    updateSummaryCards();
    
    // Update threat events table
    addThreatEventToTable(data);
    
    // Update charts
    updateCharts();
    
    // Update alert panels
    updateAlertPanels();
    
    // Show alert banner for critical threats
    if (data.severity === 'Critical') {
        showAlertBanner(data);
    }
    
    // Update timeline
    addEventToTimeline(data);
    
    // Update evidence details
    updateEvidenceDetails(data);
}

// Update summary cards
function updateSummaryCards() {
    console.log('Updating summary cards with', threatData.length, 'events');
    
    const totalSessions = new Set(threatData.map(t => t.session_id)).size;
    const totalEvents = threatData.length;
    const totalThreats = threatData.filter(t => {
        const threatType = t.threat_type || t.threat_vector;
        return threatType && threatType !== 'None' && threatType !== 'Unknown';
    }).length;
    const criticalThreats = threatData.filter(t => {
        const severity = t.severity || t.threat_level;
        return severity === 'Critical';
    }).length;
    const avgThreatScore = threatData.length > 0 ? 
        (threatData.reduce((sum, t) => sum + (t.threat_score || t.score || 0), 0) / threatData.length).toFixed(1) : 0;
    const avgEventsPerSession = totalSessions > 0 ? (totalEvents / totalSessions).toFixed(1) : 0;
    
    // Update summary card values
    const totalSessionsElement = document.getElementById('totalSessions');
    const totalEventsElement = document.getElementById('totalEvents');
    const avgEventsPerSessionElement = document.getElementById('avgEventsPerSession');
    const totalThreatsElement = document.getElementById('totalThreats');
    const criticalThreatsElement = document.getElementById('criticalThreats');
    const avgThreatScoreElement = document.getElementById('avgThreatScore');
    
    if (totalSessionsElement) totalSessionsElement.textContent = totalSessions;
    if (totalEventsElement) totalEventsElement.textContent = totalEvents;
    if (avgEventsPerSessionElement) avgEventsPerSessionElement.textContent = avgEventsPerSession;
    if (totalThreatsElement) totalThreatsElement.textContent = totalThreats;
    if (criticalThreatsElement) criticalThreatsElement.textContent = criticalThreats;
    if (avgThreatScoreElement) avgThreatScoreElement.textContent = avgThreatScore;
    
    // Update active sessions
    const activeSessionsElement = document.getElementById('activeSessions');
    if (activeSessionsElement) {
        activeSessionsElement.textContent = `${totalSessions} Active`;
    }
    
    console.log('Summary updated:', {
        totalSessions,
        totalEvents,
        totalThreats,
        criticalThreats,
        avgThreatScore,
        avgEventsPerSession
    });
}

// Add threat event to table
function addThreatEventToTable(data) {
    console.log('Adding threat event to table:', data);
    const tableBody = document.querySelector('#threatEventsTable tbody');
    const row = document.createElement('tr');
    
    // Generate a unique ID for the event
    const eventId = `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Map data fields from backend structure
    const timestamp = data.timestamp || data.time || new Date().toISOString();
    const sessionId = data.session_id || 'Unknown';
    const source = data.source || data.window_title || data.application || 'Unknown';
    const threatType = data.threat_type || data.threat_vector || 'Unknown';
    const severity = data.severity || data.threat_level || 'Low';
    const threatScore = data.threat_score || data.score || 0;
    const tdcModules = data.tdc_modules || [];
    
    row.dataset.timestamp = timestamp;
    row.dataset.sessionId = sessionId;
    row.dataset.threatType = threatType;
    row.dataset.severity = severity;
    row.dataset.tdcModules = tdcModules.join(',');
    row.dataset.eventId = eventId;
    
    row.innerHTML = `
        <td>${formatTimestamp(timestamp)}</td>
        <td><code>${sessionId}</code></td>
        <td>${source}</td>
        <td>${threatType}</td>
        <td><span class="severity-badge ${severity.toLowerCase()}">${severity}</span></td>
        <td>${threatScore}</td>
        <td>${formatTDCModules(tdcModules)}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary" onclick="viewThreatDetails('${eventId}')" 
                    data-bs-toggle="tooltip" title="View Details">
                <i class="bi bi-eye"></i>
            </button>
            <button class="btn btn-sm btn-outline-secondary" onclick="exportThreatData('${eventId}')" 
                    data-bs-toggle="tooltip" title="Export Data">
                <i class="bi bi-download"></i>
            </button>
        </td>
    `;
    
    tableBody.insertBefore(row, tableBody.firstChild);
    
    // Limit table rows
    const rows = tableBody.querySelectorAll('tr');
    if (rows.length > 100) {
        tableBody.removeChild(rows[rows.length - 1]);
    }
}

// Update charts
function updateCharts() {
    // Update threat level chart
    if (charts.threatLevel) {
        const threatLevels = ['Critical', 'High', 'Medium', 'Low'];
        const data = threatLevels.map(level => 
            threatData.filter(t => t.severity === level).length
        );
        
        charts.threatLevel.data.datasets[0].data = data;
        charts.threatLevel.update();
    }
    
    // Update threat vector chart
    if (charts.threatVector) {
        const threatTypes = ['AI_Manipulation', 'Elicitation', 'Insider_Threat', 'Sentiment_Manipulation', 'Grooming'];
        const data = threatTypes.map(type => 
            threatData.filter(t => t.threat_type === type).length
        );
        
        charts.threatVector.data.datasets[0].data = data;
        charts.threatVector.update();
    }
    
    // Update analytics chart
    if (charts.analytics) {
        const recentData = threatData.slice(-20); // Last 20 events
        const labels = recentData.map(t => formatTimestamp(t.timestamp, true));
        const scores = recentData.map(t => t.threat_score || 0);
        
        charts.analytics.data.labels = labels;
        charts.analytics.data.datasets[0].data = scores;
        charts.analytics.update();
    }
}

// Update alert panels
function updateAlertPanels() {
    const criticalThreats = threatData.filter(t => t.severity === 'Critical').slice(-5);
    const highThreats = threatData.filter(t => t.severity === 'High').slice(-5);
    const mediumThreats = threatData.filter(t => t.severity === 'Medium').slice(-5);
    
    updateAlertPanel('criticalThreatsPanel', criticalThreats, 'critical');
    updateAlertPanel('highThreatsPanel', highThreats, 'high');
    updateAlertPanel('mediumThreatsPanel', mediumThreats, 'medium');
    
    // Update counts
    document.getElementById('criticalThreatCount').textContent = threatData.filter(t => t.severity === 'Critical').length;
    document.getElementById('highThreatCount').textContent = threatData.filter(t => t.severity === 'High').length;
    document.getElementById('mediumThreatCount').textContent = threatData.filter(t => t.severity === 'Medium').length;
}

// Update alert panel
function updateAlertPanel(panelId, threats, level) {
    const panel = document.getElementById(panelId);
    
    if (threats.length === 0) {
        panel.innerHTML = `<p class="text-muted mb-0">No ${level} priority threats</p>`;
        return;
    }
    
    const threatsHtml = threats.map(threat => `
        <div class="alert alert-${level === 'critical' ? 'danger' : level === 'high' ? 'warning' : 'info'} alert-sm mb-2">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${threat.threat_type}</strong>
                    <br>
                    <small>Session: ${threat.session_id}</small>
                    <br>
                    <small>Score: ${threat.threat_score || 0}</small>
                </div>
                <small>${formatTimestamp(threat.timestamp, true)}</small>
            </div>
        </div>
    `).join('');
    
    panel.innerHTML = threatsHtml;
}

// Show alert banner
function showAlertBanner(data) {
    const banner = document.getElementById('alertBanner');
    const title = document.getElementById('alertTitle');
    const message = document.getElementById('alertMessage');
    
    title.textContent = `Critical Threat: ${data.threat_type}`;
    message.textContent = `Session ${data.session_id} - Score: ${data.threat_score || 0}`;
    
    banner.classList.remove('d-none');
    banner.classList.add('show');
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        banner.classList.remove('show');
        banner.classList.add('d-none');
    }, 10000);
}

// Add event to timeline
function addEventToTimeline(data) {
    const timeline = document.getElementById('eventTimeline');
    
    if (timeline.querySelector('.text-muted')) {
        timeline.innerHTML = '';
    }
    
    const eventElement = document.createElement('div');
    eventElement.className = `timeline-event ${data.severity.toLowerCase()}`;
    
    eventElement.innerHTML = `
        <div class="timeline-time">${formatTimestamp(data.timestamp, true)}</div>
        <div class="timeline-title">${data.threat_type}</div>
        <div class="timeline-description">Session: ${data.session_id} | Score: ${data.threat_score || 0}</div>
    `;
    
    timeline.insertBefore(eventElement, timeline.firstChild);
    
    // Limit timeline events
    const events = timeline.querySelectorAll('.timeline-event');
    if (events.length > 50) {
        timeline.removeChild(events[events.length - 1]);
    }
}

// Update evidence details
function updateEvidenceDetails(data) {
    const evidenceContainer = document.getElementById('evidenceDetails');
    
    if (evidenceContainer.querySelector('.text-muted')) {
        evidenceContainer.innerHTML = '';
    }
    
    const evidenceElement = document.createElement('div');
    evidenceElement.className = 'evidence-item';
    
    const confidence = data.threat_score > 80 ? 'high' : data.threat_score > 50 ? 'medium' : 'low';
    
    evidenceElement.innerHTML = `
        <div class="evidence-header">
            <div class="evidence-title">${data.threat_type}</div>
            <span class="evidence-confidence ${confidence}">${data.threat_score || 0}%</span>
        </div>
        <div class="evidence-content">
            <strong>Session:</strong> ${data.session_id}<br>
            <strong>Source:</strong> ${data.source || 'Unknown'}<br>
            <strong>TDC Modules:</strong> ${formatTDCModules(data.tdc_modules)}<br>
            <strong>Analysis:</strong> ${data.analysis || 'No detailed analysis available'}
        </div>
    `;
    
    evidenceContainer.insertBefore(evidenceElement, evidenceContainer.firstChild);
    
    // Limit evidence items
    const items = evidenceContainer.querySelectorAll('.evidence-item');
    if (items.length > 20) {
        evidenceContainer.removeChild(items[items.length - 1]);
    }
}

// Handle session updates
function handleSessionUpdate(data) {
    sessionData = data;
    currentSessionId = data.current_session;
    
    // Update session display
    document.getElementById('currentSessionId').textContent = currentSessionId || 'No Active Session';
    document.getElementById('chatSessionId').textContent = currentSessionId || 'No Active Session';
    
    // Update active sessions count
    document.getElementById('activeSessions').textContent = `${data.active_sessions || 0} Active`;
}

// Handle TDC updates
function handleTDCUpdate(data) {
    tdcModules = data;
    
    // Update TDC module status
    Object.keys(data).forEach(moduleId => {
        const moduleData = data[moduleId];
        updateTDCModuleStatus(moduleId, moduleData);
    });
}

// Update TDC module status
function updateTDCModuleStatus(moduleId, data) {
    const status = data.status || 'offline';
    const score = data.score || 0;
    const threats = data.threats || 0;
    
    // Update sidebar module
    const module = document.getElementById(`tdc-module-${moduleId}`);
    if (module) {
        const statusElement = module.querySelector('.tdc-module-status');
        const scoreElement = document.getElementById(`${moduleId}-score`);
        const threatsElement = document.getElementById(`${moduleId}-threats`);
        const detailsElement = document.getElementById(`${moduleId}-details`);
        
        if (statusElement) {
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            statusElement.className = `tdc-module-status ${status}`;
        }
        
        if (scoreElement) scoreElement.textContent = score;
        if (threatsElement) threatsElement.textContent = threats;
        if (detailsElement) {
            detailsElement.innerHTML = data.details || 'No analysis data available';
        }
    }
    
    // Update card module
    const card = document.getElementById(`tdc-card-${moduleId}`);
    if (card) {
        const icon = card.querySelector('.tdc-module-icon');
        const scoreElement = document.getElementById(`${moduleId}-card-score`);
        const threatsElement = document.getElementById(`${moduleId}-card-threats`);
        const detailsElement = document.getElementById(`${moduleId}-card-details`);
        
        if (icon) {
            icon.className = `tdc-module-icon ${status}`;
        }
        
        if (scoreElement) scoreElement.textContent = score;
        if (threatsElement) threatsElement.textContent = threats;
        if (detailsElement) {
            detailsElement.innerHTML = data.details || 'No analysis data available';
        }
    }
}

// Handle chat messages
function handleChatMessage(data) {
    // Update live conversation
    updateLiveConversation(data);
    
    // Update chat transcripts
    updateChatTranscripts(data);
    
    // Update chat summary
    updateChatSummary(data);
}

// Update live conversation
function updateLiveConversation(data) {
    const conversation = document.getElementById('liveConversation');
    
    if (conversation.querySelector('.text-muted')) {
        conversation.innerHTML = '';
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${data.sender.toLowerCase()} ${data.threat_detected ? 'threat' : ''}`;
    
    // Determine icon based on sender
    const iconClass = data.sender.toLowerCase() === 'ai' ? 'bi bi-robot' : 'bi bi-person';
    const iconColor = data.sender.toLowerCase() === 'ai' ? 'text-primary' : 'text-success';
    
    messageElement.innerHTML = `
        <div class="message-timestamp">${formatTimestamp(data.timestamp, true)}</div>
        <div class="message-content">
            <i class="${iconClass} ${iconColor} me-2"></i>
            ${data.content}
        </div>
    `;
    
    conversation.appendChild(messageElement);
    conversation.scrollTop = conversation.scrollHeight;
    
    // Limit messages
    const messages = conversation.querySelectorAll('.message');
    if (messages.length > 100) {
        conversation.removeChild(messages[0]);
    }
}

// Update chat transcripts
function updateChatTranscripts(data) {
    const userTranscript = document.getElementById('userTranscript');
    const aiTranscript = document.getElementById('aiTranscript');
    
    if (data.sender === 'user') {
        addTranscriptEntry(userTranscript, data);
    } else if (data.sender === 'ai') {
        addTranscriptEntry(aiTranscript, data);
    }
}

// Add transcript entry
function addTranscriptEntry(container, data) {
    const entry = document.createElement('div');
    entry.className = 'transcript-entry';
    
    entry.innerHTML = `
        <div class="transcript-timestamp">${formatTimestamp(data.timestamp, true)}</div>
        <div class="transcript-message">${data.content}</div>
    `;
    
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
    
    // Limit entries
    const entries = container.querySelectorAll('.transcript-entry');
    if (entries.length > 50) {
        container.removeChild(entries[0]);
    }
}

// Update chat summary
function updateChatSummary(data) {
    const summaryCard = document.getElementById('chatSummaryCard');
    
    // This would typically be updated with analysis from TDC modules
    if (data.threat_detected) {
        summaryCard.innerHTML = `
            <div class="alert alert-warning mb-0">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Threat Detected:</strong> ${data.threat_type || 'Unknown threat type'}
                <br>
                <small>Confidence: ${data.threat_score || 0}% | Session: ${data.session_id}</small>
            </div>
        `;
    }
}

// Handle system status
function handleSystemStatus(data) {
    // Update system indicators
    document.getElementById('pendingAlerts').textContent = `${data.pending_alerts || 0} Alerts`;
    
    // Update connection status
    updateConnectionStatus(data.websocket_connected);
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.status-indicator i.bi-circle-fill');
    if (statusIndicator) {
        statusIndicator.className = connected ? 'bi bi-circle-fill text-success' : 'bi bi-circle-fill text-danger';
    }
}

// Utility functions
function formatTimestamp(timestamp, short = false) {
    const date = new Date(timestamp);
    if (short) {
        return date.toLocaleTimeString();
    }
    return date.toLocaleString();
}

function formatTDCModules(modules) {
    if (!modules || modules.length === 0) return 'None';
    return modules.map(m => m.replace('TDC-', '')).join(', ');
}

function toggleDarkTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('dashboard-theme', newTheme);
}

// Quick actions
function quickAction(action) {
    switch (action) {
        case 'export':
            exportData();
            break;
        case 'refresh':
            loadInitialData();
            break;
        case 'help':
            showHelp();
            break;
        case 'expand':
            expandAllModules();
            break;
        case 'collapse':
            collapseAllModules();
            break;
    }
}

// Export data
function exportData() {
    const data = {
        threatData,
        sessionData,
        tdcModules,
        exportTime: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `catdams-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Show help
function showHelp() {
    const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
    helpModal.show();
}

// Setup keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'e':
                    event.preventDefault();
                    exportData();
                    break;
                case 'r':
                    event.preventDefault();
                    loadInitialData();
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    expandAllModules();
                    break;
                case 'ArrowDown':
                    event.preventDefault();
                    collapseAllModules();
                    break;
            }
        } else if (event.key === 'F1') {
            event.preventDefault();
            showHelp();
        }
    });
}

// Load initial data
function loadInitialData() {
    // This would typically fetch initial data from the server
    console.log('Loading initial data...');
    
    // Simulate loading
    setTimeout(() => {
        console.log('Initial data loaded');
    }, 1000);
}

// Navigation functions
function navigateToSection(section) {
    document.getElementById('currentSection').textContent = section.charAt(0).toUpperCase() + section.slice(1);
    // Additional navigation logic would go here
}

// Search functions
function setSearchScope(scope) {
    searchScope = scope;
    // Additional scope logic would go here
}

function clearSearch() {
    document.getElementById('globalSearch').value = '';
    filterContent('');
}

// Filter functions
function clearAllFilters() {
    const filters = ['threatFilter', 'threatLevelFilter', 'tdcModuleFilter', 'timeFilter', 'sortFilter'];
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) filter.value = filter.options[0].value;
    });
    applyFilters();
}

function saveFilterPreset() {
    const presetName = prompt('Enter preset name:');
    if (presetName) {
        const filters = ['threatFilter', 'threatLevelFilter', 'tdcModuleFilter', 'timeFilter', 'sortFilter', 'viewMode'];
        const preset = {};
        filters.forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) preset[filterId] = filter.value;
        });
        filterPresets[presetName] = preset;
        localStorage.setItem('catdams-filter-presets', JSON.stringify(filterPresets));
        alert('Filter preset saved!');
    }
}

function loadFilterPreset() {
    const presetNames = Object.keys(filterPresets);
    if (presetNames.length === 0) {
        alert('No saved presets found');
        return;
    }
    
    const presetName = prompt(`Enter preset name (${presetNames.join(', ')}):`);
    if (presetName && filterPresets[presetName]) {
        const preset = filterPresets[presetName];
        Object.keys(preset).forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) filter.value = preset[filterId];
        });
        applyFilters();
        alert('Filter preset loaded!');
    }
}

// Chart view functions
function updateChartView(chartType, viewType) {
    if (charts[chartType]) {
        charts[chartType].config.type = viewType;
        charts[chartType].update();
    }
}

// Map view functions
function updateMapView(viewType) {
    const map = document.getElementById('threatMap');
    if (map) {
        map.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-map display-4"></i>
                <p class="mt-2">${viewType.charAt(0).toUpperCase() + viewType.slice(1)} Map Loading...</p>
            </div>
        `;
    }
}

// Timeline functions
function filterTimeline(filter) {
    const events = document.querySelectorAll('.timeline-event');
    events.forEach(event => {
        if (filter === 'all' || event.classList.contains(filter)) {
            event.style.display = '';
        } else {
            event.style.display = 'none';
        }
    });
}

// Evidence functions
function showEvidence(filter) {
    const items = document.querySelectorAll('.evidence-item');
    items.forEach(item => {
        if (filter === 'all' || item.querySelector('.evidence-confidence').classList.contains(filter)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Threat detail functions
function viewThreatDetails(threatId) {
    const threat = threatData.find(t => t.id === threatId);
    if (threat) {
        alert(`Threat Details:\nType: ${threat.threat_type}\nSeverity: ${threat.severity}\nScore: ${threat.threat_score}\nSession: ${threat.session_id}`);
    }
}

function exportThreatData(threatId) {
    const threat = threatData.find(t => t.id === threatId);
    if (threat) {
        const blob = new Blob([JSON.stringify(threat, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat-${threatId}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Load saved filter presets
document.addEventListener('DOMContentLoaded', function() {
    const savedPresets = localStorage.getItem('catdams-filter-presets');
    if (savedPresets) {
        filterPresets = JSON.parse(savedPresets);
    }
}); 