#!/usr/bin/env python3
"""
Examine CATDAMS database data structure
"""

from database import SessionLocal
from db_models import Telemetry, ThreatLog
import json

def examine_data():
    db = SessionLocal()
    
    print("=== TELEMETRY DATA ===")
    telemetry_data = db.query(Telemetry).all()
    print(f"Total telemetry records: {len(telemetry_data)}")
    
    for i, record in enumerate(telemetry_data):
        print(f"\n--- Record {i+1} ---")
        print(f"ID: {record.id}")
        print(f"Session ID: {record.session_id}")
        print(f"Timestamp: {record.timestamp}")
        print(f"Escalation: {record.escalation}")
        print(f"AI Source: {record.ai_source}")
        print(f"Type Indicator: {record.type_indicator}")
        print(f"Raw User: {record.raw_user[:100] if record.raw_user else 'None'}")
        print(f"Raw AI: {record.raw_ai[:100] if record.raw_ai else 'None'}")
        print(f"Message: {record.message[:100] if record.message else 'None'}")
        
        if record.full_data:
            print(f"Full Data Keys: {list(record.full_data.keys())}")
            # Check for TDC module data
            tdc_keys = [k for k in record.full_data.keys() if k.startswith('tdc_ai')]
            print(f"TDC Module Keys: {tdc_keys}")
            
            # Show sample TDC data
            for tdc_key in tdc_keys[:3]:  # Show first 3
                tdc_data = record.full_data.get(tdc_key)
                if tdc_data:
                    print(f"  {tdc_key}: {type(tdc_data)} - {str(tdc_data)[:100]}")
        else:
            print("Full Data: None")
            
        if record.enrichments:
            print(f"Enrichments: {len(record.enrichments)} items")
            if len(record.enrichments) > 0:
                first_enrich = record.enrichments[0]
                print(f"First Enrichment Keys: {list(first_enrich.keys()) if isinstance(first_enrich, dict) else 'Not a dict'}")
        else:
            print("Enrichments: None")
    
    print("\n=== THREAT LOGS ===")
    threat_data = db.query(ThreatLog).all()
    print(f"Total threat log records: {len(threat_data)}")
    
    for i, record in enumerate(threat_data):
        print(f"\n--- Threat Log {i+1} ---")
        print(f"ID: {record.id}")
        print(f"Session ID: {record.session_id}")
        print(f"Threat Score: {record.threat_score}")
        print(f"Escalation Level: {record.escalation_level}")
        
        # Check TDC module data
        tdc_modules = [
            'tdc_ai1_user_susceptibility', 'tdc_ai2_ai_manipulation_tactics',
            'tdc_ai3_sentiment_analysis', 'tdc_ai4_prompt_attack_detection',
            'tdc_ai5_multimodal_threat', 'tdc_ai6_longterm_influence_conditioning',
            'tdc_ai7_agentic_threats', 'tdc_ai8_synthesis_integration',
            'tdc_ai9_explainability_evidence', 'tdc_ai10_psychological_manipulation',
            'tdc_ai11_intervention_response'
        ]
        
        for module in tdc_modules:
            module_data = getattr(record, module)
            if module_data:
                print(f"  {module}: {type(module_data)} - {str(module_data)[:100]}")
    
    db.close()

if __name__ == "__main__":
    examine_data() 