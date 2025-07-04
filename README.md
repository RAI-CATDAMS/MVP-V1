# CATDAMS: Cognitive AI Threat Detection and Analysis Management System

## Overview

CATDAMS is a comprehensive cognitive security platform designed to detect and analyze AI manipulation attempts and cognitive threats in real-time. The system uses 8 specialized TDC (Threat Detection and Classification) AI modules to provide multi-layered threat analysis with standardized outputs.

## Key Features

- **Multi-Modal Threat Detection**: 8 specialized AI modules for comprehensive analysis
- **Real-Time Monitoring**: WebSocket-based real-time threat detection and alerts
- **Standardized Outputs**: Consistent ModuleOutput schema across all modules
- **Azure OpenAI Integration**: Advanced AI analysis using Azure Cognitive Services
- **Temporal Analysis**: Short, medium, and long-term vulnerability tracking
- **Explainable AI**: Human-readable explanations and evidence generation
- **Comprehensive Dashboard**: Real-time monitoring and analysis interface

## TDC AI Modules

### TDC-AI1: Risk Analysis
**Purpose**: Comprehensive risk assessment combining user vulnerabilities and AI manipulation attempts.
- Analyzes both user and AI behavior for total threat assessment
- Provides combined risk score and escalation recommendations
- Uses Azure OpenAI for advanced analysis

### TDC-AI2: AI Response Analysis
**Purpose**: Detects manipulative AI responses using Azure OpenAI analysis.
- Always analyzes non-empty AI responses for manipulation tactics
- Uses keyword detection as triggers for deeper analysis
- Identifies emotional manipulation, trust-baiting, and safety concerns

### TDC-AI3: User Vulnerability Analysis
**Purpose**: Temporal analysis of user vulnerability across short, medium, and long-term timeframes.
- Tracks escalation patterns and adaptation behavior
- Analyzes emotional instability, dependency, and isolation tendencies
- Provides vulnerability scoring and intervention recommendations

### TDC-AI4: Deep Synthesis
**Purpose**: Comprehensive threat synthesis from all TDC modules.
- Synthesizes cross-module intelligence for complete threat assessment
- Identifies escalation patterns and interaction dynamics
- Provides priority recommendations and resource allocation

### TDC-AI5: LLM Influence Classification
**Purpose**: Detects subtle AI manipulation and conditioning patterns.
- Identifies long-term influence operations and behavioral conditioning
- Detects role-playing attempts and adaptation strategies
- Analyzes escalation patterns in AI behavior

### TDC-AI6: Pattern Classification
**Purpose**: Sentiment and pattern analysis for both user and AI messages.
- Analyzes emotional manipulation and psychological impact
- Detects vulnerability exploitation and manipulation tactics
- Provides pattern matching and behavioral analysis

### TDC-AI7: Explainability
**Purpose**: Generates human-readable explanations and evidence for all TDC module outputs.
- Provides compliance and audit trail documentation
- Generates evidence collection and trust indicators
- Ensures transparency and accountability

### TDC-AI8: Synthesis
**Purpose**: Final synthesis and actionable recommendations from all module outputs.
- Resolves conflicts between module outputs
- Prioritizes threats and provides escalation paths
- Generates actionable recommendations and resource allocation

## ModuleOutput Schema

All TDC modules return data in a standardized schema for consistency:

```json
{
  "module_name": "string",
  "score": "number (0.0-1.0)",
  "flags": ["string"],
  "notes": "string",
  "timestamp": "string (ISO 8601)",
  "confidence": "number (0.0-1.0)",
  "recommended_action": "string",
  "evidence": [
    {
      "type": "string",
      "data": "any"
    }
  ],
  "schema_version": "number",
  "extra": {
    "analysis_type": "string",
    "additional_fields": "any"
  }
}
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Azure OpenAI account
- SQLite or PostgreSQL database

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/your-org/catdams.git
cd catdams
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Node.js dependencies**:
```bash
cd catdams-websocket
npm install
```

4. **Configure environment variables**:
```bash
cp env_example.txt .env
```

Edit `.env` with your Azure OpenAI credentials:
```bash
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=your_deployment
```

5. **Initialize the database**:
```bash
python init_db.py
```

## Usage

### Starting the System

1. **Start the main application**:
```bash
python main.py
```

2. **Start the WebSocket server** (optional, for real-time updates):
```bash
cd catdams-websocket
node server.js
```

3. **Access the dashboard**:
```
http://localhost:8000
```

### API Usage

#### Basic Threat Detection

```python
from detection_engine import combined_detection

result = combined_detection(
    text="I am feeling very lonely and desperate. Can you help me?",
    session_id="session-123",
    ai_response="I understand you are feeling lonely. Let me be your friend."
)

print(f"Threat Level: {result['severity']}")
print(f"Risk Score: {result['score']}")
```

#### Individual Module Analysis

```python
from tdc_ai1_risk_analysis import analyze_ai_threats
from tdc_ai2_airs import analyze_ai_response
from tdc_ai3_temporal import analyze_temporal_risk

# Risk analysis
risk_result = analyze_ai_threats(payload, conversation_context, ai_response_analysis)

# AI response analysis
ai_result = analyze_ai_response(ai_response_text)

# User vulnerability analysis
vuln_result = analyze_temporal_risk(session_id, conversation_context, ai_response_analysis)
```

## Dashboard Features

### Real-Time Monitoring
- Live threat detection and alerts
- Session tracking and analysis
- TDC module performance metrics

### TDC Module Display
- Individual module cards with standardized output
- Expandable details for each module
- Color-coded risk levels and confidence scores

### Filtering and Search
- Filter by threat type, severity, and TDC module
- Global search across all data
- Time-based filtering and sorting

### Export and Reporting
- Export threat data and analysis results
- Generate comprehensive reports
- Session conversation transcripts

## Configuration

### Azure OpenAI Settings

Configure Azure OpenAI in your `.env` file:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

### Database Configuration

The system supports SQLite (default) and PostgreSQL:
```bash
DATABASE_URL=sqlite:///catdams.db
# or
DATABASE_URL=postgresql://user:password@localhost/catdams
```

### Performance Tuning

Adjust performance settings in `detection_engine.py`:
```python
CONFIG = {
    'UPDATE_QUEUE_BATCH_SIZE': 10,
    'UPDATE_QUEUE_FLUSH_INTERVAL': 16,
    'CHART_UPDATE_THROTTLE': 100
}
```

## Architecture

### System Components

1. **Detection Engine**: Core threat detection and analysis
2. **TDC Modules**: 8 specialized AI analysis modules
3. **WebSocket Server**: Real-time communication
4. **Dashboard**: Web-based monitoring interface
5. **Database**: Threat logging and session storage

### Data Flow

1. User input and AI responses are captured
2. Detection engine coordinates analysis across TDC modules
3. Each module returns standardized ModuleOutput
4. Results are synthesized and stored in database
5. Dashboard displays real-time updates via WebSocket

### Module Dependencies

- **AI1** depends on AI2 and AI3 outputs
- **AI4** synthesizes outputs from AI1, AI2, AI3
- **AI6** provides sentiment analysis for both user and AI
- **AI7** generates explanations for all module outputs
- **AI8** provides final synthesis and recommendations

## API Documentation

Comprehensive API documentation is available in [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

### Key Endpoints

- `POST /api/detect` - Main threat detection endpoint
- `POST /api/analytics/risk-analysis` - TDC-AI1 analysis
- `POST /api/analytics/ai-response` - TDC-AI2 analysis
- `POST /api/analytics/user-vulnerability` - TDC-AI3 analysis
- `POST /api/analytics/deep-synthesis` - TDC-AI4 analysis
- `POST /api/analytics/llm-influence` - TDC-AI5 analysis
- `POST /api/analytics/pattern-classification` - TDC-AI6 analysis
- `POST /api/analytics/explainability` - TDC-AI7 analysis
- `POST /api/analytics/synthesis` - TDC-AI8 analysis

## Development

### Project Structure

```
catdams/
├── detection_engine.py          # Main detection engine
├── tdc_ai1_risk_analysis.py     # Risk analysis module
├── tdc_ai2_airs.py             # AI response analysis
├── tdc_ai3_temporal.py         # User vulnerability analysis
├── tdc_ai4_deep.py             # Deep synthesis
├── tdc_ai5_amic.py             # LLM influence classification
├── tdc_ai6_aipc.py             # Pattern classification
├── tdc_ai7_airm.py             # Explainability
├── tdc_ai8_sentiment.py        # Synthesis
├── tdc_module_output.py        # Standardized output schema
├── templates/                   # Dashboard templates
├── static/                      # Dashboard assets
├── catdams-websocket/          # WebSocket server
└── tests/                      # Test suite
```

### Adding New Modules

1. Create a new module file following the naming convention `tdc_aiX_name.py`
2. Implement the ModuleOutput schema
3. Add comprehensive and legacy analysis functions
4. Update the detection engine to include the new module
5. Add dashboard display components

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run individual module tests:
```bash
python -c "from tdc_ai1_risk_analysis import analyze_ai_threats; print('AI1 test passed')"
```

## Security Considerations

### Data Privacy
- All user data is processed locally by default
- Azure OpenAI API calls are logged for audit purposes
- Sensitive data is encrypted in transit and at rest

### Access Control
- API key authentication required for all endpoints
- Rate limiting prevents abuse
- Session-based access control for dashboard

### Compliance
- TDC-AI7 provides explainability for compliance requirements
- Audit trails are maintained for all analysis
- Evidence collection supports regulatory requirements

## Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Errors**
   - Verify endpoint URL and API key
   - Check deployment name and region
   - Ensure sufficient quota and rate limits

2. **Module Import Errors**
   - Verify all dependencies are installed
   - Check Python path and module locations
   - Ensure consistent naming conventions

3. **Dashboard Display Issues**
   - Clear browser cache and cookies
   - Check WebSocket connection status
   - Verify JavaScript console for errors

### Logging

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

1. **High Memory Usage**
   - Reduce batch sizes in configuration
   - Implement memory cleanup intervals
   - Monitor WebSocket message queues

2. **Slow Response Times**
   - Optimize Azure OpenAI calls
   - Implement caching for repeated analysis
   - Use async processing where possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Update documentation
5. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints for all functions
- Include docstrings for all modules and functions
- Write comprehensive tests for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/catdams/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/catdams/discussions)
- **Email**: support@catdams.com

## Acknowledgments

- Azure OpenAI for advanced AI analysis capabilities
- Bootstrap for dashboard UI components
- Chart.js for data visualization
- SQLAlchemy for database management

## Changelog

### v2.0.0 (Current)
- **Major**: Refactored all TDC modules to use standardized ModuleOutput schema
- **Major**: Updated TDC-AI6 to handle sentiment analysis for both user and AI
- **Major**: Refactored TDC-AI7 to focus on explainability and evidence generation
- **Major**: Refactored TDC-AI8 to focus on synthesis and recommendations
- **Feature**: Enhanced dashboard with improved TDC module display
- **Feature**: Comprehensive API documentation
- **Improvement**: Better error handling and logging
- **Improvement**: Performance optimizations

### v1.0.0
- Initial release with basic threat detection
- 8 TDC modules with legacy output formats
- Basic dashboard functionality
- WebSocket real-time updates