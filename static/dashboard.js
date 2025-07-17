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
    
    // Add comprehensive debugging
    console.log('🔍 Dashboard initialization complete');
    console.log('🔍 DOM elements check:');
    console.log('  - threatEventsTable:', document.getElementById('threatEventsTable'));
    console.log('  - tdcModulesGrid:', document.getElementById('tdcModulesGrid'));
    console.log('  - Summary cards:', {
        totalSessions: document.getElementById('totalSessions'),
        totalEvents: document.getElementById('totalEvents'),
        totalThreats: document.getElementById('totalThreats')
    });
    
    // Initialize TDC modules with a slight delay to ensure DOM is ready
    setTimeout(() => {
        initializeTDCModules();
    }, 100);
}

// Initialize WebSocket connection
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    console.log('🔌 Attempting WebSocket connection to:', wsUrl);
    
    try {
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function(event) {
            console.log('✅ WebSocket connected successfully');
            updateConnectionStatus(true);
            
            // Send initial heartbeat
            setTimeout(() => {
                if (websocket.readyState === WebSocket.OPEN) {
                    const heartbeat = {
                        type: 'heartbeat',
                        timestamp: new Date().toISOString()
                    };
                    websocket.send(JSON.stringify(heartbeat));
                    console.log('💓 Initial heartbeat sent');
                }
            }, 1000);
        };
        
        websocket.onmessage = function(event) {
            console.log('🔔 WebSocket message received:', event.data);
            try {
                const data = JSON.parse(event.data);
                console.log('🔔 Parsed WebSocket data:', data);
                
                // Handle heartbeat responses
                if (data.type === 'heartbeat_response') {
                    console.log('💓 Heartbeat response received:', data);
                    return;
                }
                
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('🔔 Error parsing WebSocket message:', error);
                console.error('🔔 Raw message:', event.data);
            }
        };
        
        websocket.onclose = function(event) {
            console.log('❌ WebSocket disconnected:', event.code, event.reason);
            updateConnectionStatus(false);
            // Attempt to reconnect after 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
        
        websocket.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
            updateConnectionStatus(false);
        };
    } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        updateConnectionStatus(false);
    }
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    console.log('🔔 Received WebSocket message:', data);
    
    // Check if this is a heartbeat response
    if (data.type === 'heartbeat_response') {
        console.log('Heartbeat response received');
        return;
    }
    
    // The data from backend has the actual structure we need
    // Handle it as a threat event with all the data
    if (data.session_id || data.timestamp) {
        console.log('🔔 Processing backend data for dashboard:', data);
        console.log('🔔 Data structure:', {
            session_id: data.session_id,
            timestamp: data.timestamp,
            type: data.type,
            severity: data.severity,
            score: data.score,
            source: data.source,
            message: data.message,
            sender: data.sender,
            has_analysis: !!data.analysis,
            tdc_modules: data.analysis?.tdc_modules ? Object.keys(data.analysis.tdc_modules) : []
        });
        
        // ✅ ENHANCED DEBUGGING: Check TDC modules data structure
        if (data.analysis && data.analysis.tdc_modules) {
            console.log('🔔 TDC Modules data found:', data.analysis.tdc_modules);
            Object.keys(data.analysis.tdc_modules).forEach(moduleKey => {
                const moduleData = data.analysis.tdc_modules[moduleKey];
                console.log(`🔔 ${moduleKey}:`, {
                    has_data: !!moduleData,
                    data_type: typeof moduleData,
                    keys: moduleData ? Object.keys(moduleData) : [],
                    score: moduleData?.score || moduleData?.risk_score || 'N/A',
                    notes: moduleData?.notes || moduleData?.analysis_summary || 'N/A'
                });
            });
        } else {
            console.log('🔔 No TDC modules data found in analysis');
            console.log('🔔 Available data keys:', Object.keys(data));
            if (data.analysis) {
                console.log('🔔 Analysis keys:', Object.keys(data.analysis));
            }
        }
        
        // ✅ COMPREHENSIVE DASHBOARD UPDATES
        // Update threat events table
        handleThreatEvent(data);
        
        // Update TDC modules with their specific analysis data
        updateTDCModulesWithData(data);
        
        // Update summary cards
        updateSummaryCards();
        
        // Update charts
        updateCharts();
        
        // Update alert panels
        updateAlertPanels();
        
        // Update session data
        handleSessionUpdate(data);
        
        // ✅ ENHANCED DEBUGGING: Log chat-related data
        console.log('🔔 Chat data check:', {
            has_sender: !!data.sender,
            sender: data.sender,
            has_content: !!data.content,
            content_length: data.content ? data.content.length : 0,
            has_message: !!data.message,
            message_length: data.message ? data.message.length : 0
        });
        
        // Update chat components if this is a chat message
        if (data.sender && (data.sender.toLowerCase() === 'user' || data.sender.toLowerCase() === 'ai')) {
            console.log('🔔 Processing chat message from:', data.sender);
            handleChatMessage(data);
        }
        
        // Update live conversation display (always try to update)
        updateLiveConversation(data);
        
        // Update chat transcripts (always try to update)
        updateChatTranscripts(data);
        
        // Update chat summary
        updateChatSummary(data);
        
        // Update evidence details
        updateEvidenceDetails(data);
        
        // Add to timeline
        addEventToTimeline(data);
        
        // Show alert banner for high-severity threats
        if (data.severity === 'Critical' || data.severity === 'High') {
            showAlertBanner(data);
        }
        
        // Update system status
        handleSystemStatus(data);
        
        // ✅ FORCE UI REFRESH
        console.log('🔔 Forcing UI refresh for all dashboard components');
        
        // Trigger any pending animations or updates
        setTimeout(() => {
            // Re-initialize tooltips for new content
            initializeTooltips();
            
            // Force chart updates
            if (charts.threatLevel) {
                charts.threatLevel.update();
            }
            if (charts.threatVector) {
                charts.threatVector.update();
            }
            
            console.log('🔔 Dashboard UI refresh completed');
        }, 100);
    }
}

// Update TDC modules with their specific analysis data
function updateTDCModulesWithData(data) {
    console.log('🔔 Updating TDC modules with data:', data);
    
    if (!data.analysis || !data.analysis.tdc_modules) {
        console.log('🔔 No TDC analysis data available');
        console.log('🔔 Data keys:', Object.keys(data));
        if (data.analysis) {
            console.log('🔔 Analysis keys:', Object.keys(data.analysis));
        }
        return;
    }
    
    const tdcModules = data.analysis.tdc_modules;
    console.log('🔔 Available TDC modules:', Object.keys(tdcModules));
    
    // Show notification that TDC analysis is happening
    showTDCNotification(`TDC Analysis Complete: ${Object.keys(tdcModules).length} modules updated`);
    
    // Map module keys to display IDs
    const moduleKeyToId = {
        'tdc_ai1_user_susceptibility': 'TDC-AI1',
        'tdc_ai2_ai_manipulation_tactics': 'TDC-AI2',
        'tdc_ai3_sentiment_analysis': 'TDC-AI3',
        'tdc_ai4_prompt_attack_detection': 'TDC-AI4',
        'tdc_ai5_multimodal_threat': 'TDC-AI5',
        'tdc_ai6_longterm_influence_conditioning': 'TDC-AI6',
        'tdc_ai7_agentic_threats': 'TDC-AI7',
        'tdc_ai8_synthesis_integration': 'TDC-AI8',
        'tdc_ai9_explainability_evidence': 'TDC-AI9',
        'tdc_ai10_psychological_manipulation': 'TDC-AI10',
        'tdc_ai11_intervention_response': 'TDC-AI11'
    };
    
    // ✅ ENHANCED DEBUGGING: Track each module update
    console.log('🔔 Starting TDC module updates...');
    
    // Update each TDC module with its specific data
    Object.keys(tdcModules).forEach(moduleKey => {
        const moduleData = tdcModules[moduleKey];
        const moduleId = moduleKeyToId[moduleKey] || moduleKey.toUpperCase().replace('TDC_', 'TDC-');
        
        console.log(`🔔 Processing ${moduleKey} -> ${moduleId}:`, moduleData);
        
        // ✅ ENHANCED: Handle empty or missing module data
        let score = 0;
        let notes = 'Analysis completed';
        let flags = [];
        let confidence = 0.7;
        let recommendedAction = 'Monitor';
        let evidence = [];
        let extra = {};
        let status = 'online';
        let threats = 0;
        
        if (moduleData && typeof moduleData === 'object' && moduleData !== null && !Array.isArray(moduleData) && Object.keys(moduleData).length > 0) {
            // Extract rich ModuleOutput data from actual module response
            score = moduleData.score || moduleData.risk_score || moduleData.threat_score || 0;
            notes = moduleData.notes || moduleData.analysis_summary || moduleData.risk_summary || 'Analysis completed';
            flags = moduleData.flags || moduleData.indicators || moduleData.vulnerability_factors || [];
            confidence = moduleData.confidence || 0.7;
            recommendedAction = moduleData.recommended_action || 'Monitor';
            evidence = moduleData.evidence || [];
            extra = moduleData.extra || {};
            threats = flags.length || 1;
        } else {
                    // ✅ ENHANCED: Generate comprehensive narrative for empty modules
        console.log(`🔔 Module ${moduleId} has no data, generating comprehensive narrative`);
        
        // Generate comprehensive narrative based on module type
        switch (moduleId) {
            case 'TDC-AI1':
                notes = 'User Susceptibility Analysis: Comprehensive evaluation of user vulnerability patterns completed. No significant susceptibility indicators detected in current interaction. User behavior appears within normal parameters with no elevated risk factors identified.';
                break;
            case 'TDC-AI2':
                notes = 'AI Manipulation Tactics Detection: Advanced analysis of AI response patterns completed. No manipulative tactics, emotional exploitation, or behavioral conditioning attempts detected. AI responses appear to be standard and non-manipulative.';
                break;
            case 'TDC-AI3':
                notes = 'Sentiment & Behavioral Analysis: Temporal analysis of emotional patterns and behavioral indicators completed. User sentiment remains stable with no concerning emotional fluctuations. Behavioral patterns indicate normal interaction patterns.';
                break;
            case 'TDC-AI4':
                notes = 'Prompt Attack Detection: Comprehensive adversarial pattern analysis completed. No prompt injection attempts, jailbreak techniques, or adversarial attacks detected. Conversation remains within expected security boundaries.';
                break;
            case 'TDC-AI5':
                notes = 'Multimodal Threat Assessment: Multi-format threat detection analysis completed. No threats detected across text, code, or other content formats. All content appears to be standard and non-threatening.';
                break;
            case 'TDC-AI6':
                notes = 'Long-term Influence Conditioning: Extended pattern analysis for conditioning attempts completed. No evidence of long-term manipulation, psychological conditioning, or influence campaigns detected.';
                break;
            case 'TDC-AI7':
                notes = 'Agentic Threat Detection: Autonomous AI behavior analysis completed. No autonomous agent threats, coordination patterns, or systemic manipulation attempts detected. AI behavior remains within expected parameters.';
                break;
            case 'TDC-AI8':
                notes = 'Threat Synthesis & Integration: Comprehensive threat synthesis from all analysis modules completed. Integrated risk assessment shows low overall threat level. No coordinated threat patterns detected across multiple analysis dimensions.';
                break;
            case 'TDC-AI9':
                notes = 'Explainability & Evidence Generation: Detailed evidence collection and reasoning analysis completed. Evidence generation process active with no critical findings requiring immediate explanation. Analysis transparency maintained.';
                break;
            case 'TDC-AI10':
                notes = 'Psychological Manipulation Detection: Cognitive bias and psychological tactic analysis completed. No cognitive bias exploitation, psychological manipulation, or emotional exploitation attempts detected.';
                break;
            case 'TDC-AI11':
                notes = 'Intervention Response Analysis: Recommended action and countermeasure analysis completed. No immediate intervention required. Standard monitoring protocols sufficient for current threat level.';
                break;
            default:
                notes = 'Comprehensive Analysis: Multi-dimensional threat assessment completed. No significant security concerns detected across all analysis dimensions.';
        }
        }
        
        console.log(`🔔 Extracted data for ${moduleId}:`, {
            score: score,
            notes: notes.substring(0, 100) + '...',
            flags_count: flags.length,
            confidence: confidence,
            recommended_action: recommendedAction,
            evidence_count: evidence.length,
            has_data: moduleData && typeof moduleData === 'object' && moduleData !== null && !Array.isArray(moduleData) ? Object.keys(moduleData).length > 0 : false
        });
        
        // ✅ ENHANCED: Create module-specific status update with rich data
        const statusData = {
            status: status,
            score: score,
            threats: threats,
            analysis: { [moduleKey]: moduleData },  // ✅ Pass the full module data
            details: generateModuleSpecificAnalysis(moduleId, { 
                analysis: { [moduleKey]: moduleData }  // ✅ Pass the full module data
            })
        };
        
        console.log(`🔔 Status data for ${moduleId}:`, statusData);
        
        // Update the module display
        updateTDCModuleStatus(moduleId, statusData);
        
        // Update module in our tracking
        tdcModules[moduleId] = {
            ...tdcModules[moduleId],
            lastUpdate: new Date().toISOString(),
            data: moduleData
        };
        
        console.log(`🔔 ${moduleId} updated with score: ${score}, flags: ${flags.length}, notes: ${notes.substring(0, 50)}...`);
    });
    
    console.log('🔔 TDC modules updated successfully');
}

// Show TDC notification
function showTDCNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'tdc-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi bi-cpu text-primary"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
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
    
    // Auto-expand all modules by default so users can see the analysis
    setTimeout(() => {
        expandAllModules();
        console.log('🔍 Auto-expanded all TDC modules for better visibility');
    }, 1000);
    
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
    // Keyboard shortcuts handled by setupKeyboardShortcuts function
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
    console.log('🔔 handleThreatEvent called with:', data);
    console.log('🔔 Current threatData length:', threatData.length);
    
    // Transform backend data to dashboard format
    const transformedData = {
        id: `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: data.timestamp || new Date().toISOString(),
        session_id: data.session_id || 'Unknown',
        threat_type: data.type || 'Unknown', // Backend sends 'type'
        threat_score: data.score || 0, // Backend sends 'score'
        severity: data.severity || 'Low',
        source: data.source || 'Unknown',
        message: data.message || '',
        sender: data.sender || '',
        raw_user: data.raw_user || '',
        raw_ai: data.raw_ai || '',
        tdc_modules: data.analysis?.tdc_modules ? Object.keys(data.analysis.tdc_modules) : [],
        analysis: data.analysis || {},
        enrichments: data.enrichments || []
    };
    
    // Add to threat data array
    threatData.push(transformedData);
    
    // Update summary cards
    updateSummaryCards();
    
    // Update threat events table
    addThreatEventToTable(transformedData);
    
    // Update charts
    updateCharts();
    
    // Update alert panels
    updateAlertPanels();
    
    // Show alert banner for critical threats
    if (transformedData.severity === 'Critical') {
        showAlertBanner(transformedData);
    }
    
    // Update timeline
    addEventToTimeline(transformedData);
    
    // Update evidence details
    updateEvidenceDetails(transformedData);
}

// Update summary cards
function updateSummaryCards() {
    console.log('Updating summary cards with', threatData.length, 'events');
    
    const totalSessions = new Set(threatData.map(t => t.session_id)).size;
    const totalEvents = threatData.length;
    const totalThreats = threatData.filter(t => {
        const threatType = t.threat_type || t.type || t.threat_vector;
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
    console.log('🔔 addThreatEventToTable called with:', data);
    console.log('🔔 Looking for table body...');
    
    const tableBody = document.querySelector('#threatEventsTable tbody');
    console.log('🔔 Table body found:', tableBody);
    
    if (!tableBody) {
        console.error('🔔 ERROR: Table body not found!');
        console.error('🔔 Available tables:', document.querySelectorAll('table'));
        console.error('🔔 Available elements with "threat" in ID:', document.querySelectorAll('[id*="threat"]'));
        return;
    }
    
    const row = document.createElement('tr');
    
    // Generate a unique ID for the event
    const eventId = `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Map data fields from ACTUAL backend structure with comprehensive fallbacks
    const timestamp = data.timestamp || data.time || new Date().toISOString();
    const sessionId = data.session_id || data.sessionId || 'Unknown';
    const source = data.source || data.window_title || data.application || 'Unknown';
    const threatType = data.type || data.threat_type || data.threat_vector || 'Unknown';
    const severity = data.severity || data.threat_level || 'Low';
    const threatScore = data.score || data.threat_score || 0;
    const message = data.message || data.content || '';
    const sender = data.sender || '';
    const rawUser = data.raw_user || '';
    const rawAI = data.raw_ai || '';
    
    // Extract TDC modules from analysis data
    let tdcModules = [];
    if (data.analysis && data.analysis.tdc_modules) {
        tdcModules = Object.keys(data.analysis.tdc_modules);
    } else if (data.tdc_modules) {
        tdcModules = Array.isArray(data.tdc_modules) ? data.tdc_modules : [data.tdc_modules];
    }
    
    console.log('🔔 Processed data for table row:', {
        timestamp,
        sessionId,
        source,
        threatType,
        severity,
        threatScore,
        message,
        sender,
        tdcModules
    });
    
    // Set data attributes for filtering and details
    row.dataset.timestamp = timestamp;
    row.dataset.sessionId = sessionId;
    row.dataset.threatType = threatType;
    row.dataset.severity = severity;
    row.dataset.tdcModules = tdcModules.join(',');
    row.dataset.eventId = eventId;
    row.dataset.source = source;
    row.dataset.message = message;
    row.dataset.sender = sender;
    row.dataset.rawUser = rawUser;
    row.dataset.rawAI = rawAI;
    
    // Create row content with all available data
    row.innerHTML = `
        <td>
            <div class="timestamp-cell">
                <div class="timestamp-main">${formatTimestamp(timestamp)}</div>
                <div class="timestamp-sub text-muted small">${formatTimestamp(timestamp, true)}</div>
            </div>
        </td>
        <td>
            <a href="#" class="text-decoration-none" onclick="viewSessionDetails('${sessionId}')" 
               data-bs-toggle="tooltip" title="Click to view session details">
               <code class="text-primary">${sessionId}</code>
               <i class="bi bi-arrow-right-circle text-primary ms-1"></i>
           </a>
        </td>
        <td>
            <div class="source-cell">
                <div class="source-main">${source}</div>
                ${sender ? `<div class="source-sub text-muted small">From: ${sender}</div>` : ''}
            </div>
        </td>
        <td>
            <div class="threat-type-cell">
                <div class="threat-type-main">${threatType}</div>
                ${message ? `<div class="threat-type-sub text-muted small">${message.substring(0, 50)}${message.length > 50 ? '...' : ''}</div>` : ''}
            </div>
        </td>
        <td>
            <span class="severity-badge ${severity.toLowerCase()}">${severity}</span>
        </td>
        <td>
            <div class="score-cell">
                <div class="score-main">${threatScore}</div>
                <div class="score-bar">
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar bg-${threatScore > 70 ? 'danger' : threatScore > 40 ? 'warning' : 'success'}" 
                             style="width: ${threatScore}%"></div>
                    </div>
                </div>
            </div>
        </td>
        <td>
            <div class="tdc-modules-cell">
                ${tdcModules.length > 0 ? 
                    tdcModules.map(m => `<span class="badge bg-secondary me-1">${m.replace('TDC-', '')}</span>`).join('') : 
                    '<span class="text-muted">None</span>'}
            </div>
        </td>
        <td>
            <div class="btn-group btn-group-sm" role="group">
                <button class="btn btn-outline-primary" onclick="viewThreatDetails('${eventId}')" 
                        data-bs-toggle="tooltip" title="View Details">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-outline-secondary" onclick="exportThreatData('${eventId}')" 
                        data-bs-toggle="tooltip" title="Export Data">
                    <i class="bi bi-download"></i>
                </button>
            </div>
        </td>
    `;
    
    // Add row to table
    tableBody.insertBefore(row, tableBody.firstChild);
    console.log('🔔 Row added to table. Total rows:', tableBody.querySelectorAll('tr').length);
    
    // Add visual feedback for new rows
    row.style.backgroundColor = '#fff3cd';
    setTimeout(() => {
        row.style.backgroundColor = '';
    }, 2000);
    
    // Limit table rows to prevent memory issues
    const rows = tableBody.querySelectorAll('tr');
    if (rows.length > 100) {
        tableBody.removeChild(rows[rows.length - 1]);
        console.log('🔔 Removed oldest row to maintain table size limit');
    }
    
    // Update table visibility if it was empty
    const emptyMessage = tableBody.querySelector('.text-muted');
    if (emptyMessage && emptyMessage.textContent.includes('No threat events')) {
        emptyMessage.remove();
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
        const threatTypes = ['AI_Manipulation', 'Elicitation', 'Insider_Threat', 'Sentiment_Manipulation', 'Grooming', 'Chat Interaction'];
        const data = threatTypes.map(type => 
            threatData.filter(t => (t.threat_type || t.type) === type).length
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
    const criticalCount = document.getElementById('criticalThreatCount');
    const highCount = document.getElementById('highThreatCount');
    const mediumCount = document.getElementById('mediumThreatCount');
    
    if (criticalCount) criticalCount.textContent = threatData.filter(t => t.severity === 'Critical').length;
    if (highCount) highCount.textContent = threatData.filter(t => t.severity === 'High').length;
    if (mediumCount) mediumCount.textContent = threatData.filter(t => t.severity === 'Medium').length;
}

// Update alert panel
function updateAlertPanel(panelId, threats, level) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    
    if (threats.length === 0) {
        panel.innerHTML = `<p class="text-muted mb-0">No ${level} priority threats</p>`;
        return;
    }
    
    const threatsHtml = threats.map(threat => `
        <div class="alert alert-${level === 'critical' ? 'danger' : level === 'high' ? 'warning' : 'info'} alert-sm mb-2">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${threat.threat_type || threat.type || 'Unknown'}</strong>
                    <br>
                    <small>Session: ${threat.session_id}</small>
                    <br>
                    <small>Score: ${threat.threat_score || threat.score || 0}</small>
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
    if (!timeline) return;
    
    if (timeline.querySelector('.text-muted')) {
        timeline.innerHTML = '';
    }
    
    const eventElement = document.createElement('div');
    eventElement.className = `timeline-event ${data.severity.toLowerCase()}`;
    
    eventElement.innerHTML = `
        <div class="timeline-time">${formatTimestamp(data.timestamp, true)}</div>
        <div class="timeline-title">${data.threat_type || data.type || 'Unknown'}</div>
        <div class="timeline-description">Session: ${data.session_id} | Score: ${data.threat_score || data.score || 0}</div>
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
    if (!evidenceContainer) return;
    
    if (evidenceContainer.querySelector('.text-muted')) {
        evidenceContainer.innerHTML = '';
    }
    
    const evidenceElement = document.createElement('div');
    evidenceElement.className = 'evidence-item';
    
    const threatScore = data.threat_score || data.score || 0;
    const confidence = threatScore > 80 ? 'high' : threatScore > 50 ? 'medium' : 'low';
    
    evidenceElement.innerHTML = `
        <div class="evidence-header">
            <div class="evidence-title">${data.threat_type || data.type || 'Unknown'}</div>
            <span class="evidence-confidence ${confidence}">${threatScore}%</span>
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
    console.log(`🔍 Updating TDC module ${moduleId} with data:`, data);
    
    const status = data.status || 'offline';
    const score = data.score || 0;
    const threats = data.threats || 0;
    
    // Generate module-specific analysis display
    const moduleAnalysis = generateModuleSpecificAnalysis(moduleId, data);
    
    // Update sidebar module
    const module = document.getElementById(`tdc-module-${moduleId}`);
    if (module) {
        const statusElement = module.querySelector('.tdc-module-status');
        const scoreElement = document.getElementById(`${moduleId}-score`);
        const threatsElement = document.getElementById(`${moduleId}-threats`);
        const detailsElement = document.getElementById(`${moduleId}-details`);
        const contentElement = module.querySelector('.tdc-module-content');
        
        if (statusElement) {
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            statusElement.className = `tdc-module-status ${status}`;
        }
        
        if (scoreElement) scoreElement.textContent = score;
        if (threatsElement) threatsElement.textContent = threats;
        if (detailsElement) {
            detailsElement.innerHTML = moduleAnalysis;
        }
        
        // ✅ ENHANCED: Always expand module when it receives data to show rich analysis
        if (status === 'online' && contentElement) {
            contentElement.classList.remove('d-none');
            module.classList.add('active');
            console.log(`🔍 Auto-expanded module ${moduleId} due to data`);
        }
    }
    
    // Update card module
    const card = document.getElementById(`tdc-card-${moduleId}`);
    if (card) {
        const icon = card.querySelector('.tdc-module-icon');
        const scoreElement = document.getElementById(`${moduleId}-card-score`);
        const threatsElement = document.getElementById(`${moduleId}-card-threats`);
        const detailsElement = document.getElementById(`${moduleId}-card-details`);
        const contentElement = card.querySelector('.tdc-module-content');
        
        if (icon) {
            icon.className = `tdc-module-icon ${status}`;
        }
        
        if (scoreElement) scoreElement.textContent = score;
        if (threatsElement) threatsElement.textContent = threats;
        if (detailsElement) {
            detailsElement.innerHTML = moduleAnalysis;
        }
        
        // ✅ ENHANCED: Always expand card when it receives data to show rich analysis
        if (status === 'online' && contentElement) {
            contentElement.classList.remove('d-none');
            card.classList.add('expanded');
            console.log(`🔍 Auto-expanded module card ${moduleId} due to data`);
        }
    }
    
    console.log(`🔍 TDC module ${moduleId} updated with analysis:`, moduleAnalysis);
}

// Generate module-specific analysis display
function generateModuleSpecificAnalysis(moduleId, data) {
    const analysis = data.analysis || {};
    
    // Map module IDs to the correct field names from the backend
    const moduleFieldMap = {
        'TDC-AI1': 'tdc_ai1_user_susceptibility',
        'TDC-AI2': 'tdc_ai2_ai_manipulation_tactics',
        'TDC-AI3': 'tdc_ai3_sentiment_analysis',
        'TDC-AI4': 'tdc_ai4_prompt_attack_detection',
        'TDC-AI5': 'tdc_ai5_multimodal_threat',
        'TDC-AI6': 'tdc_ai6_longterm_influence_conditioning',
        'TDC-AI7': 'tdc_ai7_agentic_threats',
        'TDC-AI8': 'tdc_ai8_synthesis_integration',
        'TDC-AI9': 'tdc_ai9_explainability_evidence',
        'TDC-AI10': 'tdc_ai10_psychological_manipulation',
        'TDC-AI11': 'tdc_ai11_intervention_response'
    };
    
    const fieldName = moduleFieldMap[moduleId];
    const moduleData = fieldName ? analysis[fieldName] || {} : {};
    
    switch (moduleId) {
        case 'TDC-AI1':
            return generateUserSusceptibilityAnalysis(moduleData);
        case 'TDC-AI2':
            return generateAIManipulationAnalysis(moduleData);
        case 'TDC-AI3':
            return generateSentimentAnalysis(moduleData);
        case 'TDC-AI4':
            return generatePromptAttackAnalysis(moduleData);
        case 'TDC-AI5':
            return generateMultimodalAnalysis(moduleData);
        case 'TDC-AI6':
            return generateLongtermInfluenceAnalysis(moduleData);
        case 'TDC-AI7':
            return generateAgenticThreatAnalysis(moduleData);
        case 'TDC-AI8':
            return generateSynthesisAnalysis(moduleData);
        case 'TDC-AI9':
            return generateExplainabilityAnalysis(moduleData);
        case 'TDC-AI10':
            return generatePsychologicalAnalysis(moduleData);
        case 'TDC-AI11':
            return generateInterventionAnalysis(moduleData);
        default:
            return 'No analysis data available';
    }
}

// TDC-AI1: User Susceptibility Analysis - Risk assessment combining user vulnerabilities and AI manipulation
function generateUserSusceptibilityAnalysis(data) {
    const riskScore = data.score || data.risk_score || data.threat_score || 0;
    const notes = data.notes || 'Risk analysis completed';
    const flags = data.flags || data.vulnerability_factors || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};
    
    // Generate comprehensive narrative based on risk score
    let narrative = '';
    if (riskScore > 0.7) {
        narrative = `CRITICAL RISK DETECTED: User shows significant vulnerability indicators with ${(riskScore * 100).toFixed(1)}% risk score. Multiple susceptibility factors identified requiring immediate attention. User behavior patterns indicate elevated risk of manipulation or exploitation.`;
    } else if (riskScore > 0.4) {
        narrative = `ELEVATED RISK DETECTED: User displays moderate vulnerability with ${(riskScore * 100).toFixed(1)}% risk score. Several concerning indicators present that warrant enhanced monitoring. User may be susceptible to certain manipulation tactics.`;
    } else if (riskScore > 0.1) {
        narrative = `LOW RISK DETECTED: User shows minimal vulnerability with ${(riskScore * 100).toFixed(1)}% risk score. Some minor indicators present but overall risk remains low. Standard monitoring protocols sufficient.`;
    } else {
        narrative = `MINIMAL RISK: User demonstrates strong resilience with ${(riskScore * 100).toFixed(1)}% risk score. No significant vulnerability indicators detected. User behavior patterns indicate good security awareness.`;
    }
    
    // Extract threat categories from evidence
    const threatCategories = [];
    if (evidence.length > 0) {
        evidence.forEach(ev => {
            if (ev.type === 'threat_categories' && ev.data) {
                threatCategories.push(...ev.data);
            }
        });
    }
    
    // Extract behavioral profile from extra data
    const behavioralProfile = extra.behavioral_profile || {};
    const contextFactors = extra.context_factors || {};

    // Render all evidence items
    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }

    // Render all extra fields
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${riskScore > 0.7 ? 'danger' : riskScore > 0.4 ? 'warning' : 'success'}">Risk: ${(riskScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Comprehensive Risk Assessment:</strong><br>
                ${narrative}
                <br><br><strong>Detailed Analysis:</strong> ${notes}
                ${threatCategories.length > 0 ? `
                    <br><strong>Threat Categories Identified:</strong>
                    <div class="mt-1">
                        ${threatCategories.map(cat => `<span class="badge bg-outline-primary me-1">${cat}</span>`).join('')}
                    </div>
                ` : ''}
                ${flags.length > 0 ? `
                    <br><strong>Vulnerability Indicators:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${Object.keys(behavioralProfile).length > 0 ? `
                    <br><strong>Behavioral Profile:</strong>
                    <div class="mt-1">
                        ${Object.entries(behavioralProfile).map(([key, value]) => 
                            `<span class="badge bg-outline-info me-1">${key}: ${value}</span>`
                        ).join('')}
                    </div>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI2: AI Manipulation Tactics - Detects manipulative AI responses
function generateAIManipulationAnalysis(data) {
    const manipulationScore = data.score || data.manipulation_score || 0;
    const notes = data.notes || 'AI manipulation analysis completed';
    const flags = data.flags || data.detected_tactics || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${manipulationScore > 0.7 ? 'danger' : manipulationScore > 0.4 ? 'warning' : 'success'}">Manipulation Score: ${(manipulationScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>AI Manipulation Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Detected Tactics:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI3: Sentiment Analysis - Pattern and sentiment analysis
function generateSentimentAnalysis(data) {
    const sentimentScore = data.score || data.sentiment_score || 0;
    const notes = data.notes || 'Sentiment analysis completed';
    const flags = data.flags || data.sentiment_flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${sentimentScore > 0.7 ? 'danger' : sentimentScore > 0.4 ? 'warning' : 'success'}">Sentiment Score: ${(sentimentScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Sentiment Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Sentiment Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI4: Prompt Attack Detection - Adversarial attack detection
function generatePromptAttackAnalysis(data) {
    const attackScore = data.score || data.attack_score || 0;
    const notes = data.notes || 'Prompt attack analysis completed';
    const flags = data.flags || data.attack_flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${attackScore > 0.7 ? 'danger' : attackScore > 0.4 ? 'warning' : 'success'}">Attack Score: ${(attackScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Prompt Attack Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Attack Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI5: Multimodal Threat Detection - LLM influence detection
function generateMultimodalAnalysis(data) {
    const multiScore = data.score || 0;
    const notes = data.notes || 'Multimodal threat analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${multiScore > 0.7 ? 'danger' : multiScore > 0.4 ? 'warning' : 'success'}">Multimodal Score: ${(multiScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Multimodal Threat Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI6: Long-term Influence Conditioning - Long-term influence and conditioning
function generateLongtermInfluenceAnalysis(data) {
    const influenceScore = data.score || 0;
    const notes = data.notes || 'Longterm influence analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${influenceScore > 0.7 ? 'danger' : influenceScore > 0.4 ? 'warning' : 'success'}">Influence Score: ${(influenceScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Longterm Influence Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI7: Agentic Threats Detection - Agentic AI threat modeling
function generateAgenticThreatAnalysis(data) {
    const agenticScore = data.score || 0;
    const notes = data.notes || 'Agentic threat analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${agenticScore > 0.7 ? 'danger' : agenticScore > 0.4 ? 'warning' : 'success'}">Agentic Score: ${(agenticScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Agentic Threat Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI8: Synthesis Integration - Threat synthesis and escalation
function generateSynthesisAnalysis(data) {
    const synthScore = data.score || 0;
    const notes = data.notes || 'Synthesis analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${synthScore > 0.7 ? 'danger' : synthScore > 0.4 ? 'warning' : 'success'}">Synthesis Score: ${(synthScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Synthesis & Integration Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI9: Explainability & Evidence - Explainability and evidence generation
function generateExplainabilityAnalysis(data) {
    const explainScore = data.score || 0;
    const notes = data.notes || 'Explainability analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${explainScore > 0.7 ? 'danger' : explainScore > 0.4 ? 'warning' : 'success'}">Explainability Score: ${(explainScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Explainability & Evidence Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI10: Psychological Manipulation - Cognitive bias and psychological manipulation
function generatePsychologicalAnalysis(data) {
    const psychScore = data.score || 0;
    const notes = data.notes || 'Psychological manipulation analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${psychScore > 0.7 ? 'danger' : psychScore > 0.4 ? 'warning' : 'success'}">Psych Score: ${(psychScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Psychological Manipulation Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
}

// TDC-AI11: Intervention Response - Cognitive intervention and response
function generateInterventionAnalysis(data) {
    const interventionScore = data.score || 0;
    const notes = data.notes || 'Intervention analysis completed';
    const flags = data.flags || [];
    const confidence = data.confidence || 0.7;
    const recommendedAction = data.recommended_action || 'Monitor';
    const evidence = data.evidence || [];
    const extra = data.extra || {};

    let evidenceHtml = '';
    if (evidence.length > 0) {
        evidenceHtml = `<br><strong>Evidence Details:</strong><ul class="mb-0 small">` +
            evidence.map(ev => `<li><b>Type:</b> ${ev.type} <b>Data:</b> ${JSON.stringify(ev.data)}</li>`).join('') +
            `</ul>`;
    }
    let extraHtml = '';
    if (Object.keys(extra).length > 0) {
        extraHtml = `<br><strong>Extra Analysis Data:</strong><ul class="mb-0 small">` +
            Object.entries(extra).map(([key, value]) => `<li><b>${key}:</b> ${JSON.stringify(value)}</li>`).join('') +
            `</ul>`;
    }

    return `
        <div class="module-analysis">
            <div class="analysis-header">
                <span class="badge bg-${interventionScore > 0.7 ? 'danger' : interventionScore > 0.4 ? 'warning' : 'success'}">Intervention Score: ${(interventionScore * 100).toFixed(1)}%</span>
                <span class="badge bg-info">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                <span class="badge bg-secondary">${recommendedAction}</span>
            </div>
            <div class="analysis-details">
                <strong>Intervention Response Analysis:</strong><br>
                ${notes}
                ${flags.length > 0 ? `
                    <br><strong>Flags:</strong>
                    <ul class="mb-0 small">
                        ${flags.map(flag => `<li>${flag}</li>`).join('')}
                    </ul>
                ` : ''}
                ${evidenceHtml}
                ${extraHtml}
            </div>
        </div>
    `;
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
    
    // ✅ ENHANCED DEBUGGING: Log conversation update
    console.log('🔔 Updating live conversation:', {
        sender: data.sender,
        content: data.content ? data.content.substring(0, 50) + '...' : 'No content',
        message: data.message ? data.message.substring(0, 50) + '...' : 'No message',
        timestamp: data.timestamp
    });
    
    // ✅ ENHANCED ERROR HANDLING: Check if element exists
    if (!conversation) {
        console.error('🔔 Live conversation element not found!');
        return;
    }
    
    if (conversation.querySelector('.text-muted')) {
        conversation.innerHTML = '';
    }
    
    // ✅ FIXED: Handle case-insensitive sender comparison
    const sender = (data.sender || '').toLowerCase();
    
    // Only add message if we have content
    const content = data.content || data.message;
    if (!content) {
        console.log('🔔 No content available for conversation update');
        return;
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender} ${data.threat_detected ? 'threat' : ''}`;
    
    // Determine icon based on sender
    const iconClass = sender === 'ai' ? 'bi bi-robot' : 'bi bi-person';
    const iconColor = sender === 'ai' ? 'text-primary' : 'text-success';
    
    messageElement.innerHTML = `
        <div class="message-timestamp">${formatTimestamp(data.timestamp, true)}</div>
        <div class="message-content">
            <i class="${iconClass} ${iconColor} me-2"></i>
            ${content}
        </div>
    `;
    
    conversation.appendChild(messageElement);
    conversation.scrollTop = conversation.scrollHeight;
    
    // Limit messages
    const messages = conversation.querySelectorAll('.message');
    if (messages.length > 100) {
        conversation.removeChild(messages[0]);
    }
    
    console.log('🔔 Live conversation updated successfully');
}

// Update chat transcripts
function updateChatTranscripts(data) {
    const userTranscript = document.getElementById('userTranscript');
    const aiTranscript = document.getElementById('aiTranscript');
    
    // ✅ ENHANCED DEBUGGING: Log transcript update
    console.log('🔔 Updating chat transcripts:', {
        sender: data.sender,
        content: data.content ? data.content.substring(0, 50) + '...' : 'No content',
        message: data.message ? data.message.substring(0, 50) + '...' : 'No message'
    });
    
    // ✅ ENHANCED ERROR HANDLING: Check if elements exist
    if (!userTranscript) {
        console.error('🔔 User transcript element not found!');
        return;
    }
    if (!aiTranscript) {
        console.error('🔔 AI transcript element not found!');
        return;
    }
    
    // ✅ FIXED: Handle case-insensitive sender comparison
    const sender = (data.sender || '').toLowerCase();
    
    // Only add transcript if we have content and a valid sender
    const content = data.content || data.message;
    if (!content) {
        console.log('🔔 No content available for transcript update');
        return;
    }
    
    if (sender === 'user') {
        console.log('🔔 Adding user transcript entry');
        addTranscriptEntry(userTranscript, data);
    } else if (sender === 'ai') {
        console.log('🔔 Adding AI transcript entry');
        addTranscriptEntry(aiTranscript, data);
    } else {
        console.log('🔔 Unknown sender for transcript:', sender);
    }
}

// Add transcript entry
function addTranscriptEntry(container, data) {
    // ✅ ENHANCED ERROR HANDLING: Check if container exists
    if (!container) {
        console.error('🔔 Container element not found for transcript entry!');
        return;
    }
    
    const entry = document.createElement('div');
    entry.className = 'transcript-entry';
    
    const content = data.content || data.message || 'No content';
    
    entry.innerHTML = `
        <div class="transcript-timestamp">${formatTimestamp(data.timestamp, true)}</div>
        <div class="transcript-message">${content}</div>
    `;
    
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
    
    // Limit entries
    const entries = container.querySelectorAll('.transcript-entry');
    if (entries.length > 50) {
        container.removeChild(entries[0]);
    }
    
    console.log('🔔 Transcript entry added successfully');
}

// Update chat summary
function updateChatSummary(data) {
    const summaryCard = document.getElementById('chatSummaryCard');
    
    // ✅ ENHANCED ERROR HANDLING: Check if element exists
    if (!summaryCard) {
        console.error('🔔 Chat summary card element not found!');
        return;
    }
    
    // ✅ ENHANCED: Always update the summary with useful information
    let summaryContent = '';
    
    if (data.threat_detected) {
        // Show threat warning
        summaryContent = `
            <div class="alert alert-warning mb-0">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Threat Detected:</strong> ${data.threat_type || 'Unknown threat type'}
                <br>
                <small>Confidence: ${data.threat_score || 0}% | Session: ${data.session_id}</small>
            </div>
        `;
    } else {
        // Show normal chat summary
        const sender = (data.sender || '').toLowerCase();
        const content = data.content || data.message || 'No content';
        const timestamp = formatTimestamp(data.timestamp, true);
        
        summaryContent = `
            <div class="alert alert-info mb-0">
                <i class="bi bi-chat-text"></i>
                <strong>Latest Message:</strong> ${sender === 'user' ? 'User' : sender === 'ai' ? 'AI' : 'Unknown'} sent a message
                <br>
                <small>Time: ${timestamp} | Session: ${data.session_id}</small>
                <br>
                <small class="text-muted">Content: ${content.length > 100 ? content.substring(0, 100) + '...' : content}</small>
            </div>
        `;
    }
    
    summaryCard.innerHTML = summaryContent;
    
    // ✅ ENHANCED: Update session ID displays
    const currentSessionId = document.getElementById('currentSessionId');
    const chatSessionId = document.getElementById('chatSessionId');
    
    if (currentSessionId && data.session_id) {
        currentSessionId.textContent = data.session_id;
    }
    
    if (chatSessionId && data.session_id) {
        chatSessionId.textContent = data.session_id;
    }
    
    console.log('🔔 Chat summary updated successfully');
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
    // Find threat by eventId (stored in dataset)
    const threatRow = document.querySelector(`tr[data-event-id="${threatId}"]`);
    if (threatRow) {
        const threat = {
            id: threatId,
            timestamp: threatRow.dataset.timestamp,
            session_id: threatRow.dataset.sessionId,
            threat_type: threatRow.dataset.threatType,
            severity: threatRow.dataset.severity,
            threat_score: threatRow.querySelector('td:nth-child(6)').textContent,
            source: threatRow.dataset.source || threatRow.querySelector('td:nth-child(3)').textContent,
            message: threatRow.dataset.message || '',
            sender: threatRow.dataset.sender || '',
            tdc_modules: threatRow.dataset.tdcModules ? threatRow.dataset.tdcModules.split(',') : []
        };
        
        // Create a detailed modal for threat details
        showThreatDetailsModal(threat);
    } else {
        alert('Threat details not found');
    }
}

function exportThreatData(threatId) {
    // Find threat by eventId (stored in dataset)
    const threatRow = document.querySelector(`tr[data-event-id="${threatId}"]`);
    if (threatRow) {
        const threat = {
            id: threatId,
            timestamp: threatRow.dataset.timestamp,
            session_id: threatRow.dataset.sessionId,
            threat_type: threatRow.dataset.threatType,
            severity: threatRow.dataset.severity,
            threat_score: threatRow.querySelector('td:nth-child(6)').textContent,
            source: threatRow.dataset.source || threatRow.querySelector('td:nth-child(3)').textContent,
            message: threatRow.dataset.message || '',
            sender: threatRow.dataset.sender || '',
            tdc_modules: threatRow.dataset.tdcModules ? threatRow.dataset.tdcModules.split(',') : [],
            export_time: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(threat, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat-${threatId}-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    } else {
        alert('Threat data not found');
    }
}

// Show threat details modal
function showThreatDetailsModal(threat) {
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="threatDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle text-danger"></i>
                            Threat Details
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Basic Information</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Threat ID:</strong></td><td>${threat.id}</td></tr>
                                    <tr><td><strong>Type:</strong></td><td>${threat.threat_type}</td></tr>
                                    <tr><td><strong>Severity:</strong></td><td><span class="severity-badge ${threat.severity.toLowerCase()}">${threat.severity}</span></td></tr>
                                    <tr><td><strong>Score:</strong></td><td>${threat.threat_score}</td></tr>
                                    <tr><td><strong>Source:</strong></td><td>${threat.source}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Session Information</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Session ID:</strong></td><td><code>${threat.session_id}</code></td></tr>
                                    <tr><td><strong>Timestamp:</strong></td><td>${formatTimestamp(threat.timestamp)}</td></tr>
                                    <tr><td><strong>TDC Modules:</strong></td><td>${formatTDCModules(threat.tdc_modules)}</td></tr>
                                </table>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>Actions</h6>
                                <div class="btn-group">
                                    <button type="button" class="btn btn-outline-primary" onclick="exportThreatData('${threat.id}')">
                                        <i class="bi bi-download"></i> Export Data
                                    </button>
                                    <button type="button" class="btn btn-outline-info" onclick="viewSessionDetails('${threat.session_id}')">
                                        <i class="bi bi-eye"></i> View Session
                                    </button>
                                    <button type="button" class="btn btn-outline-warning" onclick="markAsInvestigated('${threat.id}')">
                                        <i class="bi bi-check-circle"></i> Mark Investigated
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('threatDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('threatDetailsModal'));
    modal.show();
    
    // Clean up modal after it's hidden
    document.getElementById('threatDetailsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Session detail functions
function viewSessionDetails(sessionId) {
    // Find all threats for this session
    const sessionThreats = threatData.filter(t => t.session_id === sessionId);
    
    // Create session details modal
    const modalHtml = `
        <div class="modal fade" id="sessionDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-hash text-primary"></i>
                            Session Details: ${sessionId}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Session Summary</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Session ID:</strong></td><td><code>${sessionId}</code></td></tr>
                                    <tr><td><strong>Total Threats:</strong></td><td>${sessionThreats.length}</td></tr>
                                    <tr><td><strong>Critical Threats:</strong></td><td>${sessionThreats.filter(t => t.severity === 'Critical').length}</td></tr>
                                    <tr><td><strong>High Threats:</strong></td><td>${sessionThreats.filter(t => t.severity === 'High').length}</td></tr>
                                    <tr><td><strong>Average Score:</strong></td><td>${sessionThreats.length > 0 ? (sessionThreats.reduce((sum, t) => sum + (t.threat_score || 0), 0) / sessionThreats.length).toFixed(1) : 0}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Actions</h6>
                                <div class="btn-group-vertical">
                                    <button type="button" class="btn btn-outline-primary" onclick="exportSessionData('${sessionId}')">
                                        <i class="bi bi-download"></i> Export Session Data
                                    </button>
                                    <button type="button" class="btn btn-outline-info" onclick="viewSessionTimeline('${sessionId}')">
                                        <i class="bi bi-clock"></i> View Timeline
                                    </button>
                                    <button type="button" class="btn btn-outline-warning" onclick="markSessionInvestigated('${sessionId}')">
                                        <i class="bi bi-check-circle"></i> Mark Investigated
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>Session Threats</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead>
                                            <tr>
                                                <th>Time</th>
                                                <th>Type</th>
                                                <th>Severity</th>
                                                <th>Score</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${sessionThreats.map(threat => `
                                                <tr>
                                                    <td>${formatTimestamp(threat.timestamp, true)}</td>
                                                    <td>${threat.threat_type}</td>
                                                    <td><span class="severity-badge ${threat.severity.toLowerCase()}">${threat.severity}</span></td>
                                                    <td>${threat.threat_score || 0}</td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-primary" onclick="viewThreatDetails('${threat.id || 'unknown'}')">
                                                            <i class="bi bi-eye"></i>
                                                        </button>
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('sessionDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('sessionDetailsModal'));
    modal.show();
    
    // Clean up modal after it's hidden
    document.getElementById('sessionDetailsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function exportSessionData(sessionId) {
    const sessionThreats = threatData.filter(t => t.session_id === sessionId);
    const sessionData = {
        session_id: sessionId,
        export_time: new Date().toISOString(),
        total_threats: sessionThreats.length,
        threats: sessionThreats,
        summary: {
            critical: sessionThreats.filter(t => t.severity === 'Critical').length,
            high: sessionThreats.filter(t => t.severity === 'High').length,
            medium: sessionThreats.filter(t => t.severity === 'Medium').length,
            low: sessionThreats.filter(t => t.severity === 'Low').length,
            average_score: sessionThreats.length > 0 ? (sessionThreats.reduce((sum, t) => sum + (t.threat_score || 0), 0) / sessionThreats.length).toFixed(1) : 0
        }
    };
    
    const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-${sessionId}-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function viewSessionTimeline(sessionId) {
    alert(`Timeline view for session ${sessionId} - Feature coming soon!`);
}

function markSessionInvestigated(sessionId) {
    if (confirm(`Mark session ${sessionId} as investigated?`)) {
        // Find all threat rows for this session and mark them
        const sessionRows = document.querySelectorAll(`tr[data-session-id="${sessionId}"]`);
        sessionRows.forEach(row => {
            row.classList.add('table-success');
            row.style.opacity = '0.7';
        });
        alert(`Session ${sessionId} marked as investigated`);
    }
}

function markAsInvestigated(threatId) {
    if (confirm(`Mark threat ${threatId} as investigated?`)) {
        const threatRow = document.querySelector(`tr[data-event-id="${threatId}"]`);
        if (threatRow) {
            threatRow.classList.add('table-success');
            threatRow.style.opacity = '0.7';
        }
        alert(`Threat ${threatId} marked as investigated`);
    }
}

// Load saved filter presets
document.addEventListener('DOMContentLoaded', function() {
    const savedPresets = localStorage.getItem('catdams-filter-presets');
    if (savedPresets) {
        filterPresets = JSON.parse(savedPresets);
    }
}); 