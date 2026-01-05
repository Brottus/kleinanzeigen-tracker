#!/usr/bin/env python3
"""
Database module for Job Scheduler
Handles SQLite database initialization and operations
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv('DB_PATH', 'jobs.db')


def get_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database():
    """Initialize database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL,
            schedule TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            
            -- Notification settings (Matterbridge integration)
            notify_enabled BOOLEAN DEFAULT 0,
            
            -- Status
            last_run TIMESTAMP,
            last_status TEXT,
            last_listing_id TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Global config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
        password_hash = generate_password_hash(admin_password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (admin_username, password_hash, 'admin@localhost'))
        
        conn.commit()
        
        # Determine password source for logging (never log the actual password!)
        password_source = 'ADMIN_PASSWORD environment variable' if os.getenv('ADMIN_PASSWORD') else 'default value (INSECURE!)'
        
        logger.info(f'Created default admin user: {admin_username}')
        print(f'✓ Created default admin user: {admin_username}')
        print(f'  Password set from: {password_source}')
        if not os.getenv('ADMIN_PASSWORD'):
            print(f'  ⚠️  WARNING: Using default password! Set ADMIN_PASSWORD environment variable!')
        print(f'  ⚠️  Change password after first login for security!')
    
    # Initialize default global config with descriptive names and detailed descriptions
    # Values are read from environment variables with fallback defaults
    default_configs = {
        # Scraper API Connection
        'scraper_api_url': {
            'value': os.getenv('SCRAPER_API_URL', 'http://localhost:3000'),
            'description': 'Ebay Kleinanzeigen Scraper API base URL'
        },
        'scraper_api_key': {
            'value': os.getenv('SCRAPER_API_KEY', 'test-key-123'),
            'description': 'API key for authenticating with the Scraper API'
        },
        'scraper_request_timeout': {
            'value': os.getenv('SCRAPER_REQUEST_TIMEOUT', '30'),
            'description': 'Request timeout in seconds when calling the Scraper API'
        },
        
        # Notification Settings
        'notification_language': {
            'value': os.getenv('NOTIFICATION_LANGUAGE', 'de'),
            'description': 'Language for notification messages: "de" (German) or "en" (English)'
        },
        
        # Matterbridge Integration (Optional)
        'matterbridge_url': {
            'value': os.getenv('MATTERBRIDGE_URL', 'http://matterbridge:4242'),
            'description': 'Matterbridge API base URL for sending notifications'
        },
        'matterbridge_token': {
            'value': os.getenv('MATTERBRIDGE_TOKEN', ''),
            'description': 'Bearer token for Matterbridge API authentication'
        },
        'matterbridge_gateway': {
            'value': os.getenv('MATTERBRIDGE_GATEWAY', 'gateway_ebaykleinanzeigen'),
            'description': 'Matterbridge gateway name to send messages through'
        },
        'matterbridge_username': {
            'value': os.getenv('MATTERBRIDGE_USERNAME', 'Kleinanzeigen Bot'),
            'description': 'Username displayed in Matterbridge messages'
        },
        
        # Job Defaults
        'default_job_schedule': {
            'value': os.getenv('DEFAULT_JOB_SCHEDULE', '*/30 * * * *'),
            'description': 'Default cron schedule for new jobs (every 30 minutes)'
        }
    }
    
    for key, config in default_configs.items():
        cursor.execute('''
            INSERT OR IGNORE INTO global_config (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, config['value'], config['description']))
    
    conn.commit()
    conn.close()
    
    logger.info('Database initialized successfully')
    print('✓ Database initialized successfully')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_database()
