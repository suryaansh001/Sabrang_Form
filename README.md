# Committee Member Registration Portal

A Streamlit web application for committee member registration with MySQL database backend.

## Features

- 📝 Committee member registration form
- 🖼️ Photo upload functionality
- 👀 View all registrations
- 🔐 Admin panel with password protection
- 📊 Statistics and analytics
- 📥 Data export to CSV
- 🗑️ Database management tools

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vege
   ```

2. **Create virtual environment**
   ```bash
   python -m venv google
   source google/bin/activate  # On Windows: google\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the database credentials in `.env`

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Streamlit Community Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Set up secrets in Streamlit Community Cloud:**
   - Go to https://share.streamlit.io/
   - Deploy your app
   - In the app settings, add the following secrets:

   ```toml
   # Database Configuration (Aiven MySQL)
   DB_HOST = "your-database-host"
   DB_PORT = 25976
   DB_USER = "your-username"
   DB_PASSWORD = "your-password"
   DB_NAME = "your-database-name"

   # Admin Configuration
   ADMIN_PASSWORD = "your-admin-password"

   # Other Configuration
   TIMEOUT = 10
   ```

3. **Deploy the app** - Streamlit will automatically detect and run `app.py`

## Environment Variables

- `DB_HOST`: MySQL database host
- `DB_PORT`: MySQL database port (default: 3306)
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: MySQL database name
- `ADMIN_PASSWORD`: Admin panel password
- `TIMEOUT`: Database connection timeout (default: 10)

## Database Schema

The application creates a `submissions` table with the following structure:

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

## Admin Panel

Access the admin panel through the navigation sidebar. Default password is `admin123` (change this in your environment variables).

Admin features:
- View registration statistics
- Export data to CSV
- Database management
- Clear all data (with confirmation)

## Security Notes

- Never commit `.env` files or `secrets.toml` to version control
- Change the default admin password before deployment
- Use strong passwords for database access
- Consider implementing additional authentication for production use

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL (Aiven Cloud)
- **Image Processing**: Pillow (PIL)
- **Data Processing**: Pandas
- **Database Connector**: PyMySQL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
