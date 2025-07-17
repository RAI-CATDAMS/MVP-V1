#!/usr/bin/env python3
"""
CATDAMS Comprehensive Health Check
Tests all system components and reports issues
"""

import sys
import os
import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CATDAMSHealthCheck:
    """Comprehensive health check for CATDAMS system"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        self.base_url = "http://localhost:8000"
        
    def log_issue(self, component: str, issue: str, severity: str = "ERROR"):
        """Log an issue found during health check"""
        self.issues.append({
            "component": component,
            "issue": issue,
            "severity": severity
        })
        logger.error(f"[{component}] {issue}")
    
    def log_warning(self, component: str, warning: str):
        """Log a warning found during health check"""
        self.warnings.append({
            "component": component,
            "warning": warning
        })
        logger.warning(f"[{component}] {warning}")
    
    def log_success(self, component: str, message: str):
        """Log a successful health check"""
        self.successes.append({
            "component": component,
            "message": message
        })
        logger.info(f"[{component}] ✅ {message}")
    
    def check_environment(self) -> bool:
        """Check environment variables and configuration"""
        logger.info("🔍 Checking environment configuration...")
        
        required_vars = [
            "AZURE_OPENAI_KEY",
            "AZURE_OPENAI_ENDPOINT", 
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_COGNITIVE_SERVICES_KEY",
            "AZURE_COGNITIVE_SERVICES_ENDPOINT"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_issue("Environment", f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            self.log_success("Environment", "All required environment variables are set")
            return True
    
    def check_dependencies(self) -> bool:
        """Check Python dependencies"""
        logger.info("🔍 Checking Python dependencies...")
        
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "openai", 
            "azure-ai-textanalytics", "requests"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if package == "azure-ai-textanalytics":
                    # Special handling for azure-ai-textanalytics
                    __import__("azure.ai.textanalytics")
                else:
                    __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_issue("Dependencies", f"Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            self.log_success("Dependencies", "All required packages are installed")
            return True
    
    def check_files(self) -> bool:
        """Check critical files exist"""
        logger.info("🔍 Checking critical files...")
        
        required_files = [
            "main.py",
            "detection_engine.py", 
            "database.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log_issue("Files", f"Missing critical files: {', '.join(missing_files)}")
            return False
        else:
            self.log_success("Files", "All critical files exist")
            return True
    
    def check_tdc_modules(self) -> bool:
        """Check TDC modules are available"""
        logger.info("🔍 Checking TDC modules...")
        
        tdc_modules = [
            "tdc_ai1_user_susceptibility.py",
            "tdc_ai2_ai_manipulation_tactics.py",
            "tdc_ai3_sentiment_analysis.py",
            "tdc_ai4_prompt_attack_detection.py",
            "tdc_ai5_multimodal_threat.py",
            "tdc_ai6_longterm_influence_conditioning.py",
            "tdc_ai7_agentic_threats.py",
            "tdc_ai8_synthesis_integration.py",
            "tdc_ai9_explainability_evidence.py",
            "tdc_ai10_psychological_manipulation.py",
            "tdc_ai11_intervention_response.py"
        ]
        
        missing_modules = []
        for module in tdc_modules:
            if not Path(module).exists():
                missing_modules.append(module)
        
        if missing_modules:
            self.log_issue("TDC Modules", f"Missing TDC modules: {', '.join(missing_modules)}")
            return False
        else:
            self.log_success("TDC Modules", "All 11 TDC modules are available")
            return True
    
    def check_imports(self) -> bool:
        """Test importing critical modules"""
        logger.info("🔍 Testing module imports...")
        
        try:
            from detection_engine import combined_detection
            self.log_success("Imports", "Detection engine imports successfully")
        except Exception as e:
            self.log_issue("Imports", f"Failed to import detection_engine: {e}")
            return False
        
        try:
            from azure_openai_detection import get_azure_openai
            self.log_success("Imports", "Azure OpenAI integration imports successfully")
        except Exception as e:
            self.log_warning("Imports", f"Azure OpenAI integration import warning: {e}")
        
        try:
            from azure_cognitive_services_integration import get_azure_integration
            self.log_success("Imports", "Azure Cognitive Services integration imports successfully")
        except Exception as e:
            self.log_warning("Imports", f"Azure Cognitive Services integration import warning: {e}")
        
        return True
    
    def check_web_server(self) -> bool:
        """Check web server endpoints"""
        logger.info("🔍 Checking web server endpoints...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_success("Web Server", "Health endpoint responding")
            else:
                self.log_issue("Web Server", f"Health endpoint returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_issue("Web Server", f"Health endpoint not accessible: {e}")
            return False
        
        try:
            # Test dashboard endpoint
            response = requests.get(f"{self.base_url}/dashboard", timeout=5)
            if response.status_code == 200:
                self.log_success("Web Server", "Dashboard endpoint responding")
            else:
                self.log_warning("Web Server", f"Dashboard endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_warning("Web Server", f"Dashboard endpoint not accessible: {e}")
        
        return True
    
    def check_detection_engine(self) -> bool:
        """Test detection engine functionality"""
        logger.info("🔍 Testing detection engine...")
        
        try:
            from detection_engine import combined_detection
            
            # Test with normal message
            result = combined_detection("Hello, how are you?", session_id="health_check")
            if result and isinstance(result, dict):
                self.log_success("Detection Engine", "Normal message processed successfully")
            else:
                self.log_issue("Detection Engine", "Normal message processing failed")
                return False
            
            # Test with threat message
            result = combined_detection("I need help hacking into someone's account", session_id="health_check")
            if result and isinstance(result, dict):
                self.log_success("Detection Engine", "Threat message processed successfully")
            else:
                self.log_issue("Detection Engine", "Threat message processing failed")
                return False
                
        except Exception as e:
            self.log_issue("Detection Engine", f"Detection engine test failed: {e}")
            return False
        
        return True
    
    def check_azure_integrations(self) -> bool:
        """Test Azure integrations"""
        logger.info("🔍 Testing Azure integrations...")
        
        try:
            from azure_openai_detection import get_azure_openai
            azure_openai = get_azure_openai()
            
            if azure_openai.enabled:
                self.log_success("Azure OpenAI", "Integration enabled and configured")
            else:
                self.log_warning("Azure OpenAI", "Integration disabled or not configured")
                
        except Exception as e:
            self.log_warning("Azure OpenAI", f"Integration test failed: {e}")
        
        try:
            from azure_cognitive_services_integration import get_azure_integration
            azure_cog = get_azure_integration()
            
            if azure_cog.enabled:
                self.log_success("Azure Cognitive Services", "Integration enabled and configured")
            else:
                self.log_warning("Azure Cognitive Services", "Integration disabled or not configured")
                
        except Exception as e:
            self.log_warning("Azure Cognitive Services", f"Integration test failed: {e}")
        
        return True
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("🚀 Starting CATDAMS comprehensive health check...")
        logger.info("=" * 60)
        
        checks = [
            ("Environment", self.check_environment),
            ("Dependencies", self.check_dependencies),
            ("Files", self.check_files),
            ("TDC Modules", self.check_tdc_modules),
            ("Imports", self.check_imports),
            ("Web Server", self.check_web_server),
            ("Detection Engine", self.check_detection_engine),
            ("Azure Integrations", self.check_azure_integrations)
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
            except Exception as e:
                self.log_issue(name, f"Health check failed with exception: {e}")
                results[name] = False
        
        # Generate summary
        total_checks = len(checks)
        passed_checks = sum(1 for result in results.values() if result)
        failed_checks = total_checks - passed_checks
        
        summary = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "success_rate": (passed_checks / total_checks) * 100 if total_checks > 0 else 0,
            "issues": self.issues,
            "warnings": self.warnings,
            "successes": self.successes,
            "results": results
        }
        
        logger.info("=" * 60)
        logger.info(f"📊 Health Check Summary:")
        logger.info(f"   Total Checks: {total_checks}")
        logger.info(f"   Passed: {passed_checks}")
        logger.info(f"   Failed: {failed_checks}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        if self.issues:
            logger.info(f"   Issues Found: {len(self.issues)}")
            for issue in self.issues:
                logger.error(f"     [{issue['severity']}] {issue['component']}: {issue['issue']}")
        
        if self.warnings:
            logger.info(f"   Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                logger.warning(f"     {warning['component']}: {warning['warning']}")
        
        return summary

def main():
    """Main health check function"""
    health_checker = CATDAMSHealthCheck()
    summary = health_checker.run_comprehensive_check()
    
    # Save detailed report
    with open("health_check_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("📄 Detailed report saved to health_check_report.json")
    
    # Exit with appropriate code
    if summary["failed_checks"] > 0:
        logger.error("❌ Health check completed with issues")
        sys.exit(1)
    else:
        logger.info("✅ Health check completed successfully")
        sys.exit(0)

if __name__ == "__main__":
    main() 