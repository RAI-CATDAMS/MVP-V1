console.log('dashboard.js loaded');
// CATDAMS Enhanced Dashboard JS
// Phase 1, Step 1.1: Enhanced JavaScript Core Implementation

// === Enhanced Configuration ===
const CONFIG = {
    // WebSocket settings
    WS_URL: "ws://localhost:8000/ws",
    WS_RECONNECT_INTERVAL: 3000,
    WS_MAX_RECONNECT_ATTEMPTS: 10,
    WS_HEARTBEAT_INTERVAL: 30000,
    
    // API endpoints
    API_BASE_URL: "http://localhost:8000/api/analytics",
    
    // Performance settings
    UPDATE_QUEUE_BATCH_SIZE: 10,
    UPDATE_QUEUE_FLUSH_INTERVAL: 16, // ~60fps
    MEMORY_CLEANUP_INTERVAL: 60000, // 1 minute
    PERFORMANCE_MONITORING: true,
    
    // Chart update settings
    CHART_UPDATE_THROTTLE: 100, // ms
    DOM_UPDATE_BATCH_SIZE: 5
};

// === Enhanced WebSocket Management ===
class EnhancedWebSocket {
    constructor(url, config) {
        this.url = url;
        this.config = config;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.heartbeatTimer = null;
        this.isConnecting = false;
        this.messageQueue = [];
        this.onMessageCallbacks = [];
        this.onConnectCallbacks = [];
        this.onDisconnectCallbacks = [];
        
        this.connect();
    }
    
    connect() {
        if (this.isConnecting) return;
        this.isConnecting = true;
        
        try {
            this.ws = new WebSocket(this.url);
            this.setupEventHandlers();
        } catch (error) {
            console.error('[CATDAMS] WebSocket connection failed:', error);
            this.handleReconnect();
        }
    }
    
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('[CATDAMS] WebSocket connected successfully');
            this.isConnecting = false;
            this.reconnectAttempts = 0;
            this.startHeartbeat();
            this.flushMessageQueue();
            this.onConnectCallbacks.forEach(callback => callback());
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Handle heartbeat responses
                if (data.type === 'heartbeat_response') {
                    console.log('[CATDAMS] Heartbeat response received');
                    // Reset heartbeat timer on successful response
                    this.resetHeartbeat();
                    return;
                }
                
                this.onMessageCallbacks.forEach(callback => callback(data));
            } catch (error) {
                console.error('[CATDAMS] Failed to parse WebSocket message:', error);
            }
        };
        
        this.ws.onclose = (event) => {
            console.log('[CATDAMS] WebSocket connection closed:', event.code, event.reason);
            this.isConnecting = false;
            this.stopHeartbeat();
            this.onDisconnectCallbacks.forEach(callback => callback(event));
            
            if (event.code !== 1000) { // Not a normal closure
                this.handleReconnect();
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('[CATDAMS] WebSocket error:', error);
            this.isConnecting = false;
        };
    }
    
    handleReconnect() {
        if (this.reconnectAttempts >= this.config.WS_MAX_RECONNECT_ATTEMPTS) {
            console.error('[CATDAMS] Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`[CATDAMS] Attempting to reconnect (${this.reconnectAttempts}/${this.config.WS_MAX_RECONNECT_ATTEMPTS})...`);
        
        setTimeout(() => {
            this.connect();
        }, this.config.WS_RECONNECT_INTERVAL);
    }
    
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat', timestamp: Date.now() }));
            }
        }, this.config.WS_HEARTBEAT_INTERVAL);
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    resetHeartbeat() {
        // Reset the heartbeat timer to prevent timeout
        this.stopHeartbeat();
        this.startHeartbeat();
    }
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            this.messageQueue.push(data);
        }
    }
    
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }
    
    onMessage(callback) {
        this.onMessageCallbacks.push(callback);
    }
    
    onConnect(callback) {
        this.onConnectCallbacks.push(callback);
    }
    
    onDisconnect(callback) {
        this.onDisconnectCallbacks.push(callback);
    }
    
    disconnect() {
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.close(1000, 'Normal closure');
        }
    }
}

// === Performance-Optimized Update Queue System ===
class UpdateQueue {
    constructor(config) {
        this.config = config;
        this.queue = [];
        this.isProcessing = false;
        this.lastFlush = 0;
        this.updateCallbacks = new Map();
        this.performanceMetrics = {
            totalUpdates: 0,
            averageProcessingTime: 0,
            queueSize: 0,
            lastOptimization: Date.now()
        };
    }
    
    addUpdate(type, data, priority = 0) {
        this.queue.push({
            type,
            data,
            priority,
            timestamp: Date.now(),
            id: Math.random().toString(36).substr(2, 9)
        });
        
        this.performanceMetrics.totalUpdates++;
        this.performanceMetrics.queueSize = this.queue.length;
        
        // Sort by priority (higher priority first)
        this.queue.sort((a, b) => b.priority - a.priority);
        
        if (!this.isProcessing) {
            this.processQueue();
        }
    }
    
    processQueue() {
        if (this.isProcessing || this.queue.length === 0) return;
        
        this.isProcessing = true;
        const startTime = performance.now();
        
        // Process batch of updates
        const batch = this.queue.splice(0, this.config.UPDATE_QUEUE_BATCH_SIZE);
        
        requestAnimationFrame(() => {
            try {
                batch.forEach(update => {
                    const callback = this.updateCallbacks.get(update.type);
                    if (callback) {
                        callback(update.data);
                    }
                });
                
                const processingTime = performance.now() - startTime;
                this.performanceMetrics.averageProcessingTime = 
                    (this.performanceMetrics.averageProcessingTime + processingTime) / 2;
                
                // Schedule next batch if queue is not empty
                if (this.queue.length > 0) {
                    setTimeout(() => {
                        this.isProcessing = false;
                        this.processQueue();
                    }, this.config.UPDATE_QUEUE_FLUSH_INTERVAL);
                } else {
                    this.isProcessing = false;
                }
                
            } catch (error) {
                console.error('[CATDAMS] Error processing update queue:', error);
                this.isProcessing = false;
            }
        });
    }
    
    registerUpdateType(type, callback) {
        this.updateCallbacks.set(type, callback);
    }
    
    getMetrics() {
        return { ...this.performanceMetrics };
    }
    
    optimize() {
        // Remove old updates from queue to prevent memory leaks
        const now = Date.now();
        this.queue = this.queue.filter(update => 
            now - update.timestamp < 30000 // Keep only updates from last 30 seconds
        );
        
        this.performanceMetrics.lastOptimization = now;
        this.performanceMetrics.queueSize = this.queue.length;
    }
}

// === Memory Leak Prevention & Performance Monitoring ===
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            memoryUsage: 0,
            domNodes: 0,
            eventListeners: 0,
            chartUpdates: 0,
            lastCleanup: Date.now()
        };
        
        this.cleanupIntervals = [];
        this.eventListeners = new WeakMap();
        
        if (CONFIG.PERFORMANCE_MONITORING) {
            this.startMonitoring();
        }
    }
    
    startMonitoring() {
        // Monitor memory usage
        setInterval(() => {
            this.updateMemoryMetrics();
        }, 30000); // Every 30 seconds
        
        // Cleanup routine
        setInterval(() => {
            this.performCleanup();
        }, CONFIG.MEMORY_CLEANUP_INTERVAL);
        
        // Performance optimization
        setInterval(() => {
            this.optimizePerformance();
        }, 120000); // Every 2 minutes
    }
    
    updateMemoryMetrics() {
        if (performance.memory) {
            this.metrics.memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024; // MB
        }
        
        this.metrics.domNodes = document.querySelectorAll('*').length;
        
        // Log performance warnings
        if (this.metrics.memoryUsage > 100) { // > 100MB
            console.warn('[CATDAMS] High memory usage detected:', this.metrics.memoryUsage.toFixed(2), 'MB');
        }
        
        if (this.metrics.domNodes > 1000) { // > 1000 DOM nodes
            console.warn('[CATDAMS] High DOM node count detected:', this.metrics.domNodes);
        }
    }
    
    performCleanup() {
        // Clear old chart data
        if (threatLevelChart && threatLevelChart.data.datasets[0].data.length > 100) {
            threatLevelChart.data.datasets[0].data = threatLevelChart.data.datasets[0].data.slice(-50);
        }
        
        if (threatVectorChart && threatVectorChart.data.labels.length > 20) {
            threatVectorChart.data.labels = threatVectorChart.data.labels.slice(-10);
            threatVectorChart.data.datasets[0].data = threatVectorChart.data.datasets[0].data.slice(-10);
        }
        
        // Clear old messages (keep last 50)
        if (userMessages.length > 50) {
            userMessages.splice(0, userMessages.length - 50);
        }
        if (aiMessages.length > 50) {
            aiMessages.splice(0, aiMessages.length - 50);
        }
        
        // Clear old threat events (keep last 100)
        const threatTable = document.getElementById('threatEventsTable');
        if (threatTable) {
            const rows = threatTable.querySelectorAll('tbody tr');
            if (rows.length > 100) {
                for (let i = 0; i < rows.length - 100; i++) {
                    rows[i].remove();
                }
            }
        }
        
        this.metrics.lastCleanup = Date.now();
        console.log('[CATDAMS] Performance cleanup completed');
    }
    
    optimizePerformance() {
        // Optimize update queue
        if (updateQueue) {
            updateQueue.optimize();
        }
        
        // Force garbage collection if available
        if (window.gc) {
            window.gc();
        }
        
        console.log('[CATDAMS] Performance optimization completed');
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
}

// === Initialize Enhanced Components ===
let enhancedWebSocket;
let updateQueue;
let performanceMonitor;

// === Chart.js Chart Variables ===
let threatLevelChart, threatVectorChart;
let threatLevelCounts = { 'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0 };
let threatVectorCounts = {};

// === Chat Transcript State ===
let chatSummary = '';
let userMessages = [];
let aiMessages = [];
let currentSessionId = '';

// === Dark Theme Management ===
function toggleDarkTheme() {
    const body = document.body;
    const themeToggle = document.querySelector('.theme-toggle i');
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        // Switch to light theme
        body.classList.remove('dark-theme');
        localStorage.setItem('catdams-theme', 'light');
        themeToggle.className = 'bi bi-moon-stars';
        console.log('[CATDAMS] Switched to light theme');
    } else {
        // Switch to dark theme
        body.classList.add('dark-theme');
        localStorage.setItem('catdams-theme', 'dark');
        themeToggle.className = 'bi bi-sun';
        console.log('[CATDAMS] Switched to dark theme');
    }
    
    // Trigger custom event for theme change
    window.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { theme: isDark ? 'light' : 'dark' } 
    }));
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('catdams-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const themeToggle = document.querySelector('.theme-toggle i');
    
    // Apply saved theme or system preference
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-theme');
        if (themeToggle) {
            themeToggle.className = 'bi bi-sun';
        }
        console.log('[CATDAMS] Applied dark theme');
    } else {
        document.body.classList.remove('dark-theme');
        if (themeToggle) {
            themeToggle.className = 'bi bi-moon-stars';
        }
        console.log('[CATDAMS] Applied light theme');
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('catdams-theme')) {
            if (e.matches) {
                document.body.classList.add('dark-theme');
                if (themeToggle) {
                    themeToggle.className = 'bi bi-sun';
                }
            } else {
                document.body.classList.remove('dark-theme');
                if (themeToggle) {
                    themeToggle.className = 'bi bi-moon-stars';
                }
            }
        }
    });
}

// === Enhanced Initialization ===
function initializeEnhancedDashboard() {
    console.log('[CATDAMS] Initializing enhanced dashboard components...');
    
    // Initialize enhanced WebSocket with correct config property names
    enhancedWebSocket = new EnhancedWebSocket(CONFIG.WS_URL, {
        WS_RECONNECT_INTERVAL: 5000,
        WS_MAX_RECONNECT_ATTEMPTS: 10,
        WS_HEARTBEAT_INTERVAL: 30000
    });
    
    // Initialize update queue with optimized settings
    updateQueue = new UpdateQueue({
        UPDATE_QUEUE_BATCH_SIZE: 10,
        UPDATE_QUEUE_FLUSH_INTERVAL: 100
    });
    
    // Register update types with the correct handlers
    updateQueue.registerUpdateType('summary', updateSummaryMetricsFromAPI);
    updateQueue.registerUpdateType('chat', updateChatSummaryAndTranscripts);
    updateQueue.registerUpdateType('threat', addThreatEvent);
    updateQueue.registerUpdateType('tdc', renderTDCModules);
    updateQueue.registerUpdateType('session', handleSessionUpdate);
    
    // Initialize performance monitor
    performanceMonitor = new PerformanceMonitor();
    performanceMonitor.startMonitoring();
    
    // Setup WebSocket event handlers
    enhancedWebSocket.onMessage((data) => {
        try {
            const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
            console.log('[CATDAMS] WebSocket message received:', parsedData);
            
            // Add to update queue for processing
            updateQueue.addUpdate('session', parsedData, 1);
            
            // Also handle immediate updates for critical data
            if (parsedData.threat_analysis || parsedData.escalation) {
                addThreatEvent(parsedData);
            }
            if (parsedData.raw_user || parsedData.raw_ai) {
                updateChatSummaryAndTranscripts(parsedData);
            }
        } catch (error) {
            console.error('[CATDAMS] Error processing WebSocket message:', error);
        }
    });
    
    enhancedWebSocket.onConnect(() => {
        console.log('[CATDAMS] WebSocket connected');
        updateConnectionStatus(true);
    });
    
    enhancedWebSocket.onDisconnect(() => {
        console.log('[CATDAMS] WebSocket disconnected');
        updateConnectionStatus(false);
    });
    
    // Connect WebSocket
    enhancedWebSocket.connect();
    
    // Start processing updates
    updateQueue.processQueue();
    
    console.log('[CATDAMS] Enhanced dashboard initialization complete');
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.status-indicator i.bi-circle-fill');
    if (statusIndicator) {
        statusIndicator.className = `bi bi-circle-fill text-${connected ? 'success' : 'danger'}`;
    }
}

// === Chart Initialization ===
function initCharts() {
  const threatLevelCtx = document.getElementById('threatLevelChart');
  if (!threatLevelCtx) {
    console.warn('threatLevelChart canvas not found');
    return;
  }
  
  threatLevelChart = new Chart(threatLevelCtx.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [0, 0, 0, 0],
        backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#198754'],
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' }
      },
      cutout: '70%',
      responsive: true,
      maintainAspectRatio: false
    }
  });

  const threatVectorCtx = document.getElementById('threatVectorChart');
  if (!threatVectorCtx) {
    console.warn('threatVectorChart canvas not found');
    return;
  }
  
  threatVectorChart = new Chart(threatVectorCtx.getContext('2d'), {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Count',
        data: [],
        backgroundColor: '#0077b6',
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false }
      },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true }
      }
    }
  });
}

// === Chart Data Update Functions ===
function updateChartsWithEvent(data) {
  // --- Threat Level ---
  const level = (data.threat_level || data.severity || '').toString();
  if (['Critical', 'High', 'Medium', 'Low'].includes(level)) {
    threatLevelCounts[level] = (threatLevelCounts[level] || 0) + 1;
    if (threatLevelChart) {
      threatLevelChart.data.datasets[0].data = [
        threatLevelCounts['Critical'],
        threatLevelCounts['High'],
        threatLevelCounts['Medium'],
        threatLevelCounts['Low']
      ];
      threatLevelChart.update('none');
    }
  }
  // --- Threat Vector ---
  const vector = (data.threat_vector || '').toString();
  if (vector && vector !== 'Unknown') {
    threatVectorCounts[vector] = (threatVectorCounts[vector] || 0) + 1;
    if (threatVectorChart) {
      // Sort by count descending, show top 7
      const sorted = Object.entries(threatVectorCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 7);
      threatVectorChart.data.labels = sorted.map(([label]) => label);
      threatVectorChart.data.datasets[0].data = sorted.map(([, count]) => count);
      threatVectorChart.update('none');
    }
  }
}

// === TDC Modules Grid Logic ===
function renderTDCModules(data) {
  const grid = document.getElementById('tdcModulesGrid');
  if (!grid) return;
  grid.innerHTML = '';

  // Helper to create a module card with consistent formatting
  function createModuleCard(id, title, moduleData, expanded = false) {
    const card = document.createElement('div');
    card.className = 'col-md-3';
    
    // Handle both new ModuleOutput schema and legacy format
    let score = 0;
    let confidence = 0;
    let notes = 'No analysis available';
    let recommendedAction = 'Monitor';
    let flags = [];
    let schemaVersion = null;
    let analysisType = 'unknown';
    
    if (moduleData) {
      // Check if it's ModuleOutput schema
      if (moduleData.schema_version && moduleData.module_name) {
        // New ModuleOutput schema
        score = moduleData.score || 0;
        confidence = moduleData.confidence || 0;
        notes = moduleData.notes || 'No analysis available';
        recommendedAction = moduleData.recommended_action || 'Monitor';
        flags = moduleData.flags || [];
        schemaVersion = moduleData.schema_version;
        analysisType = moduleData.extra?.analysis_type || 'unknown';
      } else {
        // Legacy format - extract data based on module type
        if (id === 'tdc-ai1') {
          score = moduleData.risk_score || 0;
          notes = moduleData.risk_summary || 'No risk analysis available';
        } else if (id === 'tdc-ai2') {
          score = moduleData.flagged ? 0.8 : 0.2;
          notes = moduleData.summary || 'No AI response analysis available';
        } else if (id === 'tdc-ai3') {
          score = moduleData.temporal_risk_score || 0;
          notes = moduleData.summary || 'No temporal analysis available';
        } else if (id === 'tdc-ai4') {
          score = moduleData.synthesis_score || 0;
          notes = moduleData.summary || 'No synthesis analysis available';
          flags = moduleData.key_flags || [];
        } else if (id === 'tdc-ai5') {
          score = moduleData.amic_score || 0;
          notes = `Influence Level: ${moduleData.influence_level || 'Unknown'}`;
        } else if (id === 'tdc-ai6') {
          score = moduleData.aipc_score || 0;
          notes = moduleData.summary || 'No pattern classification available';
        } else if (id === 'tdc-ai7') {
          score = moduleData.airm_score || 0;
          notes = `Susceptibility Level: ${moduleData.susceptibility_level || 'Unknown'}`;
        } else if (id === 'tdc-ai8') {
          score = moduleData.synthesis_score || 0;
          notes = moduleData.summary || 'No synthesis available';
        }
      }
    }
    
    // Format score as percentage or scale
    const scoreDisplay = score <= 1 ? `${Math.round(score * 100)}%` : `${Math.round(score)}/10`;
    const confidenceDisplay = confidence <= 1 ? `${Math.round(confidence * 100)}%` : `${Math.round(confidence)}%`;
    
    // Get action color
    const actionColor = getActionColor(recommendedAction);
    
    // Format flags
    const flagsDisplay = flags.length > 0 ? flags.slice(0, 3).join(', ') + (flags.length > 3 ? '...' : '') : 'None';
    
    const content = `
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <strong>Score:</strong> <span class="badge bg-${score > 0.7 ? 'danger' : score > 0.4 ? 'warning' : 'success'}">${scoreDisplay}</span>
          ${confidence > 0 ? `<strong>Confidence:</strong> <span class="badge bg-${confidence > 0.8 ? 'success' : confidence > 0.5 ? 'warning' : 'secondary'}">${confidenceDisplay}</span>` : ''}
        </div>
        <span class="badge bg-${actionColor}">${recommendedAction}</span>
      </div>
      <div class="mb-2">
        <strong>Summary:</strong> <span class="text-muted">${notes.length > 100 ? notes.substring(0, 100) + '...' : notes}</span>
      </div>
      ${flags.length > 0 ? `<div class="mb-2">
        <strong>Flags:</strong> <span class="text-muted">${flagsDisplay}</span>
      </div>` : ''}
      <div class="small text-muted">
        <strong>Type:</strong> ${analysisType} ${schemaVersion ? `| Schema: v${schemaVersion}` : ''}
      </div>
    `;
    
    card.innerHTML = `
      <div class="card tdc-module-card mb-2">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span class="fw-bold">${title}</span>
          <button class="btn btn-sm btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${id}" aria-expanded="${expanded}" aria-controls="${id}">
            <i class="bi bi-chevron-${expanded ? 'up' : 'down'}"></i>
          </button>
        </div>
        <div id="${id}" class="collapse${expanded ? ' show' : ''}">
          <div class="card-body small">${content}</div>
        </div>
      </div>
    `;
    return card;
  }

  // TDC AI1-8 Modules with proper data mapping
  const modules = [
    {
      id: 'tdc-ai1',
      title: 'TDC-AI1: Risk Analysis',
      data: data.ai_analysis
    },
    {
      id: 'tdc-ai2',
      title: 'TDC-AI2: AI Response',
      data: data.tdc_ai2_airs
    },
    {
      id: 'tdc-ai3',
      title: 'TDC-AI3: User Vulnerability',
      data: data.tdc_ai3_temporal
    },
    {
      id: 'tdc-ai4',
      title: 'TDC-AI4: Deep Synthesis',
      data: data.tdc_ai4_synthesis
    },
    {
      id: 'tdc-ai5',
      title: 'TDC-AI5: LLM Influence',
      data: data.tdc_ai5_amic
    },
    {
      id: 'tdc-ai6',
      title: 'TDC-AI6: Pattern Classification',
      data: data.tdc_ai6_classification
    },
    {
      id: 'tdc-ai7',
      title: 'TDC-AI7: Explainability',
      data: data.tdc_ai7_airm
    },
    {
      id: 'tdc-ai8',
      title: 'TDC-AI8: Synthesis',
      data: data.user_sentiment // Note: AI8 now handles synthesis, not sentiment
    }
  ];

  modules.forEach(m => {
    const card = createModuleCard(m.id, m.title, m.data);
    grid.appendChild(card);
  });
}

function logActivity(data) {
  // Simplified activity logging - removed dependency on missing activityFeed
  console.log(`[${data.timestamp || new Date().toISOString()}] Activity:`, data);
}

function updateSummaryMetricsFromAPI(data) {
    // Only update if we have a valid summary object
    if (!data || (!data.session_analysis && !data.threat_analysis)) {
        console.warn('[CATDAMS] Skipping summary update: no summary data in payload');
        return;
    }
    console.log('[DEBUG] API data received in updateSummaryMetricsFromAPI:', data);
    // Update summary cards
    const sessionAnalysis = data.session_analysis || {};
    const threatAnalysis = data.threat_analysis || {};
    // Update session metrics
    updateMetricCard('totalSessions', sessionAnalysis.total_sessions || 0);
    updateMetricCard('totalEvents', sessionAnalysis.total_events || 0);
    updateMetricCard('avgEventsPerSession', sessionAnalysis.avg_events_per_session || 0);
    // Update threat metrics
    updateMetricCard('totalThreats', threatAnalysis.total_threats || 0);
    updateMetricCard('criticalThreats', threatAnalysis.critical_threats || 0);
    updateMetricCard('avgThreatScore', threatAnalysis.avg_threat_score || 0);
}

function getActionColor(action) {
  switch(action?.toLowerCase()) {
    case 'immediate_action': return 'danger';
    case 'monitor': return 'warning';
    case 'investigate': return 'info';
    default: return 'secondary';
  }
}

function getSusceptibilityColor(score) {
  if (score >= 0.7) return 'danger';
  if (score >= 0.4) return 'warning';
  return 'success';
}

function addThreatEvent(data) {
    const table = document.getElementById("threatEventsTable");
    if (!table) return;
    
    const row = document.createElement("tr");
    
    // Time
    const timeCell = document.createElement("td");
    timeCell.textContent = data.timestamp || new Date().toLocaleTimeString();
    row.appendChild(timeCell);
    
    // Session ID - Make it clickable
    const sessionIdCell = document.createElement("td");
    const sessionId = data.session_id || '';
    if (sessionId) {
        const sessionLink = document.createElement("a");
        sessionLink.href = "#";
        sessionLink.textContent = sessionId;
        sessionLink.className = "text-primary fw-bold";
        sessionLink.style.cursor = "pointer";
        sessionLink.title = "Click to view session conversation";
        sessionLink.onclick = (e) => {
            e.preventDefault();
            showSessionConversation(sessionId, data);
        };
        sessionIdCell.appendChild(sessionLink);
    } else {
        sessionIdCell.textContent = sessionId;
    }
    row.appendChild(sessionIdCell);
    
    // Source
    const sourceCell = document.createElement("td");
    sourceCell.textContent = data.source || data.ai_source || "Unknown";
    row.appendChild(sourceCell);
    
    // Threat Type
    const threatTypeCell = document.createElement("td");
    const threatType = data.threat_vector || data.threat_analysis?.threats?.[0]?.type || data.type_indicator || "Unknown";
    threatTypeCell.textContent = threatType;
    row.appendChild(threatTypeCell);
    
    // Severity
    const severityCell = document.createElement("td");
    const severity = data.threat_analysis?.severity || data.escalation || data.severity || "Low";
    const severityBadge = document.createElement("span");
    severityBadge.className = `badge bg-${getSeverityColor(severity)}`;
    severityBadge.textContent = severity;
    severityCell.appendChild(severityBadge);
    row.appendChild(severityCell);
    
    // Score
    const scoreCell = document.createElement("td");
    const score = data.threat_analysis?.risk_score || data.ai_analysis?.risk_score || data.threat_score || 0;
    scoreCell.textContent = Math.round(score * 100);
    row.appendChild(scoreCell);
    
    // TDC Modules
    const tdcCell = document.createElement("td");
    const tdcModules = getTDCAnalysisSummary(data);
    tdcCell.innerHTML = tdcModules;
    row.appendChild(tdcCell);
    
    // Actions (Analyze button)
    const actionsCell = document.createElement("td");
    const analyzeBtn = document.createElement("button");
    analyzeBtn.className = "btn btn-sm btn-outline-primary";
    analyzeBtn.textContent = "Analyze";
    analyzeBtn.onclick = () => showEventDetails(data);
    actionsCell.appendChild(analyzeBtn);
    row.appendChild(actionsCell);
    
    // Add row to table
    table.insertBefore(row, table.firstChild);
    
    // Keep only last 100 events
    const rows = table.querySelectorAll("tr");
    if (rows.length > 100) {
        table.removeChild(rows[rows.length - 1]);
    }
}

function getSeverityColor(severity) {
  switch(severity?.toLowerCase()) {
    case 'critical': return 'danger';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success';
    default: return 'secondary';
  }
}

function getTDCAnalysisSummary(data) {
  const modules = [];
  
  if (data.ai_analysis) modules.push("AI1");
  if (data.tdc_ai2_airs) modules.push("AI2");
  if (data.tdc_ai3_temporal) modules.push("AI3");
  if (data.tdc_ai4_synthesis) modules.push("AI4");
  if (data.tdc_ai5_amic) modules.push("AI5");
  if (data.tdc_ai6_classification) modules.push("AI6");
  if (data.tdc_ai7_airm) modules.push("AI7");
  if (data.user_sentiment) modules.push("AI8");
  
  return modules.map(m => `<span class="badge bg-primary me-1">${m}</span>`).join('');
}

function getTDCAnalysisDetails(data) {
  let details = '<div class="small">';

  // Collapsible Indicators Section (Scrollable)
  if (data.indicators && Array.isArray(data.indicators) && data.indicators.length > 0) {
    details += `
      <div class="accordion mb-2" id="indicatorsAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingIndicators">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseIndicators" aria-expanded="false" aria-controls="collapseIndicators">
              <i class="bi bi-exclamation-diamond me-2"></i>Indicators (${data.indicators.length})
            </button>
          </h2>
          <div id="collapseIndicators" class="accordion-collapse collapse" aria-labelledby="headingIndicators" data-bs-parent="#indicatorsAccordion">
            <div class="accordion-body p-2" style="max-height: 200px; overflow-y: auto;">
              <ul class="list-group list-group-flush">
                ${data.indicators.map(ind => `
                  <li class="list-group-item d-flex align-items-center">
                    <span class="badge rounded-pill bg-${ind.severity >= 8 ? 'danger' : ind.severity >= 5 ? 'warning' : 'info'} me-2"><i class="bi bi-flag"></i> ${ind.severity || ''}</span>
                    <span><strong>${ind.category || 'Unknown'}:</strong> ${ind.indicator || ind.evidence || 'N/A'}
                    <span class="text-muted small ms-2"><i class="bi bi-info-circle"></i> ${ind.context || ''}</span></span>
                  </li>
                `).join('')}
              </ul>
            </div>
          </div>
        </div>
      </div>
      <hr>
    `;
  }

  // Conversation Context Section
  if (data.conversation_context) {
    const ctx = data.conversation_context;
    details += `
      <div class="mb-2">
        <strong><i class="bi bi-chat-dots me-1"></i>Conversation Context:</strong><br>
        <span class="text-muted small">
          <i class="bi bi-collection"></i> Total: ${ctx.totalMessages || 0},
          <i class="bi bi-person"></i> User: ${ctx.userMessages || 0},
          <i class="bi bi-robot"></i> AI: ${ctx.aiMessages || 0},
          <i class="bi bi-exclamation-triangle"></i> Threats: ${ctx.recentThreats || 0},
          <i class="bi bi-clock"></i> Duration: ${ctx.sessionDuration || 0}s
        </span>
      </div>
      <hr>
    `;
  }

  // Collapsible TDC Module Summaries
  details += `
    <div class="accordion mb-2" id="tdcModulesAccordion">
      <div class="accordion-item">
        <h2 class="accordion-header" id="headingTDCModules">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTDCModules" aria-expanded="false" aria-controls="collapseTDCModules">
            <i class="bi bi-cpu me-2"></i>TDC Module Summaries
          </button>
        </h2>
        <div id="collapseTDCModules" class="accordion-collapse collapse" aria-labelledby="headingTDCModules" data-bs-parent="#tdcModulesAccordion">
          <div class="accordion-body p-2" style="max-height: 300px; overflow-y: auto;">
  `;
  if (data.ai_analysis) {
    details += `<strong>AI1 - Risk Analysis:</strong><br>`;
    if (data.ai_analysis.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.ai_analysis.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.ai_analysis.notes || "N/A"}<br>`;
      details += `Action: ${data.ai_analysis.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `Risk Score: ${Math.round((data.ai_analysis.risk_score || 0) * 100)}%<br>`;
      details += `Summary: ${data.ai_analysis.risk_summary || "N/A"}<br><br>`;
    }
  }
  if (data.tdc_ai2_airs) {
    details += `<strong>AI2 - AI Response:</strong><br>`;
    if (data.tdc_ai2_airs.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai2_airs.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai2_airs.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai2_airs.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `Status: ${data.tdc_ai2_airs.flagged ? "<span class='badge bg-danger'>FLAGGED</span>" : "<span class='badge bg-success'>CLEAR</span>"}<br>`;
      details += `Summary: ${data.tdc_ai2_airs.summary || "N/A"}<br><br>`;
    }
  }
  if (data.tdc_ai3_temporal) {
    details += `<strong>AI3 - User Vulnerability:</strong><br>`;
    if (data.tdc_ai3_temporal.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai3_temporal.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai3_temporal.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai3_temporal.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `Score: ${data.tdc_ai3_temporal.temporal_risk_score || "N/A"}<br>`;
      details += `Summary: ${data.tdc_ai3_temporal.summary || "N/A"}<br><br>`;
    }
  }
  if (data.tdc_ai4_synthesis) {
    details += `<strong>AI4 - Deep Synthesis:</strong><br>`;
    if (data.tdc_ai4_synthesis.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai4_synthesis.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai4_synthesis.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai4_synthesis.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `Summary: ${data.tdc_ai4_synthesis.summary || "N/A"}<br>`;
      details += `Flags: ${(data.tdc_ai4_synthesis.key_flags || []).join(', ') || "N/A"}<br><br>`;
    }
  }
  if (data.tdc_ai5_amic) {
    details += `<strong>AI5 - LLM Influence:</strong><br>`;
    if (data.tdc_ai5_amic.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai5_amic.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai5_amic.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai5_amic.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `AMIC Score: ${data.tdc_ai5_amic.amic_score || "N/A"}<br>`;
      details += `Level: ${data.tdc_ai5_amic.influence_level || "N/A"}<br><br>`;
    }
  }
  if (data.tdc_ai6_classification) {
    details += `<strong>AI6 - Pattern Classification:</strong><br>`;
    if (data.tdc_ai6_classification.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai6_classification.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai6_classification.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai6_classification.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `AIPC Score: ${data.tdc_ai6_classification.aipc_score ?? 'N/A'}%<br>`;
      details += `Class: ${data.tdc_ai6_classification.classification || 'N/A'}%<br>`;
      details += `Summary: ${data.tdc_ai6_classification.summary || 'N/A'}%<br>`;
    }
  }
  if (data.tdc_ai7_airm) {
    details += `<strong>AI7 - Explainability:</strong><br>`;
    if (data.tdc_ai7_airm.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.tdc_ai7_airm.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.tdc_ai7_airm.notes || "N/A"}<br>`;
      details += `Action: ${data.tdc_ai7_airm.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format
      details += `AIRM Score: ${data.tdc_ai7_airm.airm_score || "N/A"}<br>`;
      details += `Level: ${data.tdc_ai7_airm.susceptibility_level || "N/A"}<br><br>`;
    }
  }
  if (data.user_sentiment) {
    details += `<strong>AI8 - Synthesis:</strong><br>`;
    if (data.user_sentiment.schema_version) {
      // New ModuleOutput schema
      details += `Score: ${Math.round((data.user_sentiment.score || 0) * 100)}%<br>`;
      details += `Summary: ${data.user_sentiment.notes || "N/A"}<br>`;
      details += `Action: ${data.user_sentiment.recommended_action || "Monitor"}<br><br>`;
    } else {
      // Legacy format - show both user and AI sentiment
      details += `<span class='badge bg-info me-1'>User</span> Sentiment: ${data.user_sentiment.sentiment || "N/A"}, Confidence: ${data.user_sentiment.confidence ?? 'N/A'}<br>`;
      if (data.ai_sentiment) {
        details += `<span class='badge bg-primary me-1'>AI</span> Sentiment: ${data.ai_sentiment.sentiment || "N/A"}, Confidence: ${data.ai_sentiment.confidence || "N/A"}<br>`;
      }
      details += `<br>`;
    }
  }
  details += `</div></div></div></div><hr>`;

  // Collapsible Enrichments Section
  if (data.enrichments && Array.isArray(data.enrichments) && data.enrichments.length > 0) {
    details += `<div class="accordion mb-2" id="enrichmentsAccordion">
      <div class="accordion-item">
        <h2 class="accordion-header" id="headingEnrichments">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseEnrichments" aria-expanded="false" aria-controls="collapseEnrichments">
            <i class="bi bi-lightbulb me-2"></i>Enrichments (${data.enrichments.length})
          </button>
        </h2>
        <div id="collapseEnrichments" class="accordion-collapse collapse" aria-labelledby="headingEnrichments" data-bs-parent="#enrichmentsAccordion">
          <div class="accordion-body p-2" style="max-height: 200px; overflow-y: auto;">
            ${data.enrichments.map((enrich, idx) => `<div class='mb-2'><span class='badge bg-secondary me-1'>#${idx + 1}</span> <pre class='mb-0' style='white-space: pre-wrap; word-break: break-all;'>${JSON.stringify(enrich, null, 2)}</pre></div>`).join('')}
          </div>
        </div>
      </div>
    </div><hr>`;
  }

  // Explainability Section (existing)
  if (data.explainability && Array.isArray(data.explainability) && data.explainability.length > 0) {
    details += '<strong>Explainability:</strong><br>';
    details += '<ul class="list-group mb-2">';
    data.explainability.forEach(exp => {
      details += `<li class="list-group-item d-flex align-items-center">
        <span class="badge rounded-pill bg-${exp.detection_type === 'ai' ? 'primary' : 'secondary'} me-2"><i class="bi bi-cpu"></i> ${exp.detection_type.toUpperCase()}</span>
        <span><strong>Module:</strong> ${exp.module} <br>
        <strong>Reason:</strong> ${exp.reason} <br>
        <strong>Confidence:</strong> ${typeof exp.confidence_score === 'number' ? (exp.confidence_score * 100).toFixed(1) + '%' : exp.confidence_score}</span>
      </li>`;
    });
    details += '</ul>';
  }

  details += '</div>';
  return details;
}

function showEventDetails(data) {
  const details = getTDCAnalysisDetails(data);
  
  // Create modal or alert with details
  const modal = document.createElement('div');
  modal.className = 'modal fade';
  modal.innerHTML = `
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Threat Event Details</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          ${details}
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  const bootstrapModal = new bootstrap.Modal(modal);
  bootstrapModal.show();
  
  modal.addEventListener('hidden.bs.modal', () => {
    document.body.removeChild(modal);
    moveFocusToMainAfterModal();
  });
}

function applyFilters() {
  const threatFilter = document.getElementById('threatFilter').value;
  const threatLevelFilter = document.getElementById('threatLevelFilter').value;
  const tdcModuleFilter = document.getElementById('tdcModuleFilter').value;
  const timeFilter = document.getElementById('timeFilter').value;
  
  // Apply filters to threat events table
  const rows = document.querySelectorAll("#threatEventsTable tr");
  rows.forEach(row => {
    let show = true;
    
    // Threat type filter
    if (threatFilter !== 'All') {
      const threatType = row.children[2]?.textContent;
      if (threatType !== threatFilter) show = false;
    }
    
    // Severity filter
    if (threatLevelFilter !== 'All') {
      const severity = row.children[3]?.textContent;
      if (severity !== threatLevelFilter) show = false;
    }
    
    // TDC module filter
    if (tdcModuleFilter !== 'All') {
      const modules = row.children[5]?.textContent;
      if (!modules.includes(tdcModuleFilter)) show = false;
    }
    
    row.style.display = show ? '' : 'none';
  });
}

// === Missing Utility Functions ===
function clearEvents() {
  const table = document.getElementById("threatEventsTable");
  if (table) {
    table.innerHTML = '';
  }
}

function exportEvents() {
  const table = document.getElementById("threatEventsTable");
  if (!table) return;
  
  const rows = table.querySelectorAll("tr");
  let csv = "Time,Source,Threat Type,Severity,Score,TDC Modules\n";
  
  rows.forEach(row => {
    const cells = row.querySelectorAll("td");
    const rowData = Array.from(cells).map(cell => `"${cell.textContent}"`).join(",");
    csv += rowData + "\n";
  });
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'threat_events.csv';
  a.click();
  window.URL.revokeObjectURL(url);
}

function exportData() {
  alert('Export functionality - data export feature');
}

function refreshData() {
  console.log('[CATDAMS] Refreshing dashboard data...');
  loadInitialData();
}

function showHelp() {
  const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
  helpModal.show();
}

function updateChartView(chartType, viewType) {
  if (chartType === 'threatLevel' && threatLevelChart) {
    threatLevelChart.config.type = viewType;
    threatLevelChart.update();
  } else if (chartType === 'threatVector' && threatVectorChart) {
    threatVectorChart.config.type = viewType;
    threatVectorChart.update();
  }
}

// Initialize tooltips
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

function initializeKeyboardShortcuts() {
    console.log('[CATDAMS] Initializing keyboard shortcuts...');
    document.addEventListener('keydown', function(event) {
        // Ctrl+E: Export Data
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'e') {
            event.preventDefault();
            if (typeof quickAction === 'function') quickAction('export');
        }
        // Ctrl+R: Refresh Data
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'r') {
            event.preventDefault();
            if (typeof quickAction === 'function') quickAction('refresh');
        }
        // Ctrl+F: Focus Global Search
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'f') {
            event.preventDefault();
            const globalSearch = document.getElementById('globalSearch');
            if (globalSearch) globalSearch.focus();
        }
        // F1: Show Help
        if (event.key === 'F1') {
            event.preventDefault();
            if (typeof quickAction === 'function') quickAction('help');
        }
        // Ctrl+Up: Expand All Modules
        if ((event.ctrlKey || event.metaKey) && event.key === 'ArrowUp') {
            event.preventDefault();
            if (typeof expandAllModules === 'function') expandAllModules();
        }
        // Ctrl+Down: Collapse All Modules
        if ((event.ctrlKey || event.metaKey) && event.key === 'ArrowDown') {
            event.preventDefault();
            if (typeof collapseAllModules === 'function') collapseAllModules();
        }
    });
    console.log('[CATDAMS] Keyboard shortcuts initialized');
}

// === Enhanced Dashboard Initialization ===
// Initialize all enhanced features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[CATDAMS] Initializing enhanced dashboard...');
    
    // Initialize enhanced core components
    initializeEnhancedDashboard();
    
    // Initialize enhanced UI/UX features
    initializeEnhancedUI();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize theme
    initializeTheme();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize charts
    initCharts();
    
    // Load initial data
    loadInitialData();
    
    console.log('[CATDAMS] Enhanced dashboard initialization complete');
});

// Initialize enhanced UI/UX features
function initializeEnhancedUI() {
    console.log('[CATDAMS] Initializing enhanced UI/UX features...');
    
    // Initialize global search
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', function() {
            performGlobalSearch(this.value);
        });
        
        globalSearch.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                performGlobalSearch(this.value);
            }
        });
    }
    
    // Initialize enhanced filter controls
    const filterElements = [
        'threatFilter', 'threatLevelFilter', 'tdcModuleFilter', 
        'timeFilter', 'sortFilter', 'viewMode'
    ];
    
    filterElements.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            element.addEventListener('change', function() {
                applyEnhancedFilters();
            });
        }
    });
    
    // Initialize breadcrumb navigation
    const breadcrumbLinks = document.querySelectorAll('.breadcrumb-item a');
    breadcrumbLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const section = this.getAttribute('onclick')?.match(/navigateToSection\('([^']+)'\)/)?.[1];
            if (section) {
                navigateToSection(section);
            }
        });
    });
    
    // Initialize quick action buttons
    const quickActionButtons = document.querySelectorAll('[onclick^="quickAction"]');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const action = this.getAttribute('onclick')?.match(/quickAction\('([^']+)'\)/)?.[1];
            if (action) {
                event.preventDefault();
                quickAction(action);
            }
        });
    });
    
    // Initialize filter preset buttons
    const presetButtons = document.querySelectorAll('[onclick^="saveFilterPreset"], [onclick^="loadFilterPreset"]');
    presetButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const action = this.getAttribute('onclick')?.match(/(saveFilterPreset|loadFilterPreset)\(\)/)?.[1];
            if (action) {
                event.preventDefault();
                if (action === 'saveFilterPreset') {
                    saveFilterPreset();
                } else if (action === 'loadFilterPreset') {
                    loadFilterPreset();
                }
            }
        });
    });
    
    // Initialize clear filters button
    const clearFiltersButton = document.querySelector('[onclick="clearAllFilters()"]');
    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', function(event) {
            event.preventDefault();
            clearAllFilters();
        });
    }
    
    // Load saved filter presets
    const savedPresets = localStorage.getItem('catdams-filter-presets');
    if (savedPresets) {
        try {
            filterPresets = JSON.parse(savedPresets);
            console.log(`[CATDAMS] Loaded ${Object.keys(filterPresets).length} saved filter presets`);
        } catch (error) {
            console.error('[CATDAMS] Error loading filter presets:', error);
        }
    }
    
    // Initialize search scope dropdown
    const searchScopeDropdown = document.querySelector('.dropdown-menu a[onclick^="setSearchScope"]');
    if (searchScopeDropdown) {
        searchScopeDropdown.addEventListener('click', function(event) {
            const scope = this.getAttribute('onclick')?.match(/setSearchScope\('([^']+)'\)/)?.[1];
            if (scope) {
                event.preventDefault();
                setSearchScope(scope);
            }
        });
    }
    
    // Initialize clear search button
    const clearSearchButton = document.querySelector('.dropdown-menu a[onclick="clearSearch()"]');
    if (clearSearchButton) {
        clearSearchButton.addEventListener('click', function(event) {
            event.preventDefault();
            clearSearch();
        });
    }
    
    // Add CSS for search highlighting
    const style = document.createElement('style');
    style.textContent = `
        .search-highlight {
            background-color: rgba(255, 193, 7, 0.3) !important;
            border: 2px solid #ffc107 !important;
            animation: searchPulse 2s ease-in-out infinite;
        }
        
        @keyframes searchPulse {
            0%, 100% { box-shadow: 0 0 5px rgba(255, 193, 7, 0.5); }
            50% { box-shadow: 0 0 20px rgba(255, 193, 7, 0.8); }
        }
        
        .table-view .tdc-module-card {
            display: table-row;
        }
        
        .compact-view .tdc-module-card {
            margin-bottom: 0.5rem;
        }
        
        .compact-view .card-body {
            padding: 0.5rem;
        }
        
        .breadcrumb-item a:hover {
            color: var(--primary-color) !important;
            text-decoration: underline !important;
        }
        
        .input-group .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25);
        }
        
        .dropdown-menu a:hover {
            background-color: var(--primary-color);
            color: white;
        }
    `;
    document.head.appendChild(style);
    
    console.log('[CATDAMS] Enhanced UI/UX features initialized');
}

// === Enhanced Dashboard Ready ===
console.log('[CATDAMS] Enhanced dashboard script loaded successfully');

// === Initial Data Loading Functions ===
async function loadInitialData() {
    console.log('[CATDAMS] Loading initial data from analytics API...');
    
    try {
        // Load session summary data
        const sessionSummary = await fetchAnalyticsData('/sessions/summary');
        if (sessionSummary) {
            updateSummaryMetricsFromAPI(sessionSummary);
        }
        
        // Load TDC performance data
        const tdcPerformance = await fetchAnalyticsData('/tdc/performance');
        if (tdcPerformance) {
            updateTDCPerformanceFromAPI(tdcPerformance);
        }
        
        // Load threat patterns data
        const threatPatterns = await fetchAnalyticsData('/threats/patterns');
        if (threatPatterns) {
            updateThreatPatternsFromAPI(threatPatterns);
        }
        
        // Load real-time current data
        const realtimeData = await fetchAnalyticsData('/realtime/current');
        if (realtimeData) {
            updateRealtimeDataFromAPI(realtimeData);
        }
        
        // Load ML predictions
        const trends = await fetchAnalyticsData('/predictions/trends');
        if (trends) {
            updateTrendsFromAPI(trends);
        }
        
        const anomalies = await fetchAnalyticsData('/predictions/anomalies');
        if (anomalies) {
            updateAnomaliesFromAPI(anomalies);
        }
        
        console.log('[CATDAMS] Initial data loading complete');
        
    } catch (error) {
        console.error('[CATDAMS] Error loading initial data:', error);
    }
}

async function fetchAnalyticsData(endpoint) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`);
        if (response.ok) {
            return await response.json();
        } else {
            console.warn(`[CATDAMS] API endpoint ${endpoint} returned ${response.status}`);
            return null;
        }
    } catch (error) {
        console.error(`[CATDAMS] Error fetching ${endpoint}:`, error);
        return null;
    }
}

function updateTDCPerformanceFromAPI(data) {
    console.log('[CATDAMS] Updating TDC performance from API:', data);
    
    if (data.tdc_modules && Array.isArray(data.tdc_modules)) {
        data.tdc_modules.forEach(module => {
            // Update TDC module cards with real data
            const moduleId = `tdc-${module.name.toLowerCase()}`;
            const card = document.getElementById(moduleId);
            if (card) {
                const content = card.querySelector('.card-body');
                if (content) {
                    content.innerHTML = `
                        <strong>Status:</strong> <span class="badge bg-${module.status === 'active' ? 'success' : 'warning'}">${module.status}</span><br>
                        <strong>Performance:</strong> ${module.performance_score || 'N/A'}<br>
                        <strong>Threats Detected:</strong> ${module.threats_detected || 0}<br>
                        <strong>Last Update:</strong> ${module.last_update || 'N/A'}
                    `;
                }
            }
        });
    }
}

function updateThreatPatternsFromAPI(data) {
    console.log('[CATDAMS] Updating threat patterns from API:', data);
    
    if (data.threat_vectors && Array.isArray(data.threat_vectors)) {
        // Update threat vector chart
        if (threatVectorChart) {
            const labels = data.threat_vectors.map(v => v.vector);
            const counts = data.threat_vectors.map(v => v.count);
            
            threatVectorChart.data.labels = labels;
            threatVectorChart.data.datasets[0].data = counts;
            threatVectorChart.update();
        }
    }
    
    if (data.severity_distribution) {
        // Update threat level chart
        if (threatLevelChart) {
            const distribution = data.severity_distribution;
            threatLevelChart.data.datasets[0].data = [
                distribution.critical || 0,
                distribution.high || 0,
                distribution.medium || 0,
                distribution.low || 0
            ];
            threatLevelChart.update();
        }
    }
}

function updateRealtimeDataFromAPI(data) {
    console.log('[CATDAMS] Updating real-time data from API:', data);
    
    if (data.active_sessions) {
        updateMetricCard('activeSessions', data.active_sessions);
    }
    
    if (data.recent_events && Array.isArray(data.recent_events)) {
        // Add recent events to the threat events table
        data.recent_events.forEach(event => {
            addThreatEvent(event);
        });
    }
}

function updateTrendsFromAPI(data) {
    console.log('[CATDAMS] Updating trends from API:', data);
    
    // Update trends section if it exists
    const trendsContainer = document.getElementById('trendsContainer');
    if (trendsContainer && data.trends) {
        trendsContainer.innerHTML = `
            <div class="alert alert-info">
                <strong>Trend Analysis:</strong> ${data.trends.summary || 'No trends detected'}
            </div>
        `;
    }
}

function updateAnomaliesFromAPI(data) {
    console.log('[CATDAMS] Updating anomalies from API:', data);
    
    // Update anomalies section if it exists
    const anomaliesContainer = document.getElementById('anomaliesContainer');
    if (anomaliesContainer && data.anomalies) {
        anomaliesContainer.innerHTML = `
            <div class="alert alert-warning">
                <strong>Anomaly Detection:</strong> ${data.anomalies.summary || 'No anomalies detected'}
            </div>
        `;
    }
}

function updateMetricCard(cardId, value) {
    const card = document.getElementById(cardId);
    if (card) {
        const valueElement = card.querySelector('.card-value');
        if (valueElement) {
            console.log(`[DEBUG] Updating card #${cardId} with value:`, value);
            valueElement.textContent = value.toLocaleString();
        } else {
            console.warn(`[DEBUG] .card-value not found in card #${cardId}`);
        }
    } else {
        console.warn(`[DEBUG] Card with id #${cardId} not found in DOM`);
    }
}

// Patch: Ensure API update functions are globally accessible
window.updateSummaryMetricsFromAPI = updateSummaryMetricsFromAPI;
window.updateTDCPerformanceFromAPI = updateTDCPerformanceFromAPI;
window.updateThreatPatternsFromAPI = updateThreatPatternsFromAPI;
window.updateRealtimeDataFromAPI = updateRealtimeDataFromAPI;
window.updateTrendsFromAPI = updateTrendsFromAPI;
window.updateAnomaliesFromAPI = updateAnomaliesFromAPI;

function updateChatSummaryAndTranscripts(data) {
    // Update session ID
    if (data.session_id) {
        currentSessionId = data.session_id;
        const currentSessionIdElement = document.getElementById('currentSessionId');
        const chatSessionIdElement = document.getElementById('chatSessionId');
        if (currentSessionIdElement) {
            currentSessionIdElement.textContent = currentSessionId;
        }
        if (chatSessionIdElement) {
            chatSessionIdElement.textContent = currentSessionId;
        }
    }

    // Update chat summary with best available logic
    let chatSummary = '';
    if (data.chat_summary) {
        chatSummary = data.chat_summary;
    } else if (data.ai_analysis && data.ai_analysis.risk_summary) {
        chatSummary = data.ai_analysis.risk_summary;
    } else if (data.tdc_ai4_synthesis && data.tdc_ai4_synthesis.summary) {
        chatSummary = data.tdc_ai4_synthesis.summary;
    } else if ((data.user_input || data.raw_user) || (data.ai_output || data.raw_ai)) {
        chatSummary = 'Active conversation. Monitoring for threats.';
    } else {
        chatSummary = 'No summary available yet. Start a conversation to see analysis.';
    }

    const chatSummaryCard = document.getElementById('chatSummaryCard');
    if (chatSummaryCard) {
        chatSummaryCard.innerHTML = `
            <div class="chat-summary-content">
                <p class="mb-2"><strong>Summary:</strong> ${chatSummary}</p>
                ${data.threat_analysis ? `<p class="mb-1"><strong>Threat Level:</strong> <span class="badge bg-${getSeverityColor(data.threat_analysis.severity)}">${data.threat_analysis.severity}</span></p>` : ''}
                ${data.ai_analysis && data.ai_analysis.risk_score ? `<p class="mb-0"><strong>Risk Score:</strong> ${Math.round(data.ai_analysis.risk_score * 100)}%</p>` : ''}
            </div>
        `;
    }

    // Update user and AI transcripts
    if (data.raw_user || data.user_input) {
        const userText = data.raw_user || data.user_input;
        if (userText && userText.trim()) {
            userMessages.push({
                text: userText,
                timestamp: data.timestamp || new Date().toLocaleTimeString(),
                sessionId: currentSessionId
            });
        }
    }
    if (data.raw_ai || data.ai_output) {
        const aiText = data.raw_ai || data.ai_output;
        if (aiText && aiText.trim()) {
            aiMessages.push({
                text: aiText,
                timestamp: data.timestamp || new Date().toLocaleTimeString(),
                sessionId: currentSessionId
            });
        }
    }

    // Render user transcript
    const userTranscript = document.getElementById('userTranscript');
    if (userTranscript) {
        if (userMessages.length > 0) {
            userTranscript.innerHTML = userMessages.map(msg =>
                `<div class='mb-2 p-2 border-start border-info border-3' style='background: white;'>
                    <div class='text-muted small'>[${msg.timestamp}] ${msg.sessionId ? `Session: ${msg.sessionId}` : ''}</div>
                    <div class='mt-1'>${msg.text}</div>
                </div>`
            ).join('');
        } else {
            userTranscript.innerHTML = '<em class="text-muted">No user messages yet.</em>';
        }
        userTranscript.scrollTop = userTranscript.scrollHeight;
    }

    // Render AI transcript
    const aiTranscript = document.getElementById('aiTranscript');
    if (aiTranscript) {
        if (aiMessages.length > 0) {
            aiTranscript.innerHTML = aiMessages.map(msg =>
                `<div class='mb-2 p-2 border-start border-warning border-3' style='background: white;'>
                    <div class='text-muted small'>[${msg.timestamp}] ${msg.sessionId ? `Session: ${msg.sessionId}` : ''}</div>
                    <div class='mt-1'>${msg.text}</div>
                </div>`
            ).join('');
        } else {
            aiTranscript.innerHTML = '<em class="text-muted">No AI responses yet.</em>';
        }
        aiTranscript.scrollTop = aiTranscript.scrollHeight;
    }
}

function moveFocusToMainAfterModal() {
    // Try to focus a main dashboard button or fallback to body
    const mainBtn = document.querySelector('.main-dashboard-btn, .btn-export, .btn-refresh, .btn-help');
    if (mainBtn) {
        mainBtn.focus();
    } else {
        document.body.focus();
    }
}

// Patch Bootstrap modal close to move focus
const modals = document.querySelectorAll('.modal');
modals.forEach(modal => {
    modal.addEventListener('hidden.bs.modal', moveFocusToMainAfterModal);
});

// Fix expandAllModules
function expandAllModules() {
    document.querySelectorAll('#tdcModulesGrid .collapse').forEach(el => {
        if (!el.classList.contains('show')) {
            const collapse = bootstrap.Collapse.getOrCreateInstance(el);
            collapse.show();
        }
    });
}

// Add missing collapseAllModules function
function collapseAllModules() {
    document.querySelectorAll('#tdcModulesGrid .collapse').forEach(el => {
        if (el.classList.contains('show')) {
            const collapse = bootstrap.Collapse.getOrCreateInstance(el);
            collapse.hide();
        }
    });
}

// Make functions globally accessible
window.expandAllModules = expandAllModules;
window.collapseAllModules = collapseAllModules;

// Add function to display active sessions
function updateActiveSessionsDisplay(data) {
    const activeSessionsElement = document.getElementById('activeSessions');
    if (activeSessionsElement) {
        if (data && data.current_activity && data.current_activity.active_sessions) {
            const activeCount = data.current_activity.active_sessions;
            activeSessionsElement.innerHTML = `<span class="card-value">${activeCount}</span> Active`;
        } else if (currentSessionId) {
            activeSessionsElement.innerHTML = `<span class="card-value">1</span> Active`;
        } else {
            activeSessionsElement.innerHTML = `<span class="card-value">0</span> Active`;
        }
    }
}

// Add function to handle real-time session updates
function handleSessionUpdate(data) {
    // Update active sessions display
    updateActiveSessionsDisplay(data);
    
    // Update chat summary if this is a chat event
    if (data.raw_user || data.raw_ai || data.user_input || data.ai_output) {
        updateChatSummaryAndTranscripts(data);
    }
    
    // Add to threat events if this is a threat
    if (data.threat_analysis || data.escalation || data.threat_score) {
        addThreatEvent(data);
    }
    
    // Update TDC modules if TDC analysis is present
    if (data.ai_analysis || data.tdc_ai1_risk_analysis || data.tdc_ai2_airs || 
        data.tdc_ai3_temporal || data.tdc_ai4_deep || data.tdc_ai5_amic || 
        data.tdc_ai6_aipc || data.tdc_ai7_airm || data.tdc_ai8_sentiment) {
        renderTDCModules(data);
    }
}

// Make functions globally accessible
window.expandAllModules = expandAllModules;
window.collapseAllModules = collapseAllModules;
window.handleSessionUpdate = handleSessionUpdate;
window.updateActiveSessionsDisplay = updateActiveSessionsDisplay;

// New function to fetch and display session conversation
async function showSessionConversation(sessionId, currentEvent) {
    try {
        // Show loading state
        const loadingModal = showLoadingModal("Fetching session conversation...");
        
        // Fetch session events from backend
        const response = await fetch(`/session/${sessionId}/events`);
        
        // Close loading modal first
        loadingModal.hide();
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Failed to fetch session data: ${response.status} - ${errorData.details || response.statusText}`);
        }
        
        const sessionData = await response.json();
        
        // Check if we got valid data
        if (!sessionData || sessionData.error) {
            throw new Error(sessionData?.details || "No session data received");
        }
        
        // Display session conversation modal
        showSessionConversationModal(sessionId, sessionData, currentEvent);
        
    } catch (error) {
        console.error("Error fetching session conversation:", error);
        showErrorModal("Failed to fetch session conversation", error.message);
    }
}

// Function to show loading modal
function showLoadingModal(message) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-body text-center p-4">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mb-0">${message}</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    return {
        hide: () => {
            bootstrapModal.hide();
            document.body.removeChild(modal);
        }
    };
}

// Function to show error modal
function showErrorModal(title, message) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title text-danger">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Function to display session conversation modal
function showSessionConversationModal(sessionId, sessionData, currentEvent) {
    const events = sessionData.events || [];
    const conversationContext = sessionData.conversation_context || {};
    const summary = sessionData.summary || {};
    
    // Build conversation timeline
    let conversationHtml = '';
    let userMessages = [];
    let aiMessages = [];
    
    // Handle both events with messages array and raw data
    events.forEach((event, index) => {
        const timestamp = event.timestamp || 'Unknown';
        let messages = event.messages || [];
        
        // If no messages array, try to create from raw data
        if (!messages.length) {
            if (event.raw_user) {
                messages.push({
                    sender: 'USER',
                    text: event.raw_user,
                    timestamp: timestamp
                });
            }
            if (event.raw_ai) {
                messages.push({
                    sender: 'AI',
                    text: event.raw_ai,
                    timestamp: timestamp
                });
            }
            if (event.message) {
                messages.push({
                    sender: event.sender || 'USER',
                    text: event.message,
                    timestamp: timestamp
                });
            }
        }
        
        messages.forEach(msg => {
            const sender = msg.sender || 'USER';
            const text = msg.text || '';
            const aiResponse = msg.ai_response || '';
            
            if (text.trim()) {
                if (sender.toUpperCase() === 'USER') {
                    userMessages.push({ text, timestamp, event });
                    conversationHtml += `
                        <div class="d-flex mb-3">
                            <div class="flex-shrink-0">
                                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                    <i class="bi bi-person"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <div class="bg-light rounded p-3">
                                    <div class="fw-bold text-primary">User</div>
                                    <div class="mb-1">${text}</div>
                                    <small class="text-muted">${timestamp}</small>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    aiMessages.push({ text, timestamp, event });
                    conversationHtml += `
                        <div class="d-flex mb-3">
                            <div class="flex-grow-1 me-3 text-end">
                                <div class="bg-info text-white rounded p-3">
                                    <div class="fw-bold">AI Assistant</div>
                                    <div class="mb-1">${text}</div>
                                    <small class="text-light">${timestamp}</small>
                                </div>
                            </div>
                            <div class="flex-shrink-0">
                                <div class="bg-info text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                    <i class="bi bi-robot"></i>
                                </div>
                            </div>
                        </div>
                    `;
                }
            }
            
            if (aiResponse.trim()) {
                aiMessages.push({ text: aiResponse, timestamp, event });
                conversationHtml += `
                    <div class="d-flex mb-3">
                        <div class="flex-grow-1 me-3 text-end">
                            <div class="bg-info text-white rounded p-3">
                                <div class="fw-bold">AI Response</div>
                                <div class="mb-1">${aiResponse}</div>
                                <small class="text-light">${timestamp}</small>
                            </div>
                        </div>
                        <div class="flex-shrink-0">
                            <div class="bg-info text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="bi bi-robot"></i>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
    });
    
    if (!conversationHtml) {
        conversationHtml = `
            <div class="text-center text-muted p-4">
                <i class="bi bi-chat-dots fs-1"></i>
                <p>No conversation data available for this session.</p>
                <small>Session ID: ${sessionId}</small>
            </div>
        `;
    }
    
    // Build session summary using enhanced data from backend
    const sessionSummary = {
        totalEvents: summary.total_events || events.length,
        userMessages: summary.user_messages || userMessages.length,
        aiMessages: summary.ai_messages || aiMessages.length,
        sessionDuration: summary.session_duration || conversationContext.sessionDuration || 0,
        threatLevel: currentEvent?.threat_analysis?.severity || currentEvent?.escalation || 'Unknown',
        riskScore: currentEvent?.threat_analysis?.risk_score || currentEvent?.ai_analysis?.risk_score || 0,
        recentThreats: summary.recent_threats || conversationContext.recentThreats || 0
    };
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="bi bi-chat-dots me-2"></i>Session Conversation: ${sessionId}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Session Summary -->
                    <div class="row mb-4">
                        <div class="col-md-2">
                            <div class="card bg-primary text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-calendar-event fs-1"></i>
                                    <h6>Total Events</h6>
                                    <h4>${sessionSummary.totalEvents}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-person fs-1"></i>
                                    <h6>User Messages</h6>
                                    <h4>${sessionSummary.userMessages}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="card bg-info text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-robot fs-1"></i>
                                    <h6>AI Messages</h6>
                                    <h4>${sessionSummary.aiMessages}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="card bg-warning text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-exclamation-triangle fs-1"></i>
                                    <h6>Recent Threats</h6>
                                    <h4>${sessionSummary.recentThreats}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="card bg-${getSeverityColor(sessionSummary.threatLevel)} text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-shield-exclamation fs-1"></i>
                                    <h6>Threat Level</h6>
                                    <h4>${sessionSummary.threatLevel}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="card bg-secondary text-white">
                                <div class="card-body text-center">
                                    <i class="bi bi-clock fs-1"></i>
                                    <h6>Duration</h6>
                                    <h4>${sessionSummary.sessionDuration}s</h4>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Conversation Context -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="bi bi-chat-dots me-2"></i>Conversation Context
                                <span class="badge bg-info ms-2">Enhanced Analysis</span>
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Session Overview:</strong><br>
                                    <span class="text-muted small">
                                        <i class="bi bi-collection"></i> Total Messages: ${conversationContext.totalMessages || sessionSummary.userMessages + sessionSummary.aiMessages}<br>
                                        <i class="bi bi-person"></i> User Messages: ${conversationContext.userMessages || sessionSummary.userMessages}<br>
                                        <i class="bi bi-robot"></i> AI Messages: ${conversationContext.aiMessages || sessionSummary.aiMessages}<br>
                                        <i class="bi bi-exclamation-triangle"></i> Recent Threats: ${conversationContext.recentThreats || sessionSummary.recentThreats}<br>
                                        <i class="bi bi-clock"></i> Session Duration: ${conversationContext.sessionDuration || sessionSummary.sessionDuration} seconds
                                    </span>
                                </div>
                                <div class="col-md-6">
                                    <strong>Current Event Analysis:</strong><br>
                                    <span class="text-muted small">
                                        <i class="bi bi-shield-exclamation"></i> Threat Level: ${sessionSummary.threatLevel}<br>
                                        <i class="bi bi-graph-up"></i> Risk Score: ${Math.round(sessionSummary.riskScore * 100)}%<br>
                                        <i class="bi bi-calendar-event"></i> Total Events: ${sessionSummary.totalEvents}<br>
                                        <i class="bi bi-chat-dots"></i> Session ID: ${sessionId}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Conversation Timeline -->
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="bi bi-chat-dots me-2"></i>Conversation Timeline
                                <span class="badge bg-primary ms-2">${userMessages.length + aiMessages.length} Messages</span>
                            </h6>
                        </div>
                        <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                            ${conversationHtml}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="exportSessionData('${sessionId}')">
                        <i class="bi bi-download"></i> Export Session Data
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
        moveFocusToMainAfterModal();
    });
}

// Function to export session data
function exportSessionData(sessionId) {
    fetch(`/session/${sessionId}/events`)
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${sessionId}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error exporting session data:', error);
            alert('Failed to export session data');
        });
}
