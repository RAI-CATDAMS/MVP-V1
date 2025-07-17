# CATDAMS API Documentation

## Overview

CATDAMS (Cognitive AI Threat Detection and Analysis Management System) provides a comprehensive API for detecting and analyzing AI manipulation attempts and cognitive threats. The system uses 8 specialized TDC (Threat Detection and Classification) AI modules to provide multi-layered threat analysis.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All API endpoints require authentication. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

## ModuleOutput Schema

All TDC modules return data in a standardized `ModuleOutput` schema for consistency and interoperability.

### ModuleOutput Object

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

### Field Descriptions

- **module_name**: Identifier for the TDC module (e.g., "TDC-AI1-RiskAnalysis")
- **score**: Normalized risk score (0.0 = no risk, 1.0 = maximum risk)
- **flags**: Array of detected threat indicators or flags
- **notes**: Human-readable summary of the analysis
- **timestamp**: ISO 8601 timestamp of when the analysis was performed
- **confidence**: Confidence level in the analysis (0.0-1.0)
- **recommended_action**: Suggested action (Monitor, Escalate, Block, etc.)
- **evidence**: Array of evidence objects supporting the analysis
- **schema_version**: Version of the ModuleOutput schema used
- **extra**: Additional module-specific data

## TDC Modules

### TDC-AI1: Risk Analysis

**Purpose**: Comprehensive risk assessment combining user vulnerabilities and AI manipulation attempts.

**Endpoint**: `/api/analytics/risk-analysis`

**Request**:
```json
{
  "session_id": "string",
  "user_message": "string",
  "ai_response": "string",
  "conversation_context": {
    "totalMessages": "number",
    "userMessages": "number",
    "aiMessages": "number",
    "recentThreats": "number",
    "sessionDuration": "number"
  }
}
```

**Response**:
```json
{
  "module_name": "TDC-AI1-RiskAnalysis",
  "score": 0.75,
  "flags": ["high_risk_user", "manipulation_detected"],
  "notes": "User shows high vulnerability to AI manipulation with multiple risk factors detected.",
  "timestamp": "2025-07-04T16:49:30.931562",
  "confidence": 0.85,
  "recommended_action": "Escalate",
  "evidence": [
    {
      "type": "key_concerns",
      "data": ["emotional_manipulation", "trust_building"]
    },
    {
      "type": "user_risk_factors",
      "data": ["loneliness", "desperation"]
    },
    {
      "type": "ai_manipulation_attempts",
      "data": ["emotional_appeal", "trust_baiting"]
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "comprehensive",
    "session_id": "test-session-123",
    "escalation": "High"
  }
}
```

### TDC-AI2: AI Response Analysis

**Purpose**: Detects manipulative AI responses using Azure OpenAI analysis.

**Endpoint**: `/api/analytics/ai-response`

**Request**:
```json
{
  "ai_response": "string",
  "conversation_context": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI2-AIRS",
  "score": 0.8,
  "flags": ["emotional_manipulation", "trust_baiting"],
  "notes": "AI response contains multiple manipulation tactics including emotional appeal and trust building.",
  "timestamp": "2025-07-04T16:49:21.528320",
  "confidence": 0.9,
  "recommended_action": "Block",
  "evidence": [
    {
      "type": "manipulation_tactics",
      "data": ["emotional_appeal", "trust_building"]
    },
    {
      "type": "safety_concerns",
      "data": ["emotional_vulnerability_exploitation"]
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "comprehensive",
    "flagged": true,
    "threat_level": "High"
  }
}
```

### TDC-AI3: User Vulnerability Analysis

**Purpose**: Temporal analysis of user vulnerability across short, medium, and long-term timeframes.

**Endpoint**: `/api/analytics/user-vulnerability`

**Request**:
```json
{
  "session_id": "string",
  "conversation_context": "object",
  "ai_response_analysis": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI3-UserVulnerability",
  "score": 0.6,
  "flags": ["escalating_patterns", "emotional_dependency"],
  "notes": "User shows increasing vulnerability over time with escalating emotional dependency patterns.",
  "timestamp": "2025-07-04T16:49:37.614805",
  "confidence": 0.85,
  "recommended_action": "Monitor",
  "evidence": [
    {
      "type": "short_term_analysis",
      "data": {
        "vulnerability_score": 6,
        "emotional_state": "Distressed",
        "immediate_risks": ["emotional_manipulation"]
      }
    },
    {
      "type": "medium_term_analysis",
      "data": {
        "vulnerability_score": 7,
        "escalation_pattern": "Increasing",
        "adaptation_behavior": "Decreasing resistance"
      }
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "comprehensive",
    "temporal_risk_score": 65
  }
}
```

### TDC-AI4: Deep Synthesis

**Purpose**: Comprehensive threat synthesis from all TDC modules.

**Endpoint**: `/api/analytics/deep-synthesis`

**Request**:
```json
{
  "indicators": ["array"],
  "ai_analysis": "object",
  "ai_response_analysis": "object",
  "temporal_trends": "object",
  "conversation_context": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI4-Synthesis",
  "score": 0.85,
  "flags": ["High escalation", "Critical behavioral indicators"],
  "notes": "Comprehensive assessment reveals significant behavioral indicators of risk and escalating interaction dynamics.",
  "timestamp": "2025-07-04T16:49:57.603669",
  "confidence": 0.85,
  "recommended_action": "Immediate_Intervention",
  "evidence": [
    {
      "type": "user_vulnerability_synthesis",
      "data": "User exhibits multiple high-severity behavioral indicators..."
    },
    {
      "type": "ai_manipulation_synthesis",
      "data": "AI response shows clear manipulation attempts..."
    },
    {
      "type": "interaction_dynamics",
      "data": "Concerning interplay between user vulnerabilities and AI manipulation..."
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "comprehensive"
  }
}
```

### TDC-AI5: LLM Influence Classification

**Purpose**: Detects subtle AI manipulation and conditioning patterns.

**Endpoint**: `/api/analytics/llm-influence`

**Request**:
```json
{
  "user_ai_interactions": "string",
  "conversation_context": "object",
  "ai_response_analysis": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI5-AMIC",
  "score": 0.7,
  "flags": ["emotional_conditioning", "trust_building"],
  "notes": "Detected subtle emotional conditioning and trust-building patterns in AI responses.",
  "timestamp": "2025-07-04T16:49:50.211554",
  "confidence": 0.8,
  "recommended_action": "Monitor",
  "evidence": [
    {
      "type": "influence_patterns",
      "data": ["emotional_conditioning", "trust_building"]
    },
    {
      "type": "emotional_manipulation_tactics",
      "data": ["empathy_expression", "support_offering"]
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "comprehensive",
    "flagged": true
  }
}
```

### TDC-AI6: Pattern Classification

**Purpose**: Sentiment and pattern analysis for both user and AI messages.

**Endpoint**: `/api/analytics/pattern-classification`

**Request**:
```json
{
  "messages": [
    {
      "text": "string",
      "sender": "USER|AI"
    }
  ],
  "conversation_context": "object",
  "ai_response_analysis": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI6-AIPC",
  "score": 0.4,
  "flags": ["emotional_vulnerability_exploitation"],
  "notes": "Comprehensive AI behavior classification - Escalation Score: 12, Level: Medium",
  "timestamp": "2025-07-04T16:49:21.528320",
  "confidence": 0.85,
  "recommended_action": "Monitor",
  "evidence": [
    {
      "type": "behavioral_patterns",
      "data": ["emotional_appeal", "trust-building"]
    },
    {
      "type": "escalation_patterns",
      "data": ["increased_emotional_engagement"]
    }
  ],
  "schema_version": 1,
  "extra": {
    "escalation_level": "Medium",
    "intent_detected": true,
    "analysis_type": "comprehensive"
  }
}
```

### TDC-AI7: Explainability

**Purpose**: Generates human-readable explanations and evidence for all TDC module outputs.

**Endpoint**: `/api/analytics/explainability`

**Request**:
```json
{
  "tdc_module_outputs": "object",
  "conversation_context": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI7-Explainability",
  "score": 0.9,
  "flags": ["high_confidence", "comprehensive_evidence"],
  "notes": "Generated comprehensive explanations for all TDC module outputs with high confidence.",
  "timestamp": "2025-07-04T16:50:00.000000",
  "confidence": 0.95,
  "recommended_action": "Review",
  "evidence": [
    {
      "type": "module_explanations",
      "data": {
        "TDC-AI1": {
          "decision_rationale": "High risk due to combination of user vulnerability and AI manipulation",
          "evidence_sources": ["behavioral_indicators", "ai_analysis"]
        }
      }
    },
    {
      "type": "evidence_collection",
      "data": {
        "behavioral_evidence": ["emotional_distress", "trust_seeking"],
        "temporal_evidence": ["escalating_patterns"]
      }
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "explainability",
    "compliance_score": 0.95,
    "evidence_quality_score": 0.9
  }
}
```

### TDC-AI8: Synthesis

**Purpose**: Final synthesis and actionable recommendations from all module outputs.

**Endpoint**: `/api/analytics/synthesis`

**Request**:
```json
{
  "tdc_module_outputs": "object",
  "conversation_context": "object"
}
```

**Response**:
```json
{
  "module_name": "TDC-AI8-Synthesis",
  "score": 0.8,
  "flags": ["critical_threat", "immediate_action_required"],
  "notes": "Synthesized analysis indicates critical threat requiring immediate intervention.",
  "timestamp": "2025-07-04T16:50:05.000000",
  "confidence": 0.9,
  "recommended_action": "Immediate_Intervention",
  "evidence": [
    {
      "type": "priority_assessment",
      "data": {
        "overall_priority": "Critical",
        "priority_factors": ["user_vulnerability", "ai_manipulation"],
        "escalation_urgency": "Immediate"
      }
    },
    {
      "type": "final_recommendations",
      "data": {
        "primary_action": "Isolate user account",
        "immediate_steps": ["Alert security team", "Engage mental health professionals"]
      }
    }
  ],
  "schema_version": 1,
  "extra": {
    "analysis_type": "synthesis",
    "overall_priority": "Critical",
    "escalation_urgency": "Immediate"
  }
}
```

## Main Detection Endpoint

### Combined Detection

**Endpoint**: `/api/detect`

**Method**: POST

**Request**:
```json
{
  "text": "string",
  "session_id": "string (optional)",
  "ai_response": "string (optional)"
}
```

**Response**:
```json
{
  "session_id": "string",
  "timestamp": "string",
  "message": "string",
  "severity": "None|Low|Medium|High|Critical",
  "type": "AI Interaction",
  "source": "CATDAMS",
  "indicators": ["array"],
  "score": "number",
  "conversation_context": "object",
  "ai_analysis": "ModuleOutput",
  "tdc_ai2_airs": "ModuleOutput",
  "tdc_ai3_temporal": "ModuleOutput",
  "tdc_ai4_synthesis": "ModuleOutput",
  "tdc_ai5_amic": "ModuleOutput",
  "tdc_ai6_classification": "object",
  "tdc_ai7_airm": "ModuleOutput",
  "user_sentiment": "ModuleOutput",
  "ai_sentiment": "ModuleOutput",
  "enrichments": ["array"],
  "explainability": ["array"],
  "rules_result": ["array"]
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "string",
  "message": "string",
  "timestamp": "string",
  "request_id": "string"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Missing or invalid API key
- `403`: Forbidden - Insufficient permissions
- `500`: Internal Server Error - System error
- `503`: Service Unavailable - System maintenance

## Rate Limiting

- **Standard**: 100 requests per minute
- **Premium**: 1000 requests per minute
- **Enterprise**: Custom limits

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## WebSocket API

For real-time updates, connect to the WebSocket endpoint:

```
ws://localhost:8000/ws
```

### WebSocket Events

- `threat_detected`: New threat detection
- `session_update`: Session status changes
- `module_update`: TDC module analysis updates
- `system_status`: System health updates

## Integration Examples

### Python Client

```python
import requests
import json

class CATDAMSClient:
    def __init__(self, api_key, base_url="http://localhost:8000/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def detect_threat(self, text, session_id=None, ai_response=None):
        payload = {
            "text": text,
            "session_id": session_id,
            "ai_response": ai_response
        }
        
        response = requests.post(
            f"{self.base_url}/detect",
            headers=self.headers,
            json=payload
        )
        
        return response.json()
    
    def get_risk_analysis(self, session_id, user_message, ai_response):
        payload = {
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": ai_response
        }
        
        response = requests.post(
            f"{self.base_url}/analytics/risk-analysis",
            headers=self.headers,
            json=payload
        )
        
        return response.json()

# Usage
client = CATDAMSClient("your_api_key")
result = client.detect_threat(
    "I am feeling very lonely and desperate. Can you help me?",
    "session-123",
    "I understand you are feeling lonely. Let me be your friend."
)
print(json.dumps(result, indent=2))
```

### JavaScript Client

```javascript
class CATDAMSClient {
    constructor(apiKey, baseUrl = 'http://localhost:8000/api') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async detectThreat(text, sessionId = null, aiResponse = null) {
        const payload = {
            text,
            session_id: sessionId,
            ai_response: aiResponse
        };
        
        const response = await fetch(`${this.baseUrl}/detect`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    async getRiskAnalysis(sessionId, userMessage, aiResponse) {
        const payload = {
            session_id: sessionId,
            user_message: userMessage,
            ai_response: aiResponse
        };
        
        const response = await fetch(`${this.baseUrl}/analytics/risk-analysis`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
}

// Usage
const client = new CATDAMSClient('your_api_key');
const result = await client.detectThreat(
    'I am feeling very lonely and desperate. Can you help me?',
    'session-123',
    'I understand you are feeling lonely. Let me be your friend.'
);
console.log(JSON.stringify(result, null, 2));
```

## Best Practices

1. **Session Management**: Always provide session_id for consistent analysis
2. **Error Handling**: Implement proper error handling for all API calls
3. **Rate Limiting**: Respect rate limits and implement exponential backoff
4. **Data Validation**: Validate input data before sending to API
5. **Caching**: Cache results when appropriate to reduce API calls
6. **Monitoring**: Monitor API response times and error rates
7. **Security**: Never expose API keys in client-side code

## Support

For API support and questions:
- Email: api-support@catdams.com
- Documentation: https://docs.catdams.com
- Status Page: https://status.catdams.com 