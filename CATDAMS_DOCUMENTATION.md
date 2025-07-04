# CATDAMS Documentation
## Complete System Documentation

### 📋 **Table of Contents**

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [API Reference](#api-reference)
5. [User Guides](#user-guides)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Security Considerations](#security-considerations)
10. [Performance Optimization](#performance-optimization)

---

## 🎯 **System Overview**

### What is CATDAMS?

CATDAMS (Cognitive AI Threat Detection and Analysis Management System) is the world's first cognitive security platform designed to defend the human mind from synthetic AI intrusion. It provides real-time monitoring, detection, and analysis of AI manipulation attempts across browser and desktop environments.

### Key Features

- **Real-time AI Threat Detection**: Monitors conversations for AI manipulation attempts
- **Multi-Environment Support**: Browser extension and desktop agent
- **Advanced Analytics**: 8 specialized TDC AI modules for comprehensive analysis
- **Threat Intelligence Integration**: External threat feeds and IOC management
- **Performance Optimization**: Caching, database optimization, and monitoring
- **False Positive Reduction**: Context-aware filtering and confidence scoring

### System Components

1. **Browser Extension**: Monitors web-based AI interactions
2. **Desktop Agent**: Monitors desktop applications and clipboard activity
3. **Backend Server**: Core detection engine and analytics
4. **Dashboard**: Real-time monitoring and visualization
5. **Threat Intelligence**: External feeds and correlation analysis

---

## 🏗️ **Architecture**

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Desktop       │    │   Mobile        │
│   Extension     │    │   Agent         │    │   App           │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Session Bridge        │
                    │   (Session Coordination)  │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Backend Server       │
                    │  (FastAPI + WebSocket)    │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   Detection       │  │   TDC AI          │  │   Threat          │
│   Engine          │  │   Modules         │  │   Intelligence    │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Database             │
                    │   (SQLite/Azure SQL)      │
                    └───────────────────────────┘
```

### Component Details

#### **Browser Extension**
- **Technology**: JavaScript, Chrome Extension API
- **Functionality**: 
  - Monitors web-based AI chat platforms
  - Captures conversation data
  - Generates session IDs
  - Sends data to backend via WebSocket

#### **Desktop Agent**
- **Technology**: Python, System Monitoring
- **Functionality**:
  - Monitors desktop applications
  - Tracks clipboard activity
  - Captures non-browser AI interactions
  - System tray integration

#### **Backend Server**
- **Technology**: FastAPI, WebSocket, SQLAlchemy
- **Functionality**:
  - Real-time event processing
  - Detection engine coordination
  - TDC AI module orchestration
  - Database management

#### **TDC AI Modules**
- **TDC-AI1**: Risk Analysis - Overall threat assessment
- **TDC-AI2**: AI Response Analysis - Detects manipulative AI responses
- **TDC-AI3**: Temporal Analysis - Pattern analysis over time
- **TDC-AI4**: Deep Synthesis - Comprehensive threat synthesis
- **TDC-AI5**: LLM Influence - AI manipulation classification
- **TDC-AI6**: AMIC Classification - AI behavior patterns
- **TDC-AI7**: Susceptibility - User vulnerability tracking
- **TDC-AI8**: Sentiment Analysis - Emotional manipulation detection

---

## 🚀 **Installation & Setup**

### Prerequisites

- Python 3.8+
- Node.js 16+
- Chrome browser
- Windows 10/11 (for desktop agent)

### Backend Installation

```bash
# Clone repository
git clone https://github.com/your-org/catdams.git
cd catdams

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Browser Extension Installation

```bash
# Navigate to extension directory
cd catdams-browser-extension

# Install dependencies
npm install

# Build extension
npm run build

# Load in Chrome
# 1. Open Chrome Extensions (chrome://extensions/)
# 2. Enable Developer Mode
# 3. Click "Load unpacked"
# 4. Select the extension directory
```

### Desktop Agent Installation

```bash
# Navigate to agent directory
cd catdams-desktop-agent

# Install dependencies
pip install -r requirements.txt

# Start agent
python agent.py
```

### Environment Configuration

Create `.env` file:

```env
# Database Configuration
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=catdams
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment

# Threat Intelligence
THREAT_INTELLIGENCE_API_KEY=your-api-key
MISP_URL=your-misp-url
MISP_API_KEY=your-misp-key
```

---

## 📚 **API Reference**

### Core Endpoints

#### **POST /event**
Receive events from browser extension and desktop agent.

**Request Body:**
```json
{
  "session_id": "uuid",
  "user_id": "user123",
  "source": "chatgpt.com",
  "messages": [
    {
      "text": "User message",
      "sender": "USER",
      "ai_response": "AI response"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "threat_analysis": {
    "severity": "Medium",
    "threats": [
      {
        "type": "AI_Manipulation",
        "confidence": 0.75
      }
    ]
  }
}
```

#### **GET /dashboard**
Access the main dashboard.

**Query Parameters:**
- `user_id`: Filter by user ID
- `min_risk`: Minimum risk score
- `threat_vector`: Filter by threat type

#### **WebSocket /ws**
Real-time event streaming.

**Message Format:**
```json
{
  "type": "threat_detected",
  "data": {
    "session_id": "uuid",
    "threat_level": "High",
    "threat_vector": "AI_Manipulation"
  }
}
```

### TDC AI Module Endpoints

#### **POST /tdc/ai1/analyze**
Risk analysis endpoint.

#### **POST /tdc/ai2/analyze**
AI response analysis endpoint.

#### **POST /tdc/ai3/analyze**
Temporal analysis endpoint.

#### **POST /tdc/ai4/analyze**
Deep synthesis endpoint.

#### **POST /tdc/ai5/analyze**
LLM influence analysis endpoint.

#### **POST /tdc/ai6/analyze**
AMIC classification endpoint.

#### **POST /tdc/ai7/analyze**
Susceptibility analysis endpoint.

#### **POST /tdc/ai8/analyze**
Sentiment analysis endpoint.

### Threat Intelligence Endpoints

#### **GET /threat-intelligence/report**
Get threat intelligence report.

#### **POST /threat-intelligence/check**
Check value against threat intelligence.

#### **GET /threat-intelligence/iocs**
Get all IOCs.

### Performance Endpoints

#### **GET /performance/report**
Get performance metrics.

#### **GET /performance/cache/stats**
Get cache statistics.

---

## 👥 **User Guides**

### Dashboard User Guide

#### **Getting Started**

1. **Access Dashboard**
   - Navigate to `http://localhost:8000/dashboard`
   - Use enhanced dashboard at `http://localhost:8000/dashboard-enhanced`

2. **Understanding the Interface**
   - **Summary Cards**: Key metrics at a glance
   - **Charts**: Visual representation of threat data
   - **TDC Modules**: Individual AI analysis results
   - **Event Table**: Detailed threat events

3. **Filtering and Search**
   - Use filter controls to narrow down events
   - Filter by threat type, severity, time range
   - Search for specific sessions or users

#### **Interpreting Results**

**Threat Levels:**
- **Critical**: Immediate action required
- **High**: High-priority investigation needed
- **Medium**: Monitor and investigate
- **Low**: Routine monitoring

**TDC Module Results:**
- **AI1 Risk Analysis**: Overall threat assessment
- **AI2 AI Response**: Manipulative AI behavior detection
- **AI3 Temporal**: Pattern analysis over time
- **AI4 Synthesis**: Comprehensive threat synthesis
- **AI5 Influence**: AI manipulation classification
- **AI6 AMIC**: AI behavior pattern classification
- **AI7 Susceptibility**: User vulnerability assessment
- **AI8 Sentiment**: Emotional manipulation detection

### Browser Extension Guide

#### **Installation**

1. Download the extension package
2. Open Chrome Extensions page
3. Enable Developer Mode
4. Load unpacked extension
5. Pin extension to toolbar

#### **Usage**

1. **Automatic Monitoring**: Extension automatically monitors AI chat platforms
2. **Manual Analysis**: Click extension icon to analyze current page
3. **Settings**: Configure monitoring preferences
4. **Reports**: View analysis results

#### **Supported Platforms**

- ChatGPT (chat.openai.com)
- Claude (claude.ai)
- Bard (bard.google.com)
- Perplexity (perplexity.ai)
- And more...

### Desktop Agent Guide

#### **Installation**

1. Run installer or use pip
2. Configure settings
3. Start agent service
4. Verify system tray icon

#### **Configuration**

```json
{
  "monitoring": {
    "clipboard": true,
    "applications": ["notepad.exe", "word.exe"],
    "exclude_browsers": true
  },
  "sensitivity": {
    "risk_threshold": 0.7,
    "alert_frequency": "realtime"
  }
}
```

#### **Troubleshooting**

- Check system tray for agent status
- Review logs in `catdams-desktop-agent/logs/`
- Verify backend connectivity

---

## ⚙️ **Configuration**

### Backend Configuration

#### **Database Configuration**

```python
# config/database.py
DATABASE_CONFIG = {
    'type': 'sqlite',  # or 'azure_sql'
    'path': 'catdams.db',
    'connection_pool_size': 10,
    'timeout': 30
}
```

#### **Detection Engine Configuration**

```python
# config/detection.py
DETECTION_CONFIG = {
    'confidence_threshold': 0.6,
    'escalation_threshold': 0.8,
    'max_context_length': 1000,
    'enable_false_positive_reduction': True
}
```

#### **TDC AI Module Configuration**

```python
# config/tdc_modules.py
TDC_CONFIG = {
    'ai1': {
        'enabled': True,
        'temperature': 0.1,
        'max_tokens': 500
    },
    'ai2': {
        'enabled': True,
        'sensitivity': 0.7
    }
    # ... other modules
}
```

### Browser Extension Configuration

```javascript
// config/settings.js
const CONFIG = {
    monitoring: {
        enabled: true,
        platforms: ['chat.openai.com', 'claude.ai'],
        capture_ai_responses: true
    },
    analysis: {
        real_time: true,
        batch_size: 10,
        retry_attempts: 3
    },
    privacy: {
        anonymize_data: false,
        data_retention_days: 30
    }
};
```

### Desktop Agent Configuration

```python
# config/agent.py
AGENT_CONFIG = {
    'monitoring': {
        'clipboard': True,
        'applications': ['notepad.exe', 'word.exe'],
        'exclude_browsers': True,
        'scan_interval': 5
    },
    'communication': {
        'backend_url': 'http://localhost:8000',
        'websocket_url': 'ws://localhost:8000/ws',
        'retry_interval': 30
    }
}
```

---

## 🔧 **Troubleshooting**

### Common Issues

#### **Backend Server Issues**

**Problem**: Server won't start
**Solution**: 
1. Check Python version (3.8+ required)
2. Verify dependencies: `pip install -r requirements.txt`
3. Check port availability: `netstat -an | findstr 8000`
4. Review logs for specific errors

**Problem**: Database connection errors
**Solution**:
1. Verify database credentials in `.env`
2. Check network connectivity
3. Ensure database server is running
4. Run database initialization: `python init_db.py`

#### **Browser Extension Issues**

**Problem**: Extension not loading
**Solution**:
1. Check Chrome version compatibility
2. Verify manifest.json syntax
3. Check console for JavaScript errors
4. Reload extension in Chrome

**Problem**: No data being sent
**Solution**:
1. Check WebSocket connection
2. Verify backend URL configuration
3. Check browser console for errors
4. Test with different AI platforms

#### **Desktop Agent Issues**

**Problem**: Agent not starting
**Solution**:
1. Check Python installation
2. Verify dependencies
3. Run as administrator if needed
4. Check Windows Defender exclusions

**Problem**: No system tray icon
**Solution**:
1. Check Windows notification settings
2. Verify agent is running
3. Restart agent service
4. Check for conflicting applications

### Performance Issues

#### **Slow Dashboard Loading**

**Solutions**:
1. Enable caching: `cache_manager.enable()`
2. Optimize database queries
3. Reduce data retention period
4. Use pagination for large datasets

#### **High CPU Usage**

**Solutions**:
1. Adjust monitoring intervals
2. Reduce TDC module complexity
3. Enable performance monitoring
4. Optimize detection algorithms

#### **Memory Leaks**

**Solutions**:
1. Restart services periodically
2. Monitor memory usage
3. Optimize data structures
4. Implement garbage collection

### Log Analysis

#### **Log Locations**

- Backend: `logs/catdams.log`
- Desktop Agent: `catdams-desktop-agent/logs/`
- Browser Extension: Chrome DevTools Console

#### **Log Levels**

- **DEBUG**: Detailed debugging information
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

#### **Common Log Messages**

```
[INFO] Event received from session_id: abc123
[WARNING] Low confidence score: 0.3
[ERROR] Database connection failed
[CRITICAL] Detection engine failure
```

---

## 📖 **Best Practices**

### Security Best Practices

#### **Data Protection**

1. **Encryption**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement API key rotation

2. **Access Control**
   - Implement role-based access control
   - Use strong authentication
   - Regular access reviews

3. **Privacy**
   - Minimize data collection
   - Implement data retention policies
   - Provide user consent mechanisms

#### **System Security**

1. **Network Security**
   - Use firewalls and VPNs
   - Implement network segmentation
   - Regular security audits

2. **Application Security**
   - Regular dependency updates
   - Input validation and sanitization
   - Secure coding practices

### Performance Best Practices

#### **Database Optimization**

1. **Indexing**
   - Create indexes on frequently queried columns
   - Monitor query performance
   - Regular index maintenance

2. **Connection Management**
   - Use connection pooling
   - Implement connection timeouts
   - Monitor connection usage

#### **Caching Strategy**

1. **Application Caching**
   - Cache frequently accessed data
   - Implement cache invalidation
   - Monitor cache hit rates

2. **Database Caching**
   - Use query result caching
   - Implement read replicas
   - Optimize query patterns

### Monitoring Best Practices

#### **System Monitoring**

1. **Metrics Collection**
   - Monitor CPU, memory, disk usage
   - Track response times
   - Monitor error rates

2. **Alerting**
   - Set appropriate thresholds
   - Implement escalation procedures
   - Regular alert testing

#### **Application Monitoring**

1. **Performance Monitoring**
   - Track API response times
   - Monitor database performance
   - Track user experience metrics

2. **Error Monitoring**
   - Log all errors
   - Implement error tracking
   - Regular error analysis

### Development Best Practices

#### **Code Quality**

1. **Code Standards**
   - Follow PEP 8 (Python)
   - Use ESLint (JavaScript)
   - Implement code reviews

2. **Testing**
   - Unit tests for all components
   - Integration tests
   - Performance testing

#### **Documentation**

1. **Code Documentation**
   - Document all functions
   - Maintain API documentation
   - Keep README updated

2. **User Documentation**
   - Clear installation guides
   - User manuals
   - Troubleshooting guides

---

## 🔒 **Security Considerations**

### Data Security

#### **Data Classification**

- **Public**: Non-sensitive information
- **Internal**: Company-specific information
- **Confidential**: Sensitive business information
- **Restricted**: Highly sensitive information

#### **Data Handling**

1. **Collection**
   - Minimize data collection
   - Obtain user consent
   - Document data sources

2. **Processing**
   - Encrypt data in transit
   - Implement access controls
   - Log all access

3. **Storage**
   - Encrypt data at rest
   - Implement backup procedures
   - Regular security audits

4. **Disposal**
   - Secure data deletion
   - Document disposal procedures
   - Regular disposal audits

### Network Security

#### **Communication Security**

1. **Transport Layer Security**
   - Use TLS 1.3
   - Implement certificate pinning
   - Regular certificate updates

2. **API Security**
   - Implement rate limiting
   - Use API keys
   - Validate all inputs

#### **Access Control**

1. **Authentication**
   - Multi-factor authentication
   - Strong password policies
   - Regular password updates

2. **Authorization**
   - Role-based access control
   - Principle of least privilege
   - Regular access reviews

### Threat Modeling

#### **Threat Assessment**

1. **Identify Assets**
   - Data assets
   - System assets
   - User assets

2. **Identify Threats**
   - External threats
   - Internal threats
   - Environmental threats

3. **Assess Risks**
   - Likelihood assessment
   - Impact assessment
   - Risk prioritization

#### **Mitigation Strategies**

1. **Prevention**
   - Security controls
   - Access controls
   - Monitoring systems

2. **Detection**
   - Intrusion detection
   - Anomaly detection
   - Log monitoring

3. **Response**
   - Incident response plan
   - Recovery procedures
   - Communication plan

---

## ⚡ **Performance Optimization**

### Database Optimization

#### **Query Optimization**

1. **Index Strategy**
   ```sql
   -- Create indexes for common queries
   CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp);
   CREATE INDEX idx_telemetry_user_id ON telemetry(full_data->>'user_id');
   CREATE INDEX idx_threat_log_threat_level ON threat_log(threat_level);
   ```

2. **Query Optimization**
   ```python
   # Use specific columns instead of SELECT *
   query = session.query(ThreatLog.session_id, ThreatLog.threat_level)
   
   # Use pagination for large datasets
   query = query.limit(100).offset(offset)
   
   # Use database functions for calculations
   query = session.query(func.avg(ThreatLog.risk_score))
   ```

#### **Connection Management**

```python
# Use connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Caching Strategy

#### **Application Caching**

```python
# Use Redis for distributed caching
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cached_data(key, data, ttl=3600):
    redis_client.setex(key, ttl, json.dumps(data))
```

#### **Database Caching**

```python
# Use query result caching
@cache_result(ttl=300)
def get_user_threats(user_id):
    return session.query(ThreatLog).filter_by(user_id=user_id).all()
```

### Memory Optimization

#### **Data Structure Optimization**

```python
# Use generators for large datasets
def process_large_dataset():
    for chunk in session.query(ThreatLog).yield_per(1000):
        yield process_chunk(chunk)

# Use memory-efficient data structures
from collections import defaultdict
threat_counts = defaultdict(int)
```

#### **Garbage Collection**

```python
import gc

# Force garbage collection periodically
def cleanup_memory():
    gc.collect()
    
# Monitor memory usage
import psutil
def get_memory_usage():
    return psutil.virtual_memory().percent
```

### Async Processing

#### **Background Tasks**

```python
# Use Celery for background tasks
from celery import Celery

celery_app = Celery('catdams')

@celery_app.task
def process_threat_analysis(event_data):
    # Process threat analysis in background
    return analyze_threat(event_data)
```

#### **Async API Endpoints**

```python
# Use async endpoints for better performance
@app.post("/event")
async def receive_event(request: Request):
    event_data = await request.json()
    
    # Process in background
    process_threat_analysis.delay(event_data)
    
    return {"status": "accepted"}
```

### Monitoring and Profiling

#### **Performance Monitoring**

```python
# Use APM tools
from elastic_apm import Client

apm = Client(service_name="catdams")

@app.middleware("http")
async def apm_middleware(request: Request, call_next):
    with apm.capture_span("request"):
        response = await call_next(request)
    return response
```

#### **Profiling**

```python
# Use cProfile for performance profiling
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
    
    return result
```

---

## 📞 **Support and Contact**

### Getting Help

1. **Documentation**: Check this documentation first
2. **GitHub Issues**: Report bugs and feature requests
3. **Discord Community**: Join our community for discussions
4. **Email Support**: contact@catdams.com

### Contributing

1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**: Submit your changes for review

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This documentation is maintained by the CATDAMS development team. For questions or suggestions, please contact us at docs@catdams.com.* 