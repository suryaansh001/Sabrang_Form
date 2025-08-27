import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import uuid
import base64
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    # Try to get from streamlit secrets first, then from environment variables
    try:
        # Streamlit secrets
        db_config = {
            'host': st.secrets.get("DB_HOST", os.getenv('DB_HOST')),
            'port': int(st.secrets.get("DB_PORT", os.getenv('DB_PORT', 3306))),
            'user': st.secrets.get("DB_USER", os.getenv('DB_USER')),
            'password': st.secrets.get("DB_PASSWORD", os.getenv('DB_PASSWORD')),
            'db': st.secrets.get("DB_NAME", os.getenv('DB_NAME')),
            'timeout': int(st.secrets.get("TIMEOUT", os.getenv('TIMEOUT', 10)))
        }
    except Exception:
        # Fallback to environment variables
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'db': os.getenv('DB_NAME'),
            'timeout': int(os.getenv('TIMEOUT', 10))
        }
    
    # Validate required parameters
    if not all([db_config['host'], db_config['user'], db_config['password'], db_config['db']]):
        st.error("Database configuration is missing. Please check your environment variables or Streamlit secrets.")
        st.stop()
    
    return pymysql.connect(
        charset="utf8mb4",
        connect_timeout=db_config['timeout'],
        cursorclass=pymysql.cursors.DictCursor,
        db=db_config['db'],
        host=db_config['host'],
        password=db_config['password'],
        read_timeout=db_config['timeout'],
        port=db_config['port'],
        user=db_config['user'],
        write_timeout=db_config['timeout'],
    )

def get_sqlalchemy_engine():
    """Create and return SQLAlchemy engine for pandas compatibility"""
    try:
        # Try Streamlit secrets first
        db_user = st.secrets.get("DB_USER", os.getenv('DB_USER'))
        db_password = st.secrets.get("DB_PASSWORD", os.getenv('DB_PASSWORD'))
        db_host = st.secrets.get("DB_HOST", os.getenv('DB_HOST'))
        db_port = st.secrets.get("DB_PORT", os.getenv('DB_PORT', 3306))
        db_name = st.secrets.get("DB_NAME", os.getenv('DB_NAME'))
    except Exception:
        # Fallback to environment variables
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT', 3306)
        db_name = os.getenv('DB_NAME')
    
    db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

# Database setup
def init_database():
    """Initialize the MySQL database and create tables if they don't exist"""
    try:
        conn = get_db_connection()
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
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.error("Please check your database connection settings.")
        return False

def save_submission(data):
    """Save form submission to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions 
            (submission_id, name, committee, social_media_links, photo_filename, photo_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', data)
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            return True
        else:
            st.error("No rows were inserted into the database")
            return False
            
    except pymysql.Error as e:
        st.error(f"Database error: {e}")
        return False
    except Exception as e:
        st.error(f"Error saving submission: {e}")
        return False

def get_all_submissions():
    """Retrieve all submissions from database"""
    engine = get_sqlalchemy_engine()
    
    query = '''
        SELECT id, submission_id, name, committee, social_media_links,
               photo_filename, submission_date
        FROM submissions
        ORDER BY submission_date DESC
    '''
    
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading submissions: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()

def get_photo_data(submission_id):
    """Retrieve photo data for a specific submission"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT photo_data FROM submissions WHERE submission_id = %s', (submission_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['photo_data'] if result else None

def parse_social_media_links(links_string):
    """Parse comma-separated social media links"""
    if not links_string:
        return []
    return [link.strip() for link in links_string.split(',') if link.strip()]

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Committee Member Portal",
        page_icon="👥",
        layout="wide"
    )
    
    # Initialize database
    if not init_database():
        st.error("❌ Database initialization failed. Please check your configuration.")
        st.stop()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Submit Form", "View Submissions", "Admin Panel"])
    
    if page == "Submit Form":
        show_submission_form()
    elif page == "View Submissions":
        show_submissions()
    elif page == "Admin Panel":
        show_admin_panel()

def show_submission_form():
    st.title("👥 Committee Member Registration Portal")
    st.write("Please fill out the form below to register as a committee member.")
    
    with st.form("committee_submission_form", clear_on_submit=True):
        # Name field
        name = st.text_input("Full Name *", 
                           placeholder="Enter your full name",
                           help="Enter your complete name as you want it to appear")
        
        # Committee field
        committee = st.text_input("Committee *", 
                                 placeholder="Enter the committee name (e.g., Executive Committee, Technical Committee, etc.)",
                                 help="Enter the name of the committee you want to join")
        
        # Social Media Links field
        social_media_links = st.text_area("Social Media Links", 
                                        placeholder="https://linkedin.com/in/yourprofile, https://twitter.com/yourhandle, https://instagram.com/yourhandle",
                                        help="Enter your social media profile links separated by commas. Include full URLs (starting with https://)")
        
        # Image upload
        uploaded_file = st.file_uploader("Upload Your Photo *", 
                                       type=['png', 'jpg', 'jpeg'], 
                                       help="Upload a clear photo of yourself (Supported formats: PNG, JPG, JPEG | Max size: 5MB)")
        
        # Preview uploaded image
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(image, caption="Preview of uploaded photo", width=300)
        
        # Submit button
        submitted = st.form_submit_button("Submit Registration", type="primary")
        
        if submitted:
            # Validation
            if not name or not committee or not uploaded_file:
                st.error("Please fill in all required fields marked with *")
            elif len(committee.strip()) < 2:
                st.error("Please enter a valid committee name (at least 2 characters)")
            else:
                # Validate social media links if provided
                if social_media_links:
                    links = parse_social_media_links(social_media_links)
                    invalid_links = []
                    for link in links:
                        if not (link.startswith('http://') or link.startswith('https://')):
                            invalid_links.append(link)
                    
                    if invalid_links:
                        st.error(f"Please provide valid URLs starting with http:// or https:// for: {', '.join(invalid_links)}")
                        return
                
                # Generate unique submission ID
                submission_id = str(uuid.uuid4())[:8].upper()
                
                # Convert image to binary data
                photo_data = uploaded_file.getvalue()
                
                # Prepare data for database
                data = (
                    submission_id,
                    name.strip(),
                    committee.strip(),
                    social_media_links.strip() if social_media_links else None,
                    uploaded_file.name,
                    photo_data
                )
                
                # Save to database
                if save_submission(data):
                    st.success(f"✅ Registration submitted and saved to database successfully!")
                    st.info(f"Your submission ID is: **{submission_id}**")
                    st.info(f"� Data has been securely stored in the MySQL database")
                    st.balloons()
                    
                    # Show summary
                    st.subheader("Registration Summary:")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Committee:** {committee}")
                    if social_media_links:
                        st.write("**Social Media Links:**")
                        for link in parse_social_media_links(social_media_links):
                            st.write(f"- {link}")
                else:
                    st.error("❌ Failed to save registration to database. Please try again.")

def show_submissions():
    st.title("📋 Committee Member Registrations")
    
    # Password protection for viewing submissions
    if 'submissions_authenticated' not in st.session_state:
        st.session_state.submissions_authenticated = False
    
    if not st.session_state.submissions_authenticated:
        st.info("🔒 This section is password protected. Please enter the password to view submissions.")
        password = st.text_input("Enter password to view submissions:", type="password")
        if st.button("Access Submissions"):
            try:
                # Use the same admin password for submissions viewing
                view_password = st.secrets.get("ADMIN_PASSWORD", os.getenv('ADMIN_PASSWORD', 'admin123'))
            except Exception:
                view_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            if password == view_password:
                st.session_state.submissions_authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid password")
        return
    
    # Add logout button for submissions
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔓 Logout from Submissions"):
            st.session_state.submissions_authenticated = False
            st.rerun()
    
    try:
        df = get_all_submissions()
        
        if df.empty:
            st.info("No registrations found.")
        else:
            st.write(f"Total registrations: **{len(df)}**")
            
            # Add search and filter options
            col1, col2 = st.columns(2)
            with col1:
                search_name = st.text_input("Search by name:", placeholder="Enter name to search...")
            with col2:
                # Get unique committees for filter
                committees = df['committee'].unique().tolist()
                committee_filter = st.selectbox("Filter by committee:", ["All Committees"] + committees)
            
            # Apply filters
            filtered_df = df.copy()
            if search_name:
                filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]
            if committee_filter != "All Committees":
                filtered_df = filtered_df[filtered_df['committee'] == committee_filter]
            
            st.write(f"Showing {len(filtered_df)} of {len(df)} registrations")
            
            # Display submissions in an expandable format
            for idx, row in filtered_df.iterrows():
                with st.expander(f"👤 {row['name']} - {row['committee']} (ID: {row['submission_id']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Name:** {row['name']}")
                        st.write(f"**Committee:** {row['committee']}")
                        st.write(f"**Submission Date:** {row['submission_date']}")
                        st.write(f"**Submission ID:** {row['submission_id']}")
                        
                        if row['social_media_links']:
                            st.write("**Social Media Links:**")
                            links = parse_social_media_links(row['social_media_links'])
                            for link in links:
                                st.markdown(f"- [{link}]({link})")
                        else:
                            st.write("**Social Media Links:** Not provided")
                    
                    with col2:
                        # Display photo
                        photo_data = get_photo_data(row['submission_id'])
                        if photo_data:
                            try:
                                image = Image.open(io.BytesIO(photo_data))
                                st.image(image, caption=row['photo_filename'], width=200)
                            except Exception as e:
                                st.error(f"Error loading image: {e}")
                        else:
                            st.write("No photo available")
    
    except Exception as e:
        st.error(f"Error loading registrations: {e}")

def show_admin_panel():
    st.title("🔧 Admin Panel")
    
    # Password protection for admin panel
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        password = st.text_input("Enter admin password:", type="password")
        if st.button("Login"):
            try:
                admin_password = st.secrets.get("ADMIN_PASSWORD", os.getenv('ADMIN_PASSWORD', 'admin123'))
            except Exception:
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            if password == admin_password:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        st.info("Please enter the admin password to access this panel.")
        return
    
    st.success("✅ Admin access granted")
    
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Admin functionalities
    tab1, tab2, tab3 = st.tabs(["📊 Statistics", "📥 Export Data", "🗑️ Database Management"])
    
    with tab1:
        try:
            df = get_all_submissions()
            if not df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Registrations", len(df))
                
                with col2:
                    most_popular_committee = df['committee'].mode().iloc[0] if not df['committee'].mode().empty else "N/A"
                    st.metric("Most Popular Committee", most_popular_committee)
                
                with col3:
                    today_registrations = len(df[df['submission_date'].str.contains(datetime.now().strftime('%Y-%m-%d'))])
                    st.metric("Today's Registrations", today_registrations)
                
                # Charts
                st.subheader("Registrations by Committee")
                committee_counts = df['committee'].value_counts()
                st.bar_chart(committee_counts)
                
                # Social media statistics
                social_media_provided = len(df[df['social_media_links'].notna()])
                st.subheader("Social Media Links")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("With Social Media", social_media_provided)
                with col2:
                    st.metric("Without Social Media", len(df) - social_media_provided)
                
            else:
                st.info("No data available for statistics.")
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
    
    with tab2:
        st.subheader("Export Registration Data")
        
        try:
            df = get_all_submissions()
            if not df.empty:
                # Prepare CSV data (excluding photo data for CSV export)
                export_df = df.drop(columns=['id'], errors='ignore')
                csv_data = export_df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"committee_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ Export data prepared successfully!")
                st.info("Note: Photo data is not included in CSV export due to file size limitations.")
            else:
                st.info("No data to export.")
        except Exception as e:
            st.error(f"Error preparing export: {e}")
    
    with tab3:
        st.subheader("Database Management")
        st.warning("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.button("Confirm Delete All", type="secondary"):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Get count before deletion
                        cursor.execute('SELECT COUNT(*) as count FROM submissions')
                        before_count = cursor.fetchone()['count']
                        
                        # Delete all records
                        cursor.execute('DELETE FROM submissions')
                        conn.commit()
                        
                        # Verify deletion
                        cursor.execute('SELECT COUNT(*) as count FROM submissions')
                        after_count = cursor.fetchone()['count']
                        
                        conn.close()
                        
                        if after_count == 0:
                            st.success(f"✅ Successfully deleted {before_count} records from database!")
                        else:
                            st.warning(f"⚠️ Deletion incomplete. {after_count} records remain.")
                            
                    except Exception as e:
                        st.error(f"❌ Error clearing data: {e}")
        
        with col2:
            st.info("Database: MySQL (Aiven Cloud)")

if __name__ == "__main__":
    main()