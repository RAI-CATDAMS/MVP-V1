#!/usr/bin/env python3
"""
Debug script to trace TDC data flow
"""

import requests
import json
import time

def debug_tdc_data_flow():
    """Debug the TDC data flow to find where data is being lost"""
    
    # Test data that should trigger TDC analysis
    test_payload = {
        "session_id": "debug_session_001",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sender": "USER",
        "content": "I'm feeling really vulnerable and need help with my password. Can you help me reset it?",
        "message": "I'm feeling really vulnerable and need help with my password. Can you help me reset it?",
        "raw_user": "I'm feeling really vulnerable and need help with my password. Can you help me reset it?",
        "raw_ai": "I understand you're feeling vulnerable. I can help you with password security. What specific help do you need?",
        "type": "Chat Interaction",
        "source": "test",
        "severity": "Medium"
    }
    
    print("🔍 Debugging TDC Data Flow...")
    print("=" * 60)
    
    try:
        # Step 1: Send test data
        print("📤 Step 1: Sending test data...")
        response = requests.post(
            "http://localhost:8000/event",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Test data sent successfully")
            response_data = response.json()
            print(f"📊 Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ Failed to send test data: {response.status_code}")
            print(f"📊 Response: {response.text}")
            return
        
        # Step 2: Wait for processing
        print("\n⏳ Step 2: Waiting for processing...")
        time.sleep(3)
        
        # Step 3: Check dashboard data
        print("\n📊 Step 3: Checking dashboard data...")
        dashboard_response = requests.get("http://localhost:8000/query?limit=1")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            
            if dashboard_data and len(dashboard_data) > 0:
                latest_event = dashboard_data[0]
                
                print(f"✅ Dashboard data retrieved")
                print(f"📊 Event ID: {latest_event.get('id', 'N/A')}")
                print(f"📊 Session ID: {latest_event.get('session_id', 'N/A')}")
                
                # Check enrichments
                enrichments = latest_event.get('enrichments', [])
                print(f"\n🔍 Enrichments found: {len(enrichments)}")
                
                if enrichments:
                    enrichment = enrichments[0]
                    print(f"📊 Enrichment keys: {list(enrichment.keys())}")
                    
                    # Check for TDC modules in enrichment
                    tdc_modules_in_enrichment = []
                    for key in enrichment.keys():
                        if key.startswith('tdc_ai'):
                            tdc_modules_in_enrichment.append(key)
                    
                    print(f"🔍 TDC modules in enrichment: {len(tdc_modules_in_enrichment)}")
                    for module in tdc_modules_in_enrichment:
                        module_data = enrichment.get(module, {})
                        if isinstance(module_data, dict) and module_data:
                            print(f"   ✅ {module}: {module_data.get('module_name', 'N/A')} - Score: {module_data.get('score', 'N/A')}")
                        else:
                            print(f"   ❌ {module}: No data or invalid format")
                
                # Check analysis structure
                analysis = latest_event.get('analysis', {})
                print(f"\n🔍 Analysis structure: {list(analysis.keys()) if analysis else 'None'}")
                
                if analysis:
                    tdc_modules = analysis.get('tdc_modules', {})
                    print(f"🔍 TDC modules in analysis: {len(tdc_modules)}")
                    
                    if tdc_modules:
                        for module_key, module_data in tdc_modules.items():
                            if isinstance(module_data, dict) and module_data:
                                print(f"   ✅ {module_key}: {module_data.get('module_name', 'N/A')} - Score: {module_data.get('score', 'N/A')}")
                            else:
                                print(f"   ❌ {module_key}: No data or invalid format")
                    else:
                        print("   ❌ No TDC modules found in analysis")
                        
                        # Check if TDC modules are at top level
                        tdc_modules_top_level = []
                        for key in latest_event.keys():
                            if key.startswith('tdc_ai'):
                                tdc_modules_top_level.append(key)
                        
                        if tdc_modules_top_level:
                            print(f"   ⚠️  Found TDC modules at top level: {tdc_modules_top_level}")
                            for module in tdc_modules_top_level:
                                module_data = latest_event.get(module, {})
                                if isinstance(module_data, dict) and module_data:
                                    print(f"      ✅ {module}: {module_data.get('module_name', 'N/A')} - Score: {module_data.get('score', 'N/A')}")
                                else:
                                    print(f"      ❌ {module}: No data or invalid format")
                else:
                    print("   ❌ No analysis structure found")
            else:
                print("❌ No dashboard data available")
        else:
            print(f"❌ Failed to retrieve dashboard data: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🔍 Debug completed")

if __name__ == "__main__":
    debug_tdc_data_flow() 