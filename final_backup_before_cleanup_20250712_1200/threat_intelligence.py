"""
CATDAMS Threat Intelligence Integration Module
==============================================

This module provides comprehensive threat intelligence integration including:
- External threat feed integration
- IOC (Indicator of Compromise) management
- Threat actor attribution
- Intelligence sharing and collaboration
- Automated threat hunting
"""

import requests
import json
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IOC:
    """Indicator of Compromise"""
    ioc_id: str
    ioc_type: str  # ip, domain, url, hash, email
    ioc_value: str
    threat_type: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: List[str]
    description: str
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None

@dataclass
class ThreatFeed:
    """Threat intelligence feed configuration"""
    feed_id: str
    name: str
    url: str
    api_key: Optional[str] = None
    feed_type: str  # 'json', 'csv', 'stix', 'misp'
    update_interval: int  # seconds
    enabled: bool = True
    last_update: Optional[datetime] = None
    ioc_count: int = 0

@dataclass
class ThreatActor:
    """Threat actor information"""
    actor_id: str
    name: str
    aliases: List[str]
    description: str
    motivation: str
    capabilities: List[str]
    targets: List[str]
    first_seen: datetime
    last_seen: datetime
    confidence: float

class ThreatIntelligenceManager:
    """Comprehensive threat intelligence management system"""
    
    def __init__(self, db_path: str = "catdams.db"):
        self.db_path = db_path
        self.feeds: Dict[str, ThreatFeed] = {}
        self.iocs: Dict[str, IOC] = {}
        self.threat_actors: Dict[str, ThreatActor] = {}
        self.correlation_rules: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        
        # Initialize database
        self._init_database()
        
        # Load existing data
        self._load_feeds()
        self._load_iocs()
        self._load_threat_actors()
        
        # Start feed update thread
        self.update_thread = threading.Thread(target=self._update_feeds_loop, daemon=True)
        self.update_thread.start()
        
        # Statistics
        self.stats = {
            'total_iocs': 0,
            'active_feeds': 0,
            'correlations_found': 0,
            'last_update': None
        }
    
    def _init_database(self):
        """Initialize threat intelligence database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # IOC table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_iocs (
                    ioc_id TEXT PRIMARY KEY,
                    ioc_type TEXT,
                    ioc_value TEXT,
                    threat_type TEXT,
                    confidence REAL,
                    first_seen TEXT,
                    last_seen TEXT,
                    source TEXT,
                    tags TEXT,
                    description TEXT,
                    threat_actor TEXT,
                    campaign TEXT
                )
            """)
            
            # Threat feeds table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_feeds (
                    feed_id TEXT PRIMARY KEY,
                    name TEXT,
                    url TEXT,
                    api_key TEXT,
                    feed_type TEXT,
                    update_interval INTEGER,
                    enabled INTEGER,
                    last_update TEXT,
                    ioc_count INTEGER
                )
            """)
            
            # Threat actors table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_actors (
                    actor_id TEXT PRIMARY KEY,
                    name TEXT,
                    aliases TEXT,
                    description TEXT,
                    motivation TEXT,
                    capabilities TEXT,
                    targets TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    confidence REAL
                )
            """)
            
            # Correlation rules table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS correlation_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT,
                    conditions TEXT,
                    action TEXT,
                    enabled INTEGER,
                    created_at TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ioc_value ON threat_iocs(ioc_value)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ioc_type ON threat_iocs(ioc_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threat_type ON threat_iocs(threat_type)")
    
    def _load_feeds(self):
        """Load threat feeds from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM threat_feeds WHERE enabled = 1")
            for row in cursor.fetchall():
                feed = ThreatFeed(
                    feed_id=row[0],
                    name=row[1],
                    url=row[2],
                    api_key=row[3],
                    feed_type=row[4],
                    update_interval=row[5],
                    enabled=bool(row[6]),
                    last_update=datetime.fromisoformat(row[7]) if row[7] else None,
                    ioc_count=row[8]
                )
                self.feeds[feed.feed_id] = feed
    
    def _load_iocs(self):
        """Load IOCs from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM threat_iocs")
            for row in cursor.fetchall():
                ioc = IOC(
                    ioc_id=row[0],
                    ioc_type=row[1],
                    ioc_value=row[2],
                    threat_type=row[3],
                    confidence=row[4],
                    first_seen=datetime.fromisoformat(row[5]),
                    last_seen=datetime.fromisoformat(row[6]),
                    source=row[7],
                    tags=json.loads(row[8]) if row[8] else [],
                    description=row[9],
                    threat_actor=row[10],
                    campaign=row[11]
                )
                self.iocs[ioc.ioc_id] = ioc
        
        self.stats['total_iocs'] = len(self.iocs)
    
    def _load_threat_actors(self):
        """Load threat actors from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM threat_actors")
            for row in cursor.fetchall():
                actor = ThreatActor(
                    actor_id=row[0],
                    name=row[1],
                    aliases=json.loads(row[2]) if row[2] else [],
                    description=row[3],
                    motivation=row[4],
                    capabilities=json.loads(row[5]) if row[5] else [],
                    targets=json.loads(row[6]) if row[6] else [],
                    first_seen=datetime.fromisoformat(row[7]),
                    last_seen=datetime.fromisoformat(row[8]),
                    confidence=row[9]
                )
                self.threat_actors[actor.actor_id] = actor
    
    def add_feed(self, name: str, url: str, feed_type: str = 'json', 
                 api_key: str = None, update_interval: int = 3600) -> str:
        """Add a new threat intelligence feed"""
        feed_id = f"feed_{int(time.time())}"
        
        feed = ThreatFeed(
            feed_id=feed_id,
            name=name,
            url=url,
            api_key=api_key,
            feed_type=feed_type,
            update_interval=update_interval,
            enabled=True
        )
        
        self.feeds[feed_id] = feed
        self._save_feed(feed)
        self.stats['active_feeds'] = len([f for f in self.feeds.values() if f.enabled])
        
        return feed_id
    
    def _save_feed(self, feed: ThreatFeed):
        """Save feed to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO threat_feeds 
                (feed_id, name, url, api_key, feed_type, update_interval, enabled, last_update, ioc_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feed.feed_id, feed.name, feed.url, feed.api_key, feed.feed_type,
                feed.update_interval, 1 if feed.enabled else 0,
                feed.last_update.isoformat() if feed.last_update else None,
                feed.ioc_count
            ))
    
    def _update_feeds_loop(self):
        """Background thread for updating threat feeds"""
        while True:
            try:
                for feed in self.feeds.values():
                    if not feed.enabled:
                        continue
                    
                    # Check if it's time to update
                    if (feed.last_update is None or 
                        datetime.now() - feed.last_update > timedelta(seconds=feed.update_interval)):
                        self._update_feed(feed)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Feed update error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _update_feed(self, feed: ThreatFeed):
        """Update a specific threat feed"""
        try:
            headers = {}
            if feed.api_key:
                headers['Authorization'] = f'Bearer {feed.api_key}'
            
            response = requests.get(feed.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse feed data based on type
            if feed.feed_type == 'json':
                data = response.json()
                iocs = self._parse_json_feed(data)
            elif feed.feed_type == 'csv':
                iocs = self._parse_csv_feed(response.text)
            else:
                logger.warning(f"Unsupported feed type: {feed.feed_type}")
                return
            
            # Add IOCs to database
            new_iocs = 0
            for ioc_data in iocs:
                if self._add_ioc(ioc_data):
                    new_iocs += 1
            
            # Update feed statistics
            feed.last_update = datetime.now()
            feed.ioc_count = len([ioc for ioc in self.iocs.values() if ioc.source == feed.name])
            self._save_feed(feed)
            
            logger.info(f"Updated feed {feed.name}: {new_iocs} new IOCs")
            
        except Exception as e:
            logger.error(f"Failed to update feed {feed.name}: {e}")
    
    def _parse_json_feed(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse JSON threat feed data"""
        iocs = []
        
        # Handle different JSON feed formats
        if 'data' in data:
            items = data['data']
        elif 'indicators' in data:
            items = data['indicators']
        elif isinstance(data, list):
            items = data
        else:
            items = [data]
        
        for item in items:
            ioc = {
                'ioc_type': item.get('type', 'unknown'),
                'ioc_value': item.get('value', item.get('indicator', '')),
                'threat_type': item.get('threat_type', 'unknown'),
                'confidence': item.get('confidence', 0.5),
                'description': item.get('description', ''),
                'tags': item.get('tags', []),
                'threat_actor': item.get('threat_actor'),
                'campaign': item.get('campaign')
            }
            iocs.append(ioc)
        
        return iocs
    
    def _parse_csv_feed(self, csv_data: str) -> List[Dict[str, Any]]:
        """Parse CSV threat feed data"""
        import csv
        from io import StringIO
        
        iocs = []
        reader = csv.DictReader(StringIO(csv_data))
        
        for row in reader:
            ioc = {
                'ioc_type': row.get('type', 'unknown'),
                'ioc_value': row.get('value', row.get('indicator', '')),
                'threat_type': row.get('threat_type', 'unknown'),
                'confidence': float(row.get('confidence', 0.5)),
                'description': row.get('description', ''),
                'tags': row.get('tags', '').split(',') if row.get('tags') else [],
                'threat_actor': row.get('threat_actor'),
                'campaign': row.get('campaign')
            }
            iocs.append(ioc)
        
        return iocs
    
    def _add_ioc(self, ioc_data: Dict[str, Any]) -> bool:
        """Add IOC to database"""
        ioc_value = ioc_data['ioc_value']
        ioc_type = ioc_data['ioc_type']
        
        # Check if IOC already exists
        existing_ioc = self._find_ioc(ioc_value, ioc_type)
        
        if existing_ioc:
            # Update existing IOC
            existing_ioc.last_seen = datetime.now()
            existing_ioc.confidence = max(existing_ioc.confidence, ioc_data['confidence'])
            if ioc_data.get('threat_actor'):
                existing_ioc.threat_actor = ioc_data['threat_actor']
            if ioc_data.get('campaign'):
                existing_ioc.campaign = ioc_data['campaign']
            
            self._save_ioc(existing_ioc)
            return False
        else:
            # Create new IOC
            ioc_id = f"ioc_{int(time.time())}_{hash(ioc_value)}"
            ioc = IOC(
                ioc_id=ioc_id,
                ioc_type=ioc_type,
                ioc_value=ioc_value,
                threat_type=ioc_data['threat_type'],
                confidence=ioc_data['confidence'],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                source=ioc_data.get('source', 'unknown'),
                tags=ioc_data.get('tags', []),
                description=ioc_data.get('description', ''),
                threat_actor=ioc_data.get('threat_actor'),
                campaign=ioc_data.get('campaign')
            )
            
            self.iocs[ioc_id] = ioc
            self._save_ioc(ioc)
            self.stats['total_iocs'] += 1
            return True
    
    def _find_ioc(self, value: str, ioc_type: str) -> Optional[IOC]:
        """Find existing IOC by value and type"""
        for ioc in self.iocs.values():
            if ioc.ioc_value == value and ioc.ioc_type == ioc_type:
                return ioc
        return None
    
    def _save_ioc(self, ioc: IOC):
        """Save IOC to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO threat_iocs 
                (ioc_id, ioc_type, ioc_value, threat_type, confidence, first_seen, last_seen, 
                 source, tags, description, threat_actor, campaign)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ioc.ioc_id, ioc.ioc_type, ioc.ioc_value, ioc.threat_type, ioc.confidence,
                ioc.first_seen.isoformat(), ioc.last_seen.isoformat(), ioc.source,
                json.dumps(ioc.tags), ioc.description, ioc.threat_actor, ioc.campaign
            ))
    
    def check_ioc(self, value: str, ioc_type: str = None) -> List[IOC]:
        """Check if a value matches any IOCs"""
        matches = []
        
        for ioc in self.iocs.values():
            if ioc.ioc_value == value:
                if ioc_type is None or ioc.ioc_type == ioc_type:
                    matches.append(ioc)
        
        return matches
    
    def correlate_threats(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate event data with threat intelligence"""
        correlations = {
            'ioc_matches': [],
            'threat_actor_matches': [],
            'campaign_matches': [],
            'confidence_score': 0.0,
            'recommendations': []
        }
        
        # Check for IOC matches
        message = event_data.get('message', '')
        source = event_data.get('source', '')
        
        # Extract potential IOCs from message
        potential_iocs = self._extract_iocs_from_text(message)
        
        for ioc_type, ioc_value in potential_iocs:
            matches = self.check_ioc(ioc_value, ioc_type)
            for match in matches:
                correlations['ioc_matches'].append({
                    'ioc': match,
                    'context': f"Found in message: {ioc_value}"
                })
                correlations['confidence_score'] += match.confidence
        
        # Check source against known threat actors
        for actor in self.threat_actors.values():
            if source.lower() in [alias.lower() for alias in actor.aliases]:
                correlations['threat_actor_matches'].append(actor)
                correlations['confidence_score'] += actor.confidence
        
        # Generate recommendations
        if correlations['ioc_matches']:
            correlations['recommendations'].append("Block communication with identified IOCs")
        if correlations['threat_actor_matches']:
            correlations['recommendations'].append("Monitor for additional activity from identified threat actor")
        
        # Normalize confidence score
        correlations['confidence_score'] = min(1.0, correlations['confidence_score'])
        
        return correlations
    
    def _extract_iocs_from_text(self, text: str) -> List[Tuple[str, str]]:
        """Extract potential IOCs from text"""
        import re
        
        iocs = []
        
        # IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        for match in re.finditer(ip_pattern, text):
            iocs.append(('ip', match.group()))
        
        # Domains
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        for match in re.finditer(domain_pattern, text):
            iocs.append(('domain', match.group()))
        
        # URLs
        url_pattern = r'https?://[^\s]+'
        for match in re.finditer(url_pattern, text):
            iocs.append(('url', match.group()))
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            iocs.append(('email', match.group()))
        
        return iocs
    
    def get_threat_intelligence_report(self) -> Dict[str, Any]:
        """Get comprehensive threat intelligence report"""
        return {
            'statistics': {
                'total_iocs': self.stats['total_iocs'],
                'active_feeds': self.stats['active_feeds'],
                'threat_actors': len(self.threat_actors),
                'correlations_found': self.stats['correlations_found']
            },
            'recent_iocs': [
                {
                    'value': ioc.ioc_value,
                    'type': ioc.ioc_type,
                    'threat_type': ioc.threat_type,
                    'confidence': ioc.confidence,
                    'first_seen': ioc.first_seen.isoformat(),
                    'source': ioc.source
                }
                for ioc in sorted(self.iocs.values(), key=lambda x: x.first_seen, reverse=True)[:10]
            ],
            'top_threat_types': self._get_top_threat_types(),
            'active_feeds': [
                {
                    'name': feed.name,
                    'last_update': feed.last_update.isoformat() if feed.last_update else None,
                    'ioc_count': feed.ioc_count
                }
                for feed in self.feeds.values() if feed.enabled
            ]
        }
    
    def _get_top_threat_types(self) -> List[Dict[str, Any]]:
        """Get top threat types by IOC count"""
        threat_type_counts = defaultdict(int)
        for ioc in self.iocs.values():
            threat_type_counts[ioc.threat_type] += 1
        
        return [
            {'threat_type': threat_type, 'count': count}
            for threat_type, count in sorted(threat_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

# Global instance
threat_intelligence = ThreatIntelligenceManager()

def check_threat_intelligence(value: str, ioc_type: str = None) -> List[Dict[str, Any]]:
    """Check value against threat intelligence"""
    matches = threat_intelligence.check_ioc(value, ioc_type)
    return [
        {
            'ioc_value': ioc.ioc_value,
            'ioc_type': ioc.ioc_type,
            'threat_type': ioc.threat_type,
            'confidence': ioc.confidence,
            'threat_actor': ioc.threat_actor,
            'campaign': ioc.campaign,
            'description': ioc.description
        }
        for ioc in matches
    ]

def correlate_event_threats(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Correlate event with threat intelligence"""
    return threat_intelligence.correlate_threats(event_data)

def get_threat_intelligence_report() -> Dict[str, Any]:
    """Get threat intelligence report"""
    return threat_intelligence.get_threat_intelligence_report()

def add_threat_feed(name: str, url: str, feed_type: str = 'json', 
                   api_key: str = None, update_interval: int = 3600) -> str:
    """Add a new threat intelligence feed"""
    return threat_intelligence.add_feed(name, url, feed_type, api_key, update_interval) 