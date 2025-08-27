#!/usr/bin/env python3
"""
Simple CRUD Operations Script
A lightweight Python script for Add, Delete, and View operations
using JSON file storage (no database required for testing).
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class SimpleRegistrationManager:
    """Simple class to handle CRUD operations using JSON file storage"""
    
    def __init__(self, data_file: str = "registrations.json"):
        """Initialize with data file"""
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict]:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self) -> bool:
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    def add_record(self, name: str, committee: str, social_media_links: str = None, 
                   email: str = None, phone: str = None) -> bool:
        """Add a new registration record"""
        try:
            # Generate unique ID
            record_id = str(uuid.uuid4())[:8].upper()
            
            # Create new record
            new_record = {
                "id": len(self.data) + 1,
                "submission_id": record_id,
                "name": name.strip(),
                "committee": committee.strip(),
                "social_media_links": social_media_links.strip() if social_media_links else None,
                "email": email.strip() if email else None,
                "phone": phone.strip() if phone else None,
                "submission_date": datetime.now().isoformat()
            }
            
            self.data.append(new_record)
            
            if self.save_data():
                print(f"✅ Record added successfully!")
                print(f"📝 Submission ID: {record_id}")
                print(f"👤 Name: {name}")
                print(f"🏢 Committee: {committee}")
                return True
            else:
                print("❌ Failed to save record")
                return False
                
        except Exception as e:
            print(f"❌ Error adding record: {e}")
            return False
    
    def delete_record(self, submission_id: str = None, record_id: int = None) -> bool:
        """Delete a record by submission_id or record id"""
        try:
            record_to_delete = None
            index_to_delete = None
            
            if submission_id:
                for i, record in enumerate(self.data):
                    if record.get('submission_id') == submission_id:
                        record_to_delete = record
                        index_to_delete = i
                        break
            elif record_id:
                for i, record in enumerate(self.data):
                    if record.get('id') == record_id:
                        record_to_delete = record
                        index_to_delete = i
                        break
            
            if not record_to_delete:
                identifier = submission_id if submission_id else record_id
                print(f"❌ No record found with ID: {identifier}")
                return False
            
            print(f"📋 Record to delete:")
            print(f"   👤 Name: {record_to_delete['name']}")
            print(f"   🏢 Committee: {record_to_delete['committee']}")
            print(f"   📅 Date: {record_to_delete['submission_date']}")
            
            confirmation = input("⚠️  Are you sure you want to delete this record? (yes/no): ").lower()
            if confirmation != 'yes':
                print("❌ Deletion cancelled")
                return False
            
            self.data.pop(index_to_delete)
            
            if self.save_data():
                print("✅ Record deleted successfully!")
                return True
            else:
                print("❌ Failed to save changes")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting record: {e}")
            return False
    
    def view_records(self, committee: str = None, search_name: str = None, 
                    limit: int = None) -> List[Dict]:
        """View records with optional filtering"""
        try:
            filtered_data = self.data.copy()
            
            if committee:
                filtered_data = [r for r in filtered_data 
                               if committee.lower() in r.get('committee', '').lower()]
            
            if search_name:
                filtered_data = [r for r in filtered_data 
                               if search_name.lower() in r.get('name', '').lower()]
            
            # Sort by submission date (newest first)
            filtered_data.sort(key=lambda x: x.get('submission_date', ''), reverse=True)
            
            if limit:
                filtered_data = filtered_data[:limit]
            
            return filtered_data
            
        except Exception as e:
            print(f"❌ Error viewing records: {e}")
            return []
    
    def get_record_by_id(self, submission_id: str) -> Optional[Dict]:
        """Get a specific record by submission ID"""
        for record in self.data:
            if record.get('submission_id') == submission_id:
                return record
        return None
    
    def get_statistics(self) -> Dict:
        """Get data statistics"""
        try:
            total_records = len(self.data)
            
            # Count by committee
            committees = {}
            for record in self.data:
                committee = record.get('committee', 'Unknown')
                committees[committee] = committees.get(committee, 0) + 1
            
            # Count recent records (last 7 days)
            recent_count = 0
            seven_days_ago = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) 
                            - datetime.timedelta(days=7))
            
            for record in self.data:
                try:
                    record_date = datetime.fromisoformat(record.get('submission_date', ''))
                    if record_date >= seven_days_ago:
                        recent_count += 1
                except:
                    continue
            
            # Count records with social media
            with_social_media = len([r for r in self.data 
                                   if r.get('social_media_links')])
            
            return {
                'total_records': total_records,
                'committee_stats': [{'committee': k, 'count': v} for k, v in committees.items()],
                'recent_records': recent_count,
                'with_social_media': with_social_media
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def export_to_csv(self, filename: str = None) -> bool:
        """Export data to CSV"""
        try:
            if not self.data:
                print("❌ No data to export")
                return False
            
            if filename is None:
                filename = f"registrations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Convert to CSV manually (without pandas dependency)
            headers = ['id', 'submission_id', 'name', 'committee', 'social_media_links', 
                      'email', 'phone', 'submission_date']
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Write headers
                f.write(','.join(headers) + '\n')
                
                # Write data
                for record in self.data:
                    row = []
                    for header in headers:
                        value = record.get(header, '')
                        # Handle commas and quotes in data
                        if ',' in str(value) or '"' in str(value):
                            value = f'"{str(value).replace('"', '""')}"'
                        row.append(str(value))
                    f.write(','.join(row) + '\n')
            
            print(f"✅ Data exported to: {filename}")
            print(f"📊 Total records exported: {len(self.data)}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False

class SimpleCLI:
    """Simple Command Line Interface"""
    
    def __init__(self):
        self.manager = SimpleRegistrationManager()
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("🎯 SIMPLE REGISTRATION MANAGEMENT SYSTEM")
        print("="*50)
        print("1. 📝 Add New Registration")
        print("2. 👀 View All Registrations")
        print("3. 🗑️  Delete Registration")
        print("4. 🔍 Search Records")
        print("5. 📊 View Statistics")
        print("6. 📥 Export to CSV")
        print("7. 🧪 Add Sample Data")
        print("8. ❌ Exit")
        print("="*50)
    
    def add_registration(self):
        """Add new registration"""
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
        
        social_media = input("🔗 Enter social media links (optional): ").strip()
        email = input("📧 Enter email (optional): ").strip()
        phone = input("📱 Enter phone number (optional): ").strip()
        
        self.manager.add_record(name, committee, social_media, email, phone)
    
    def view_registrations(self):
        """View all registrations"""
        print("\n👀 VIEW REGISTRATIONS")
        print("-" * 30)
        
        # Filter options
        committee_filter = input("🏢 Filter by committee (optional): ").strip()
        committee_filter = committee_filter if committee_filter else None
        
        name_search = input("🔍 Search by name (optional): ").strip()
        name_search = name_search if name_search else None
        
        try:
            limit = input("📊 Limit results (optional): ").strip()
            limit = int(limit) if limit else None
        except ValueError:
            limit = None
        
        records = self.manager.view_records(committee_filter, name_search, limit)
        
        if not records:
            print("\n❌ No records found!")
            return
        
        print(f"\n📋 FOUND {len(records)} RECORD(S)")
        print("=" * 80)
        
        for i, record in enumerate(records, 1):
            print(f"\n📄 RECORD #{i}")
            print(f"   🆔 ID: {record.get('id', 'N/A')}")
            print(f"   🎫 Submission ID: {record.get('submission_id', 'N/A')}")
            print(f"   👤 Name: {record.get('name', 'N/A')}")
            print(f"   🏢 Committee: {record.get('committee', 'N/A')}")
            print(f"   📅 Date: {record.get('submission_date', 'N/A')}")
            
            if record.get('email'):
                print(f"   📧 Email: {record['email']}")
            
            if record.get('phone'):
                print(f"   📱 Phone: {record['phone']}")
            
            if record.get('social_media_links'):
                print(f"   🔗 Social Media: {record['social_media_links']}")
            
            print("-" * 80)
    
    def delete_registration(self):
        """Delete registration"""
        print("\n🗑️  DELETE REGISTRATION")
        print("-" * 30)
        
        print("Choose deletion method:")
        print("1. Delete by Submission ID")
        print("2. Delete by Record ID")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            submission_id = input("🎫 Enter submission ID: ").strip()
            if submission_id:
                self.manager.delete_record(submission_id=submission_id)
            else:
                print("❌ Submission ID is required!")
        
        elif choice == "2":
            try:
                record_id = int(input("🆔 Enter record ID: ").strip())
                self.manager.delete_record(record_id=record_id)
            except ValueError:
                print("❌ Invalid record ID!")
        
        else:
            print("❌ Invalid choice!")
    
    def search_records(self):
        """Search records"""
        print("\n🔍 SEARCH RECORDS")
        print("-" * 30)
        
        search_term = input("🔍 Enter search term: ").strip()
        
        if not search_term:
            print("❌ Search term is required!")
            return
        
        # Search in both name and committee
        name_results = self.manager.view_records(search_name=search_term)
        committee_results = self.manager.view_records(committee=search_term)
        
        # Combine results
        all_results = list({r['submission_id']: r for r in name_results + committee_results}.values())
        
        if not all_results:
            print(f"\n❌ No records found for: '{search_term}'")
            return
        
        print(f"\n🎯 SEARCH RESULTS FOR: '{search_term}'")
        print(f"📊 Found {len(all_results)} record(s)")
        print("=" * 80)
        
        for i, record in enumerate(all_results, 1):
            print(f"\n📄 RESULT #{i}")
            print(f"   🎫 Submission ID: {record.get('submission_id', 'N/A')}")
            print(f"   👤 Name: {record.get('name', 'N/A')}")
            print(f"   🏢 Committee: {record.get('committee', 'N/A')}")
            print("-" * 80)
    
    def view_statistics(self):
        """View statistics"""
        print("\n📊 STATISTICS")
        print("-" * 30)
        
        stats = self.manager.get_statistics()
        
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
        """Export data"""
        filename = input("📁 Enter filename (or press Enter for auto): ").strip()
        filename = filename if filename else None
        self.manager.export_to_csv(filename)
    
    def add_sample_data(self):
        """Add sample data for testing"""
        print("\n🧪 ADDING SAMPLE DATA")
        print("-" * 30)
        
        sample_data = [
            ("John Doe", "Executive Committee", "https://linkedin.com/in/johndoe", "john@example.com", "+1234567890"),
            ("Jane Smith", "Technical Committee", "https://github.com/janesmith", "jane@example.com", "+1234567891"),
            ("Bob Johnson", "Marketing Committee", "https://twitter.com/bobjohnson", "bob@example.com", "+1234567892"),
            ("Alice Wilson", "Executive Committee", "https://linkedin.com/in/alicewilson", "alice@example.com", "+1234567893"),
            ("Charlie Brown", "Event Committee", None, "charlie@example.com", None)
        ]
        
        added_count = 0
        for name, committee, social, email, phone in sample_data:
            if self.manager.add_record(name, committee, social, email, phone):
                added_count += 1
        
        print(f"\n✅ Added {added_count} sample records!")
    
    def run(self):
        """Main program loop"""
        print("🚀 Starting Simple Registration Management System...")
        print(f"📁 Data will be stored in: {self.manager.data_file}")
        
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
                    self.add_sample_data()
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
    cli = SimpleCLI()
    cli.run()

if __name__ == "__main__":
    main()
