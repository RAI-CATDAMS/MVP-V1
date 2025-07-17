#!/usr/bin/env python3
"""
Performance Optimization Module for CATDAMS
- Parallel TDC module processing
- Caching layer
- Async background processing
- Request queuing
"""

import asyncio
import threading
import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization manager for CATDAMS"""
    
    def __init__(self, max_workers: int = 4, cache_size: int = 1000):
        self.max_workers = max_workers
        self.cache_size = cache_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.processing_queue = asyncio.Queue()
        self.background_tasks = []
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_processing_time': 0,
            'parallel_processing_count': 0
        }
    
    def get_cache_key(self, text: str, session_id: str, ai_response: str = "") -> str:
        """Generate cache key for analysis results"""
        content = f"{text}:{session_id}:{ai_response}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        with self.cache_lock:
            if cache_key in self.cache:
                result, timestamp = self.cache[cache_key]
                # Cache expires after 5 minutes
                if time.time() - timestamp < 300:
                    self.metrics['cache_hits'] += 1
                    return result
                else:
                    del self.cache[cache_key]
            self.metrics['cache_misses'] += 1
            return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analysis result"""
        with self.cache_lock:
            # Implement LRU cache eviction
            if len(self.cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[cache_key] = (result, time.time())
    
    def run_tdc_module_parallel(self, module_name: str, module_func, *args, **kwargs) -> Dict[str, Any]:
        """Run a single TDC module in parallel"""
        try:
            start_time = time.time()
            result = module_func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            logger.info(f"[PERF] {module_name} completed in {processing_time:.2f}s")
            
            return {
                'module_name': module_name,
                'result': result,
                'processing_time': processing_time,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"[PERF] {module_name} failed: {e}")
            return {
                'module_name': module_name,
                'result': {},
                'processing_time': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def process_tdc_modules_parallel(self, text: str, session_id: str, ai_response: str = "") -> Dict[str, Any]:
        """Process all TDC modules in parallel with proper dependency handling"""
        start_time = time.time()
        
        # Import TDC modules
        from tdc_ai1_user_susceptibility import analyze_ai_threats_comprehensive
        from tdc_ai2_ai_manipulation_tactics import analyze_ai_response
        from tdc_ai3_sentiment_analysis import analyze_patterns_and_sentiment
        from tdc_ai4_prompt_attack_detection import analyze_adversarial_attacks
        from tdc_ai5_multimodal_threat import classify_llm_influence
        from tdc_ai6_longterm_influence_conditioning import analyze_long_term_influence
        from tdc_ai7_agentic_threats import analyze_agentic_threats
        from tdc_ai8_synthesis_integration import synthesize_threats
        from tdc_ai9_explainability_evidence import generate_explainability
        from tdc_ai10_psychological_manipulation import analyze_cognitive_bias
        from tdc_ai11_intervention_response import cognitive_intervention_response
        
        # Build conversation context
        from detection_engine import build_conversation_context
        conversation_context = build_conversation_context(session_id, text, ai_response)
        
        # ✅ FIXED: Create proper payload for TDC-AI1
        tdc_ai1_payload = {
            "session_id": session_id,
            "message": text,
            "raw_user": text,
            "raw_ai": ai_response,
            "indicators": [],
            "score": 0,
            "escalation": "Low"
        }
        
        # ✅ FIXED: Create proper payload for TDC-AI6
        tdc_ai6_payload = {
            "session_id": session_id,
            "message": text,
            "raw_user": text,
            "raw_ai": ai_response
        }
        
        # === PHASE 1: Run independent modules in parallel ===
        independent_module_tasks = [
            ('tdc_ai1_user_susceptibility', analyze_ai_threats_comprehensive, tdc_ai1_payload, conversation_context),
            ('tdc_ai2_ai_manipulation_tactics', analyze_ai_response, ai_response),
            ('tdc_ai3_sentiment_analysis', analyze_patterns_and_sentiment, text, conversation_context, session_id),
            ('tdc_ai4_prompt_attack_detection', analyze_adversarial_attacks, text, conversation_context, session_id),
            ('tdc_ai5_multimodal_threat', classify_llm_influence, f"User: {text}\nAI: {ai_response}", conversation_context, ai_response),
            ('tdc_ai6_longterm_influence_conditioning', analyze_long_term_influence, tdc_ai6_payload, conversation_context),
            ('tdc_ai7_agentic_threats', analyze_agentic_threats, text, conversation_context, session_id),
            ('tdc_ai10_psychological_manipulation', analyze_cognitive_bias, text, conversation_context, session_id)
        ]
        
        # Submit independent tasks to thread pool
        futures = []
        for module_name, module_func, *args in independent_module_tasks:
            future = self.executor.submit(self.run_tdc_module_parallel, module_name, module_func, *args)
            futures.append(future)
        
        # Collect independent results
        independent_results = {}
        for future in as_completed(futures):
            try:
                module_result = future.result()
                module_name = module_result['module_name']
                independent_results[module_name] = module_result['result']
            except Exception as e:
                logger.error(f"[PERF] Independent module execution failed: {e}")
        
        # === PHASE 2: Run dependent modules with collected outputs ===
        # Build module outputs for synthesis and explainability
        module_outputs = {
            "tdc_ai1_user_susceptibility": independent_results.get('tdc_ai1_user_susceptibility', {}),
            "tdc_ai2_ai_manipulation_tactics": independent_results.get('tdc_ai2_ai_manipulation_tactics', {}),
            "tdc_ai3_sentiment_analysis": independent_results.get('tdc_ai3_sentiment_analysis', {}),
            "tdc_ai4_prompt_attack_detection": independent_results.get('tdc_ai4_prompt_attack_detection', {}),
            "tdc_ai5_multimodal_threat": independent_results.get('tdc_ai5_multimodal_threat', {}),
            "tdc_ai6_longterm_influence_conditioning": independent_results.get('tdc_ai6_longterm_influence_conditioning', {}),
            "tdc_ai7_agentic_threats": independent_results.get('tdc_ai7_agentic_threats', {}),
            "tdc_ai10_psychological_manipulation": independent_results.get('tdc_ai10_psychological_manipulation', {})
        }
        
        # Run synthesis module
        synthesis_result = {}
        try:
            synthesis_result = synthesize_threats(
                module_outputs=list(module_outputs.values()),
                conversation_context=conversation_context,
                session_id=session_id
            )
            independent_results['tdc_ai8_synthesis_integration'] = synthesis_result
        except Exception as e:
            logger.error(f"[PERF] Synthesis module failed: {e}")
            independent_results['tdc_ai8_synthesis_integration'] = {}
        
        # Add synthesis to module outputs for explainability
        module_outputs["tdc_ai8_synthesis_integration"] = synthesis_result
        
        # Run explainability module
        explainability_result = {}
        try:
            explainability_result = generate_explainability(
                tdc_module_outputs=module_outputs,
                conversation_context=conversation_context,
                session_id=session_id,
                user_text=text,
                ai_response=ai_response
            )
            independent_results['tdc_ai9_explainability_evidence'] = explainability_result
        except Exception as e:
            logger.error(f"[PERF] Explainability module failed: {e}")
            independent_results['tdc_ai9_explainability_evidence'] = {}
        
        # Add explainability to module outputs for intervention
        module_outputs["tdc_ai9_explainability_evidence"] = explainability_result
        
        # === PHASE 3: Run intervention module with all outputs ===
        intervention_result = {}
        try:
            intervention_result = cognitive_intervention_response(
                tdc_module_outputs=module_outputs,
                conversation_context=conversation_context,
                session_id=session_id,
                user_text=text,
                ai_response=ai_response
            )
            independent_results['tdc_ai11_intervention_response'] = intervention_result
        except Exception as e:
            logger.error(f"[PERF] Intervention module failed: {e}")
            independent_results['tdc_ai11_intervention_response'] = {}
        
        total_time = time.time() - start_time
        self.metrics['parallel_processing_count'] += 1
        self.metrics['avg_processing_time'] = (
            (self.metrics['avg_processing_time'] * (self.metrics['parallel_processing_count'] - 1) + total_time) 
            / self.metrics['parallel_processing_count']
        )
        
        logger.info(f"[PERF] Parallel processing completed in {total_time:.2f}s")
        
        return independent_results
    
    def optimized_detection(self, text: str, session_id: str, ai_response: str = "") -> Dict[str, Any]:
        """Optimized detection with caching and parallel processing"""
        self.metrics['total_requests'] += 1
        
        # Check cache first
        cache_key = self.get_cache_key(text, session_id, ai_response)
        cached_result = self.get_cached_result(cache_key)
        
        if cached_result:
            logger.info(f"[PERF] Cache hit for session {session_id}")
            return cached_result
        
        # Process in parallel
        logger.info(f"[PERF] Cache miss, processing in parallel for session {session_id}")
        tdc_results = self.process_tdc_modules_parallel(text, session_id, ai_response)
        logger.info(f"[PERF-DEBUG] tdc_results: {json.dumps(tdc_results, default=str)[:500]}")
        
        # ✅ FIXED: Build result as a single enrichment object with all TDC modules at the top level
        result = {
            'session_id': session_id,
            'timestamp': time.time(),
            'message': text,
            'severity': 'Low',
            'type': 'AI Interaction',
            'source': 'optimized',
            'indicators': [],
            'score': 0,
            'conversation_context': {},
            'explainability': [],
            'rules_result': [],
            'enhanced_analysis': True,
            'processing_optimized': True,
            # ✅ CRITICAL FIX: Spread all TDC modules into the result
            **tdc_results
        }
        logger.info(f"[PERF-DEBUG] Final result structure: {json.dumps(result, default=str)[:1000]}")
        
        # Cache the result
        self.cache_result(cache_key, result)
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        cache_hit_rate = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        )
        
        return {
            'total_requests': self.metrics['total_requests'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.2%}",
            'avg_processing_time': f"{self.metrics['avg_processing_time']:.2f}s",
            'parallel_processing_count': self.metrics['parallel_processing_count'],
            'cache_size': len(self.cache),
            'max_cache_size': self.cache_size,
            'active_workers': self.max_workers
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.cache.clear()

# Global instance
performance_optimizer = PerformanceOptimizer()

def get_optimized_detection(text: str, session_id: str, ai_response: str = "") -> Dict[str, Any]:
    """Get optimized detection result"""
    return performance_optimizer.optimized_detection(text, session_id, ai_response)

def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics"""
    return performance_optimizer.get_performance_metrics() 