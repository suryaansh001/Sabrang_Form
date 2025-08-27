# CRUD Operations Scripts

This repository contains two Python scripts for Add, Delete, and View operations for committee registrations:

## 📁 Files Overview

### 1. `crud_operations.py` - Database Version
- **Full-featured CRUD operations** using MySQL database
- **Requires database setup** with your existing MySQL configuration
- **Photo storage support** with BLOB data
- **Advanced filtering and search**
- **Export to CSV functionality**
- **Statistics and analytics**

### 2. `simple_crud.py` - JSON File Version
- **Lightweight CRUD operations** using JSON file storage
- **No database required** - perfect for testing and small-scale use
- **File-based storage** (creates `registrations.json`)
- **All basic CRUD operations**
- **Sample data generation**
- **Export functionality**

## 🚀 Getting Started

### Prerequisites

For `crud_operations.py`:
```bash
pip install pymysql pandas python-dotenv sqlalchemy
```

For `simple_crud.py`:
```bash
# No additional dependencies required - uses only Python standard library
```

### Environment Setup (for Database Version)

Create a `.env` file in your project directory:
```env
DB_HOST=your_database_host
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name
TIMEOUT=10
```

## 📖 Usage

### Running the Database Version
```bash
python crud_operations.py
```

### Running the Simple Version
```bash
python simple_crud.py
```

## 🎯 Features

### Common Features (Both Scripts)
- ✅ **Add new registrations** with name, committee, and contact info
- ✅ **View all registrations** with filtering options
- ✅ **Delete registrations** by ID
- ✅ **Search functionality** by name or committee
- ✅ **Statistics and analytics**
- ✅ **Export to CSV**
- ✅ **Interactive CLI interface**

### Database Version Additional Features
- 📸 **Photo upload support**
- 🔒 **Robust data persistence**
- 📊 **Advanced statistics**
- 🔍 **Complex filtering options**
- 💾 **Binary data storage**

### Simple Version Additional Features
- 🧪 **Sample data generation**
- 📁 **No setup required**
- 🚀 **Quick testing**
- 💾 **Human-readable JSON storage**

## 🎮 Menu Options

Both scripts provide an interactive menu with the following options:

1. **📝 Add New Registration** - Add committee member details
2. **👀 View Registrations** - Browse all registrations with filters
3. **🗑️ Delete Registration** - Remove registrations by ID
4. **🔍 Search Records** - Find specific registrations
5. **📊 View Statistics** - See data analytics
6. **📥 Export to CSV** - Download data
7. **Initialize/Sample Data** - Setup or test data
8. **❌ Exit** - Quit the application

## 📋 Data Fields

### Required Fields
- **Name** - Full name of the committee member
- **Committee** - Committee name they want to join

### Optional Fields
- **Social Media Links** - LinkedIn, Twitter, etc.
- **Email** - Contact email address
- **Phone** - Phone number
- **Photo** - Profile picture (database version only)

## 🔍 Search and Filter Options

- **Filter by Committee** - Show only specific committee members
- **Search by Name** - Find members by partial name match
- **Limit Results** - Control number of results displayed
- **Date Range** - Recent registrations (in statistics)

## 📊 Export Functionality

Both scripts can export data to CSV format with:
- All registration details
- Timestamp information
- Automatic filename generation
- Custom filename support

## 🛠️ Database Schema (for Database Version)

```sql
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    committee VARCHAR(255) NOT NULL,
    social_media_links TEXT,
    photo_filename VARCHAR(255),
    photo_data LONGBLOB,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📁 JSON Structure (for Simple Version)

```json
[
  {
    "id": 1,
    "submission_id": "ABC12345",
    "name": "John Doe",
    "committee": "Executive Committee",
    "social_media_links": "https://linkedin.com/in/johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "submission_date": "2025-01-01T12:00:00"
  }
]
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error (Database Version)**
   - Check your `.env` file configuration
   - Verify database server is running
   - Confirm network connectivity

2. **Permission Error (Simple Version)**
   - Ensure write permissions in the directory
   - Check if `registrations.json` is not locked by another process

3. **Module Import Error**
   - Install required dependencies: `pip install -r requirements.txt`
   - Activate your virtual environment if using one

### Error Messages

- `❌ Database configuration is incomplete` - Check your `.env` file
- `❌ No records found` - Database/file is empty
- `❌ Invalid choice` - Enter a number between 1-8
- `❌ Name is required` - Fill in all required fields

## 🎯 Best Practices

1. **Backup your data** regularly
2. **Use the simple version** for testing and development
3. **Use the database version** for production environments
4. **Validate input data** before submission
5. **Export data periodically** for backup purposes

## 🔐 Security Notes

- The database version includes password protection for admin features
- Never commit your `.env` file to version control
- Use strong database passwords
- Consider encryption for sensitive data

## 🤝 Contributing

Feel free to enhance these scripts by adding:
- Input validation improvements
- Additional export formats (Excel, PDF)
- Email notification features
- Backup and restore functionality
- Web interface integration

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Verify your environment setup
3. Review the error messages carefully
4. Test with the simple version first
