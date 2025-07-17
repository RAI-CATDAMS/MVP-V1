from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
from database import Base

# === AIPC Module Tables ===
class AIPCEvaluation(Base):
    __tablename__ = "aipc_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    escalation_score = Column(Integer)
    escalation_level = Column(String(50))
    summary = Column(String(1000))
    timestamp = Column(DateTime, default=datetime.utcnow)

    matches = relationship("AIPCMatch", back_populates="evaluation", cascade="all, delete-orphan")


class AIPCMatch(Base):
    __tablename__ = "aipc_matches"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("aipc_evaluations.id"))
    category = Column(String(100))
    pattern = Column(String(500))
    similarity = Column(Float)
    severity = Column(Integer)
    matched_text = Column(String(1000))

    evaluation = relationship("AIPCEvaluation", back_populates="matches")


# === CATDAMS Detection Engine Log Table ===
class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_text = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    threat_score = Column(Integer)
    escalation_level = Column(String)
    indicators = Column(JSON)
    context = Column(JSON)
    
    # === TDC Module Outputs (11-Module Structure) ===
    tdc_ai1_user_susceptibility = Column(JSON)  # User Risk & Susceptibility Analysis
    tdc_ai2_ai_manipulation_tactics = Column(JSON)          # AI Tactics & Manipulation Detection
    tdc_ai3_sentiment_analysis = Column(JSON)      # Pattern & Sentiment Analysis
    tdc_ai4_prompt_attack_detection = Column(JSON)   # Adversarial Prompt & Attack Detection
    tdc_ai5_multimodal_threat = Column(JSON)    # Multi-Modal Threat Detection
    tdc_ai6_longterm_influence_conditioning = Column(JSON)     # Long-Term Influence & Conditioning Analysis
    tdc_ai7_agentic_threats = Column(JSON)       # Agentic AI & Autonomous Agent Threat Modeling
    tdc_ai8_synthesis_integration = Column(JSON)     # Threat Synthesis & Escalation Detection
    tdc_ai9_explainability_evidence = Column(JSON) # Explainability & Evidence Generation
    tdc_ai10_psychological_manipulation = Column(JSON) # Cognitive Bias & Psychological Manipulation
    tdc_ai11_intervention_response = Column(JSON)  # Cognitive Intervention & Response
    
    # === Legacy Support (for backward compatibility) ===
    ai_analysis = Column(JSON)
    ai_output = Column(JSON)
    deep_synthesis = Column(JSON)
    classification = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# === CATDAMS Event Telemetry Table ===
class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    session_id = Column(String, index=True)
    escalation = Column(String)
    ai_source = Column(String)
    type_indicator = Column(String)
    ai_pattern = Column(String)
    ip_address = Column(String)
    country = Column(String)
    ai_country_origin = Column(String)

    # ✅ Added for user/AI separation and chat visibility
    sender = Column(String)
    raw_user = Column(Text)
    raw_ai = Column(Text)
    message = Column(Text)

    full_data = Column(JSON)
    enrichments = Column(JSON)
