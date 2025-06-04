# Office Website Deployment Guide

## Overview
This document provides instructions for deploying the Office Website application, which includes login functionality, role-based access control, and SIP document management for different departments.

## Prerequisites
- Python 3.8 or higher
- MySQL database
- Web server (optional for production deployment)

## Local Development Setup

### 1. Set Up Virtual Environment
```bash
cd office_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
The application is configured to use MySQL by default. The database connection settings are in `src/main.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
```

You can modify these settings or use environment variables to configure your database connection.

### 4. Initialize Database
The application will automatically create the database tables and default roles when it first runs.

### 5. Run the Application
```bash
cd office_app
python src/main.py
```

The application will be available at http://localhost:5000

## Default Credentials
On first run, the application creates an admin user:
- Username: admin
- Password: admin123
- Department: management

**Important:** Change this password immediately after first login.

## User Roles
The application includes three predefined roles:
1. **admin** - Full access to all departments and features
2. **management** - Access to all departments
3. **employee** - Access only to their assigned department

## Department Access
- Users can only access their assigned department unless they have admin or management roles
- SIP documents can only be uploaded to departments the user has access to
- Management and admin users can access all departments

## Production Deployment

### Option 1: Using Gunicorn (Recommended)
1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
cd office_app
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'
```

### Option 2: Using a Web Server (Nginx/Apache)
For production environments, it's recommended to use a web server like Nginx or Apache as a reverse proxy.

#### Nginx Configuration Example:
```
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## File Upload Configuration
- SIP document uploads are stored in `src/static/uploads/`
- Maximum file size is set to 16MB by default
- You can modify these settings in `src/main.py`

## Troubleshooting
- If you encounter database connection issues, verify your MySQL credentials and ensure the database exists
- For permission errors with file uploads, check that the application has write access to the uploads directory
- If login fails, ensure the database was properly initialized with the default admin user

## Security Considerations
- Change the default admin password immediately
- Update the SECRET_KEY in `src/main.py` for production
- Consider using HTTPS in production environments
- Regularly backup your database
