#!/usr/bin/env python3
"""
Database Initialization Script
Initializes PostgreSQL database for Video Generator and Voice Cloning integration
"""

import psycopg2
import os
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
POSTGRES_HOST = "192.168.1.218"  # k3s node IP
POSTGRES_PORT = 30432            # NodePort
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres123"
DATABASE_NAME = "video_voice_integration"

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DATABASE_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
            print(f"Database '{DATABASE_NAME}' created successfully!")
        else:
            print(f"Database '{DATABASE_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def init_database():
    """Initialize the database with tables and data"""
    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=DATABASE_NAME
        )
        cursor = conn.cursor()
        
        # Read and execute the SQL initialization script
        with open('init_database.sql', 'r') as file:
            sql_script = file.read()
        
        # Execute the entire script as one transaction
        try:
            cursor.execute(sql_script)
            print("✓ SQL script executed successfully")
        except Exception as e:
            print(f"Error executing SQL script: {e}")
            conn.rollback()
            return False
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def test_connection():
    """Test the database connection and show some basic info"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=DATABASE_NAME
        )
        cursor = conn.cursor()
        
        # Test basic queries
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        if version:
            print(f"PostgreSQL Version: {version[0]}")
        else:
            print("PostgreSQL Version: Unknown")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[table[0] for table in tables]}")
        
        # Check voice mappings
        cursor.execute("SELECT voice_id, voice_name, is_default FROM voice_mappings;")
        voice_mappings = cursor.fetchall()
        print(f"\nVoice mappings: {voice_mappings}")
        
        # Check settings
        cursor.execute("SELECT setting_key, setting_value FROM settings;")
        settings = cursor.fetchall()
        print(f"\nSettings: {settings}")
        
        cursor.close()
        conn.close()
        
        print("\nDatabase connection test successful!")
        return True
        
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

def main():
    """Main function to run the database initialization"""
    print("=== Database Initialization Script ===")
    print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
    print(f"User: {POSTGRES_USER}")
    print(f"Database: {DATABASE_NAME}")
    print()
    
    # Step 1: Create database
    if not create_database():
        print("Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Initialize database with tables
    if not init_database():
        print("Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Step 3: Test connection
    if not test_connection():
        print("Failed to test connection. Exiting.")
        sys.exit(1)
    
    print("\n=== Database initialization completed successfully! ===")
    print("\nYou can now use the database with the following connection parameters:")
    print(f"Host: {POSTGRES_HOST}")
    print(f"Port: {POSTGRES_PORT}")
    print(f"Database: {DATABASE_NAME}")
    print(f"User: {POSTGRES_USER}")
    print(f"Password: {POSTGRES_PASSWORD}")

if __name__ == "__main__":
    main() 