
from plyer import notification
import json

def show_alert(message, tdc_analysis=None, severity="Medium"):
    """Show enhanced alert with TDC module analysis"""
    
    # Base notification
    title = f"CATDAMS Sentinel Alert ({severity})"
    
    # Enhance message with TDC analysis if available
    if tdc_analysis and isinstance(tdc_analysis, dict):
        tdc_modules = []
        for module_name, analysis in tdc_analysis.items():
            if isinstance(analysis, dict) and analysis.get('confidence', 0) > 0.5:
                # Extract module display name
                module_display = module_name.replace('tdc_ai', 'TDC-AI').replace('_', ' ').title()
                confidence = analysis.get('confidence', 0)
                tdc_modules.append(f"{module_display} ({confidence:.1f})")
        
        if tdc_modules:
            message += f"\n\nTDC Analysis: {', '.join(tdc_modules[:3])}"  # Show first 3 modules
            if len(tdc_modules) > 3:
                message += f" (+{len(tdc_modules) - 3} more)"
    
    notification.notify(
        title=title,
        message=message,
        timeout=8 if tdc_analysis else 5  # Longer timeout for TDC alerts
    )

def show_tdc_summary(tdc_analysis):
    """Show a summary of TDC module analysis"""
    if not tdc_analysis:
        return
    
    summary_parts = []
    for module_name, analysis in tdc_analysis.items():
        if isinstance(analysis, dict) and analysis.get('confidence', 0) > 0.6:
            # Get indicators from analysis
            indicators = []
            for key, value in analysis.items():
                if key != 'confidence' and isinstance(value, list):
                    indicators.extend(value[:2])  # Show first 2 indicators
            
            if indicators:
                module_short = module_name.split('_')[-1].title()
                summary_parts.append(f"{module_short}: {', '.join(indicators[:2])}")
    
    if summary_parts:
        show_alert("TDC Threat Analysis", tdc_analysis, "High")
        print(f"[TDC SUMMARY] {' | '.join(summary_parts)}")
