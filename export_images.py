#!/usr/bin/env python3
"""
Image Export Utility for Committee Submissions Database
This script exports images from the MySQL database to local files.
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    return pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        db=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
    )

def export_all_images():
    """Export all images from database to local files"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create exports directory if it doesn't exist
    export_dir = "exported_images"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Get all submissions with images
    cursor.execute("""
        SELECT submission_id, name, photo_filename, photo_data 
        FROM submissions 
        WHERE photo_data IS NOT NULL
        ORDER BY submission_date DESC
    """)
    
    results = cursor.fetchall()
    
    for row in results:
        submission_id = row['submission_id']
        name = row['name']
        original_filename = row['photo_filename']
        photo_data = row['photo_data']
        
        # Create safe filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        file_extension = os.path.splitext(original_filename)[1] if original_filename else '.jpg'
        filename = f"{submission_id}_{safe_name}{file_extension}"
        filepath = os.path.join(export_dir, filename)
        
        # Write image data to file
        try:
            with open(filepath, 'wb') as f:
                f.write(photo_data)
            print(f"✅ Exported: {filename}")
        except Exception as e:
            print(f"❌ Error exporting {filename}: {e}")
    
    conn.close()
    print(f"\n🎉 Export complete! Images saved to '{export_dir}' directory.")

def export_single_image(submission_id):
    """Export a single image by submission ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT submission_id, name, photo_filename, photo_data 
        FROM submissions 
        WHERE submission_id = %s AND photo_data IS NOT NULL
    """, (submission_id,))
    
    result = cursor.fetchone()
    
    if result:
        name = result['name']
        original_filename = result['photo_filename']
        photo_data = result['photo_data']
        
        # Create safe filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        file_extension = os.path.splitext(original_filename)[1] if original_filename else '.jpg'
        filename = f"{submission_id}_{safe_name}{file_extension}"
        
        # Write image data to file
        try:
            with open(filename, 'wb') as f:
                f.write(photo_data)
            print(f"✅ Exported: {filename}")
        except Exception as e:
            print(f"❌ Error exporting {filename}: {e}")
    else:
        print(f"❌ No image found for submission ID: {submission_id}")
    
    conn.close()

def list_submissions():
    """List all submissions with image info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            submission_id,
            name,
            committee,
            photo_filename,
            CASE 
                WHEN photo_data IS NOT NULL THEN CONCAT(ROUND(LENGTH(photo_data)/1024, 2), ' KB')
                ELSE 'No image'
            END as image_size,
            submission_date
        FROM submissions 
        ORDER BY submission_date DESC
    """)
    
    results = cursor.fetchall()
    
    print("\n📋 All Submissions:")
    print("-" * 80)
    print(f"{'ID':<10} {'Name':<20} {'Committee':<20} {'Filename':<15} {'Size':<10}")
    print("-" * 80)
    
    for row in results:
        print(f"{row['submission_id']:<10} {row['name'][:19]:<20} {row['committee'][:19]:<20} {(row['photo_filename'] or 'N/A')[:14]:<15} {row['image_size']:<10}")
    
    conn.close()

if __name__ == "__main__":
    print("🖼️  Committee Submissions Image Export Utility")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all submissions")
        print("2. Export all images")
        print("3. Export single image by ID")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            list_submissions()
        elif choice == "2":
            export_all_images()
        elif choice == "3":
            submission_id = input("Enter submission ID: ").strip()
            if submission_id:
                export_single_image(submission_id)
            else:
                print("❌ Please enter a valid submission ID")
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
