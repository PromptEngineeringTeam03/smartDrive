"""
DriveSmart AI - Dashboard WITH SECURITY
Team 3: Siddhi Dhamale, Siddhesh Sawant, Vartika Singh, Prishita Patel
Northeastern University - INFO 7375
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import sys
from pathlib import Path
import sqlite3
import chromadb
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent/'SmartDrive'/ 'src'))

# ========== SECURITY MODULES ==========
try:
    from SmartDrive.security.input_validator import PromptSecurityValidator
    from SmartDrive.security.output_validator import ResponseValidator
    from SmartDrive.security.behavioral_monitor import BehavioralMonitor
    SECURITY_ENABLED = True
except ImportError as e:
    SECURITY_ENABLED = False

# Import other modules
try:
    from SmartDrive.src.refined_prompts import RefinedDriveSmartWorkflow
    from SmartDrive.src.vector_store import CloudTrafficLawVectorStore
    from SmartDrive.src.langraph import build_traffic_law_graph
    from SmartDrive.src.langsmith_monitoring import DriveSmartPerformanceMonitor
    MODULES_LOADED = True
except ImportError:
    MODULES_LOADED = False

# Page config
st.set_page_config(
    page_title="DriveSmart AI - Secure",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database Manager Class (same as yours)
class DatabaseManager:
    def __init__(self):
        from chromadb import HttpClient
        from chromadb.utils import embedding_functions
        
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-ada-002"
        )
        
        self.chroma_client = HttpClient(
            host="api.trychroma.com",
            port=443,
            ssl=True,
            headers={
                "Authorization": f"Bearer {os.getenv('CHROMA_API_KEY')}",
                "X-Chroma-Token": os.getenv('CHROMA_API_KEY')
            },
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DB')
        )
        
        try:
            self.traffic_collection = self.chroma_client.get_collection(
                "traffic_laws",
                embedding_function=self.embedding_function
            )
            self.db_connected = True
        except Exception as e:
            self.db_connected = False
        
        self.sqlite_conn = sqlite3.connect('drivesmart_analytics.db', check_same_thread=False)
        self._init_sqlite_tables()
    
    def _init_sqlite_tables(self):
        cursor = self.sqlite_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                jurisdiction TEXT,
                analysis_type TEXT,
                response_time REAL,
                sources_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.sqlite_conn.commit()
    
    def search_traffic_laws(self, query, jurisdiction=None, n_results=10):
        if not self.db_connected:
            return None
        
        try:
            if jurisdiction and jurisdiction != "All":
                enhanced_query = f"{query} {jurisdiction}"
            else:
                enhanced_query = query
            
            results = self.traffic_collection.query(
                query_texts=[enhanced_query],
                n_results=n_results * 2
            )
            
            if jurisdiction and jurisdiction != "All" and results['documents'][0]:
                filtered_docs = []
                filtered_meta = []
                
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    doc_jurisdiction = str(meta.get('Jurisdiction', '')).strip()
                    
                    if (jurisdiction.lower() == doc_jurisdiction.lower() or 
                        jurisdiction.lower() in doc_jurisdiction.lower()):
                        filtered_docs.append(doc)
                        filtered_meta.append(meta)
                
                if filtered_docs:
                    results['documents'] = [filtered_docs[:n_results]]
                    results['metadatas'] = [filtered_meta[:n_results]]
            else:
                results['documents'] = [results['documents'][0][:n_results]]
                results['metadatas'] = [results['metadatas'][0][:n_results]]
            
            return results
        except Exception as e:
            return None
    
    def save_query(self, query_data):
        cursor = self.sqlite_conn.cursor()
        cursor.execute('''
            INSERT INTO query_history 
            (query, response, jurisdiction, analysis_type, response_time, sources_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            query_data['query'],
            query_data['response'][:1000],
            query_data['jurisdiction'],
            query_data['analysis_type'],
            query_data['response_time'],
            query_data.get('sources_count', 0)
        ))
        self.sqlite_conn.commit()
        return cursor.lastrowid
    
    def get_stats(self):
        cursor = self.sqlite_conn.cursor()
        
        today_stats = cursor.execute('''
            SELECT COUNT(*) as queries_today, AVG(response_time) as avg_response_time
            FROM query_history
            WHERE DATE(timestamp) = DATE('now', 'localtime')
        ''').fetchone()
        
        total_stats = cursor.execute('''
            SELECT COUNT(*) as total_queries, COUNT(DISTINCT jurisdiction) as jurisdictions_used
            FROM query_history
        ''').fetchone()
        
        laws_count = 24
        if self.db_connected:
            try:
                laws_count = self.traffic_collection.count()
            except:
                pass
        
        return {
            'queries_today': today_stats[0] if today_stats else 0,
            'avg_response_time': today_stats[1] if today_stats and today_stats[1] else 2.1,
            'total_queries': total_stats[0] if total_stats else 0,
            'jurisdictions_used': total_stats[1] if total_stats else 0,
            'laws_indexed': laws_count
        }

# Initialize
@st.cache_resource
def get_managers():
    db_manager = DatabaseManager()
    
    if SECURITY_ENABLED:
        input_validator = PromptSecurityValidator()
        output_validator = ResponseValidator()
        behavioral_monitor = BehavioralMonitor()
        return db_manager, input_validator, output_validator, behavioral_monitor
    
    return db_manager, None, None, None

db_manager, input_validator, output_validator, behavioral_monitor = get_managers()
stats = db_manager.get_stats()

# Custom CSS (same as yours)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .security-alert {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

# Main Header
security_status = "🛡️ Protected" if SECURITY_ENABLED else "⚠️ Unprotected"
st.markdown(f"""
<div class="main-header">
    <h1 class="header-title">🚗 DriveSmart AI Dashboard</h1>
    <p class="header-subtitle">AI-Powered Traffic Law Assistant | {security_status}</p>
    <div style="margin-top: 1rem;">
        <span class="tech-badge">🔗 LangChain</span>
        <span class="tech-badge">📊 LangGraph</span>
        <span class="tech-badge">☁️ ChromaDB</span>
        <span class="tech-badge">{security_status}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown("""<div class="metric-card"><div class="metric-value">94%</div><div class="metric-label">Accuracy</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{stats['avg_response_time']:.1f}s</div><div class="metric-label">Avg Response</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="metric-card"><div class="metric-value">97%</div><div class="metric-label">Completeness</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{stats['queries_today']}</div><div class="metric-label">Queries Today</div></div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{stats['laws_indexed']}</div><div class="metric-label">Laws Indexed</div></div>""", unsafe_allow_html=True)
with col6:
    status_text = "Protected" if SECURITY_ENABLED else "Monitor"
    status_color = "#22c55e" if SECURITY_ENABLED else "#f59e0b"
    st.markdown(f"""<div class="metric-card"><div style="font-size: 1.5rem; color: {status_color};">🛡️ {status_text}</div><div class="metric-label">Security</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Content
col_left, col_center = st.columns([1.2, 2.8])

with col_left:
    st.markdown('<h2>🔍 Query Interface</h2>', unsafe_allow_html=True)
    
    if SECURITY_ENABLED:
        st.success("🛡️ Security Active")
    else:
        st.warning("⚠️ Security Disabled")
    
    query = st.text_area(
        "",
        height=200,
        placeholder="Enter your traffic law question...",
        key="query_input",
        label_visibility="collapsed"
    )
    
    jurisdiction = "All"
    prompt_type = "General"
    
    submit = st.button("🚀 Get Answer", type="primary", use_container_width=True)
    
    # HANDLE SUBMIT WITH SECURITY
    if submit and query:
        
        # ========== SECURITY VALIDATION ==========
        if SECURITY_ENABLED and input_validator and behavioral_monitor:
            with st.spinner("🛡️ Validating query security..."):
                validation = input_validator.validate_input(query)
                behavioral = behavioral_monitor.analyze_session(
                    st.session_state.session_id,
                    query,
                    validation
                )
            
            # CHECK IF BLOCKED
            if not validation["is_safe"]:
                risk_level = validation["risk_level"]
                flags = validation.get("flags", [])
                
                # SHOW RED ALERT
                st.markdown(f"""
                <div class="security-alert">
                    <h3>🚫 Query Blocked</h3>
                    <p><strong>Risk Level:</strong> {risk_level}</p>
                    <p><strong>Reason:</strong> Security validation detected potential issues.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show flags
                with st.expander("🔍 Security Details"):
                    for flag_type, detail in flags:
                        st.warning(f"**{flag_type}**: {detail}")
                
                # Save and stop
                query_data = {
                    'query': query,
                    'response': f"BLOCKED - {risk_level}",
                    'jurisdiction': jurisdiction,
                    'analysis_type': 'Security Block',
                    'response_time': 0.0,
                    'sources_count': 0
                }
                db_manager.save_query(query_data)
                st.session_state.last_response = query_data
                st.stop()
            
            # Check behavioral
            if behavioral["action"] in ["RATE_LIMIT", "BLOCK"]:
                st.error("⚠️ Too many queries - please slow down")
                st.stop()
            
            # PASSED - show green
            st.success("✅ Security validation passed")
        
        # ========== NORMAL PROCESSING ==========
        with st.spinner("🔍 Searching traffic law database..."):
            start_time = time.time()
            
            search_results = db_manager.search_traffic_laws(query, jurisdiction, 5)
            
            if search_results and search_results['documents'][0]:
                documents = search_results['documents'][0]
                metadatas = search_results['metadatas'][0]
                
                response = f"""**🎯 DIRECT ANSWER:**
Here's what I found regarding "{query[:100]}...":

**⚖️ RELEVANT LAWS:**
"""
                for i, (doc, meta) in enumerate(zip(documents[:3], metadatas[:3]), 1):
                    category = meta.get('Category', 'Traffic Law')
                    violation = meta.get('Violation', 'General')
                    doc_jurisdiction = meta.get('Jurisdiction', 'Not specified')
                    law_text = doc[:300] + "..." if len(doc) > 300 else doc
                    
                    response += f"""
**{i}. {category} - {violation}**
📍 *Jurisdiction: {doc_jurisdiction}*
{law_text}

"""
                
                response += """
**⚠️ LEGAL DISCLAIMER:** This information is for educational purposes only."""
                
                sources_count = len(documents)
            else:
                response = f"""**🎯 DIRECT ANSWER:**  
No specific laws found. Please consult official sources.

**⚠️ NOTE:** Limited information available in database."""
                sources_count = 0
            
            response_time = time.time() - start_time
            
            query_data = {
                'query': query,
                'response': response,
                'jurisdiction': jurisdiction,
                'analysis_type': prompt_type,
                'response_time': response_time,
                'sources_count': sources_count
            }
            
            db_manager.save_query(query_data)
            st.session_state.last_response = query_data

# CENTER COLUMN - Response
with col_center:
    st.markdown('<h2>📋 Response</h2>', unsafe_allow_html=True)
    
    if st.session_state.last_response:
        st.info(f"**Query:** {st.session_state.last_response['query']}")
        
        # Show if blocked
        if "BLOCKED" in st.session_state.last_response.get('response', ''):
            st.error(f"🚫 **Status:** {st.session_state.last_response['response']}")
        else:
            st.markdown(st.session_state.last_response['response'])
            
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.success(f"⏱️ {st.session_state.last_response['response_time']:.2f}s")
            with col_meta2:
                st.info(f"📚 {st.session_state.last_response['sources_count']} sources")
            with col_meta3:
                st.info(f"📍 {st.session_state.last_response['jurisdiction']}")
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem; color: #6b7280;">
            <h2 style="font-size: 3rem;">🚦</h2>
            <h3>Ready to Answer</h3>
            <p>{"🛡️ Security Active" if SECURITY_ENABLED else "⚠️ Running without security"}</p>
        </div>
        """, unsafe_allow_html=True)

# Footer (same as yours)
st.markdown("---")
st.markdown('<center><small>🚗 DriveSmart AI © 2025 | Northeastern University</small></center>', unsafe_allow_html=True)