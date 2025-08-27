#!/usr/bin/env python3
"""
Committee Registration CRUD Operations Script
A comprehensive Python script for Add, Delete, and View operations
for the committee registration system.
"""

import pymysql
import pandas as pd
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Optional
import base64

# Load environment variables
load_dotenv()

class CommitteeRegistrationDB:
    """Class to handle CRUD operations for committee registrations"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'db': os.getenv('DB_NAME'),
            'timeout': int(os.getenv('TIMEOUT', 10))
        }
        
        # Validate configuration
        if not all([self.db_config['host'], self.db_config['user'], 
                   self.db_config['password'], self.db_config['db']]):
            raise ValueError("Database configuration is incomplete. Please check your .env file.")
    
    def get_connection(self):
        """Create and return a database connection"""
        return pymysql.connect(
            charset="utf8mb4",
            connect_timeout=self.db_config['timeout'],
            cursorclass=pymysql.cursors.DictCursor,
            db=self.db_config['db'],
            host=self.db_config['host'],
            password=self.db_config['password'],
            read_timeout=self.db_config['timeout'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            write_timeout=self.db_config['timeout'],
        )
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    submission_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    committee VARCHAR(255) NOT NULL,
                    social_media_links TEXT,
                    photo_filename VARCHAR(255),
                    photo_data LONGBLOB,
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            return False
    
    def add_record(self, name: str, committee: str, social_media_links: str = None, 
                   photo_path: str = None) -> bool:
        """Add a new committee registration record"""
        try:
            # Generate unique submission ID
            submission_id = str(uuid.uuid4())[:8].upper()
            
            # Handle photo data
            photo_data = None
            photo_filename = None
            
            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    photo_data = f.read()
                photo_filename = os.path.basename(photo_path)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO submissions 
                (submission_id, name, committee, social_media_links, photo_filename, photo_data)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (submission_id, name, committee, social_media_links, photo_filename, photo_data))
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            if rows_affected > 0:
                print(f"✅ Record added successfully!")
                print(f"📝 Submission ID: {submission_id}")
                print(f"👤 Name: {name}")
                print(f"🏢 Committee: {committee}")
                return True
            else:
                print("❌ Failed to add record")
                return False
                
        except Exception as e:
            print(f"❌ Error adding record: {e}")
            return False
    
    def delete_record(self, submission_id: str = None, record_id: int = None) -> bool:
        """Delete a record by submission_id or database id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if submission_id:
                # First, get the record details for confirmation
                cursor.execute('SELECT * FROM submissions WHERE submission_id = %s', (submission_id,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"❌ No record found with submission ID: {submission_id}")
                    return False
                
                print(f"📋 Record to delete:")
                print(f"   👤 Name: {record['name']}")
                print(f"   🏢 Committee: {record['committee']}")
                print(f"   📅 Date: {record['submission_date']}")
                
                confirmation = input("⚠️  Are you sure you want to delete this record? (yes/no): ").lower()
                if confirmation != 'yes':
                    print("❌ Deletion cancelled")
                    return False
                
                cursor.execute('DELETE FROM submissions WHERE submission_id = %s', (submission_id,))
                
            elif record_id:
                # First, get the record details for confirmation
                cursor.execute('SELECT * FROM submissions WHERE id = %s', (record_id,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"❌ No record found with ID: {record_id}")
                    return False
                
                print(f"📋 Record to delete:")
                print(f"   👤 Name: {record['name']}")
                print(f"   🏢 Committee: {record['committee']}")
                print(f"   📅 Date: {record['submission_date']}")
                
                confirmation = input("⚠️  Are you sure you want to delete this record? (yes/no): ").lower()
                if confirmation != 'yes':
                    print("❌ Deletion cancelled")
                    return False
                
                cursor.execute('DELETE FROM submissions WHERE id = %s', (record_id,))
            else:
                print("❌ Please provide either submission_id or record_id")
                return False
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            if rows_affected > 0:
                print("✅ Record deleted successfully!")
                return True
            else:
                print("❌ No record was deleted")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting record: {e}")
            return False
    
    def view_records(self, committee: str = None, search_name: str = None, 
                    limit: int = None) -> List[Dict]:
        """View records with optional filtering"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build query with filters
            query = '''
                SELECT id, submission_id, name, committee, social_media_links,
                       photo_filename, submission_date
                FROM submissions
            '''
            
            conditions = []
            params = []
            
            if committee:
                conditions.append("committee LIKE %s")
                params.append(f"%{committee}%")
            
            if search_name:
                conditions.append("name LIKE %s")
                params.append(f"%{search_name}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY submission_date DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"❌ Error viewing records: {e}")
            return []
    
    def get_record_by_id(self, submission_id: str) -> Optional[Dict]:
        """Get a specific record by submission ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM submissions WHERE submission_id = %s', (submission_id,))
            record = cursor.fetchone()
            conn.close()
            
            return record
            
        except Exception as e:
            print(f"❌ Error getting record: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total records
            cursor.execute('SELECT COUNT(*) as total FROM submissions')
            total_records = cursor.fetchone()['total']
            
            # Records by committee
            cursor.execute('''
                SELECT committee, COUNT(*) as count 
                FROM submissions 
                GROUP BY committee 
                ORDER BY count DESC
            ''')
            committee_stats = cursor.fetchall()
            
            # Recent records (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) as recent 
                FROM submissions 
                WHERE submission_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''')
            recent_records = cursor.fetchone()['recent']
            
            # Records with social media
            cursor.execute('''
                SELECT COUNT(*) as with_social 
                FROM submissions 
                WHERE social_media_links IS NOT NULL AND social_media_links != ''
            ''')
            with_social_media = cursor.fetchone()['with_social']
            
            conn.close()
            
            return {
                'total_records': total_records,
                'committee_stats': committee_stats,
                'recent_records': recent_records,
                'with_social_media': with_social_media
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def export_to_csv(self, filename: str = None) -> bool:
        """Export all records to CSV"""
        try:
            records = self.view_records()
            if not records:
                print("❌ No records to export")
                return False
            
            df = pd.DataFrame(records)
            
            if filename is None:
                filename = f"committee_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            df.to_csv(filename, index=False)
            print(f"✅ Data exported to: {filename}")
            print(f"📊 Total records exported: {len(records)}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False

class CLIInterface:
    """Command Line Interface for the CRUD operations"""
    
    def __init__(self):
        self.db = CommitteeRegistrationDB()
        
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("🎯 COMMITTEE REGISTRATION MANAGEMENT SYSTEM")
        print("="*50)
        print("1. 📝 Add New Registration")
        print("2. 👀 View Registrations")
        print("3. 🗑️  Delete Registration")
        print("4. 🔍 Search Records")
        print("5. 📊 View Statistics")
        print("6. 📥 Export to CSV")
        print("7. 🔧 Initialize Database")
        print("8. ❌ Exit")
        print("="*50)
    
    def add_registration(self):
        """Add a new registration through CLI"""
        print("\n📝 ADD NEW REGISTRATION")
        print("-" * 30)
        
        name = input("👤 Enter full name: ").strip()
        if not name:
            print("❌ Name is required!")
            return
        
        committee = input("🏢 Enter committee name: ").strip()
        if not committee:
            print("❌ Committee is required!")
            return
        
        social_media = input("🔗 Enter social media links (comma-separated, optional): ").strip()
        social_media = social_media if social_media else None
        
        photo_path = input("📷 Enter photo file path (optional): ").strip()
        if photo_path and not os.path.exists(photo_path):
            print(f"⚠️  Photo file not found: {photo_path}")
            photo_path = None
        
        if self.db.add_record(name, committee, social_media, photo_path):
            print("\n🎉 Registration added successfully!")
        else:
            print("\n❌ Failed to add registration!")
    
    def view_registrations(self):
        """View registrations with filtering options"""
        print("\n👀 VIEW REGISTRATIONS")
        print("-" * 30)
        
        # Filter options
        committee_filter = input("🏢 Filter by committee (optional): ").strip()
        committee_filter = committee_filter if committee_filter else None
        
        name_search = input("🔍 Search by name (optional): ").strip()
        name_search = name_search if name_search else None
        
        try:
            limit = input("📊 Limit results (optional, press Enter for all): ").strip()
            limit = int(limit) if limit else None
        except ValueError:
            limit = None
        
        records = self.db.view_records(committee_filter, name_search, limit)
        
        if not records:
            print("\n❌ No records found!")
            return
        
        print(f"\n📋 FOUND {len(records)} RECORD(S)")
        print("=" * 80)
        
        for i, record in enumerate(records, 1):
            print(f"\n📄 RECORD #{i}")
            print(f"   🆔 ID: {record['id']}")
            print(f"   🎫 Submission ID: {record['submission_id']}")
            print(f"   👤 Name: {record['name']}")
            print(f"   🏢 Committee: {record['committee']}")
            print(f"   📅 Date: {record['submission_date']}")
            
            if record['social_media_links']:
                print(f"   🔗 Social Media: {record['social_media_links']}")
            
            if record['photo_filename']:
                print(f"   📷 Photo: {record['photo_filename']}")
            
            print("-" * 80)
    
    def delete_registration(self):
        """Delete a registration"""
        print("\n🗑️  DELETE REGISTRATION")
        print("-" * 30)
        
        print("Choose deletion method:")
        print("1. Delete by Submission ID")
        print("2. Delete by Database ID")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            submission_id = input("🎫 Enter submission ID: ").strip()
            if submission_id:
                self.db.delete_record(submission_id=submission_id)
            else:
                print("❌ Submission ID is required!")
        
        elif choice == "2":
            try:
                record_id = int(input("🆔 Enter database ID: ").strip())
                self.db.delete_record(record_id=record_id)
            except ValueError:
                print("❌ Invalid database ID!")
        
        else:
            print("❌ Invalid choice!")
    
    def search_records(self):
        """Advanced search functionality"""
        print("\n🔍 SEARCH RECORDS")
        print("-" * 30)
        
        search_term = input("🔍 Enter search term (name or committee): ").strip()
        
        if not search_term:
            print("❌ Search term is required!")
            return
        
        # Search in both name and committee
        name_results = self.db.view_records(search_name=search_term)
        committee_results = self.db.view_records(committee=search_term)
        
        # Combine and deduplicate results
        all_results = {r['id']: r for r in name_results + committee_results}.values()
        
        if not all_results:
            print(f"\n❌ No records found for: '{search_term}'")
            return
        
        print(f"\n🎯 SEARCH RESULTS FOR: '{search_term}'")
        print(f"📊 Found {len(all_results)} record(s)")
        print("=" * 80)
        
        for i, record in enumerate(all_results, 1):
            print(f"\n📄 RESULT #{i}")
            print(f"   🆔 ID: {record['id']}")
            print(f"   🎫 Submission ID: {record['submission_id']}")
            print(f"   👤 Name: {record['name']}")
            print(f"   🏢 Committee: {record['committee']}")
            print(f"   📅 Date: {record['submission_date']}")
            print("-" * 80)
    
    def view_statistics(self):
        """View database statistics"""
        print("\n📊 DATABASE STATISTICS")
        print("-" * 30)
        
        stats = self.db.get_statistics()
        
        if not stats:
            print("❌ Unable to fetch statistics!")
            return
        
        print(f"📈 Total Registrations: {stats['total_records']}")
        print(f"📅 Recent (Last 7 days): {stats['recent_records']}")
        print(f"🔗 With Social Media: {stats['with_social_media']}")
        
        if stats['committee_stats']:
            print("\n🏢 REGISTRATIONS BY COMMITTEE:")
            print("-" * 40)
            for committee in stats['committee_stats']:
                print(f"   {committee['committee']}: {committee['count']}")
    
    def export_data(self):
        """Export data to CSV"""
        print("\n📥 EXPORT DATA")
        print("-" * 30)
        
        filename = input("📁 Enter filename (press Enter for auto-generated): ").strip()
        filename = filename if filename else None
        
        if self.db.export_to_csv(filename):
            print("\n✅ Export completed successfully!")
        else:
            print("\n❌ Export failed!")
    
    def run(self):
        """Main program loop"""
        print("🚀 Starting Committee Registration Management System...")
        
        # Try to initialize database
        if not self.db.init_database():
            print("❌ Failed to initialize database. Please check your configuration.")
            return
        
        while True:
            try:
                self.display_menu()
                choice = input("\n🎯 Enter your choice (1-8): ").strip()
                
                if choice == "1":
                    self.add_registration()
                elif choice == "2":
                    self.view_registrations()
                elif choice == "3":
                    self.delete_registration()
                elif choice == "4":
                    self.search_records()
                elif choice == "5":
                    self.view_statistics()
                elif choice == "6":
                    self.export_data()
                elif choice == "7":
                    self.db.init_database()
                elif choice == "8":
                    print("\n👋 Thank you for using the system. Goodbye!")
                    break
                else:
                    print("\n❌ Invalid choice! Please select 1-8.")
                
                input("\n⏸️  Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Program interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("\n⏸️  Press Enter to continue...")

def main():
    """Main function"""
    try:
        cli = CLIInterface()
        cli.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Please check your database configuration and try again.")

if __name__ == "__main__":
    main()
