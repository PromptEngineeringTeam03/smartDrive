# db_connection.py
import os
import sqlite3
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Initialize ChromaDB connection
        self.chroma_client = chromadb.HttpClient(
            host="https://api.trychroma.com",
            port=443,
            ssl=True,
            headers={
                "Authorization": f"Bearer {os.getenv('CHROMA_API_KEY')}"
            },
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DB')
        )
        
        # Get the traffic_laws collection
        self.traffic_collection = self.chroma_client.get_collection("traffic_laws")
        
        # Initialize SQLite for query history
        self.sqlite_conn = sqlite3.connect('drivesmart_analytics.db', check_same_thread=False)
        self._init_sqlite_tables()
    
    def _init_sqlite_tables(self):
        """Create SQLite tables for analytics"""
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
                chroma_ids TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                helpful BOOLEAN,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (query_id) REFERENCES query_history(id)
            )
        ''')
        
        self.sqlite_conn.commit()
    
    def search_traffic_laws(self, query, jurisdiction=None, n_results=5):
        """Search traffic laws in ChromaDB"""
        where_clause = None
        if jurisdiction:
            where_clause = {"jurisdiction": jurisdiction}
        
        results = self.traffic_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        return results
    
    def save_query(self, query_data):
        """Save query to SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_history 
            (query, response, jurisdiction, analysis_type, response_time, sources_count, chroma_ids)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            query_data['query'],
            query_data['response'],
            query_data['jurisdiction'],
            query_data['analysis_type'],
            query_data['response_time'],
            query_data.get('sources_count', 0),
            ','.join(query_data.get('chroma_ids', []))
        ))
        
        self.sqlite_conn.commit()
        return cursor.lastrowid
    
    def get_stats(self):
        """Get dashboard statistics"""
        cursor = self.sqlite_conn.cursor()
        
        # Today's stats
        today_stats = cursor.execute('''
            SELECT 
                COUNT(*) as queries_today,
                AVG(response_time) as avg_response_time
            FROM query_history
            WHERE DATE(timestamp) = DATE('now')
        ''').fetchone()
        
        # Total stats
        total_stats = cursor.execute('''
            SELECT 
                COUNT(*) as total_queries,
                COUNT(DISTINCT jurisdiction) as jurisdictions_used
            FROM query_history
        ''').fetchone()
        
        return {
            'queries_today': today_stats[0] if today_stats else 0,
            'avg_response_time': today_stats[1] if today_stats and today_stats[1] else 0,
            'total_queries': total_stats[0] if total_stats else 0,
            'jurisdictions_used': total_stats[1] if total_stats else 0,
            'laws_indexed': self.traffic_collection.count()  # Get from ChromaDB
        }