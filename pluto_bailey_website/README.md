# [Pluto] Bailey Heating and Air Success Manuals - Website Guide

This document provides instructions for setting up and running your office website with login functionality, role-based access control, and SIP document management.

## Quick Start Guide

1. **Extract the files** to a location of your choice

2. **Install Python requirements**:
   ```
   pip3 install -r requirements.txt
   ```

3. **Run the website**:
   ```
   PYTHONPATH=/path/to/extracted/folder python3 src/main.py
   ```
   Replace "/path/to/extracted/folder" with the actual path where you extracted the files

4. **Access the website**:
   - Open your browser and go to: http://localhost:8080
   - Log in with default admin credentials:
     * Username: admin
     * Password: admin123

## Features

- **Role-based access control**: Employees can only access their department pages
- **Management access**: Top-level management can access all departments
- **SIP document management**: Upload and manage SIP documents for each department
- **User management**: Create and manage user accounts with appropriate permissions

## Customization

The website has been customized with your company name "[Pluto] Bailey Heating and Air Success Manuals" throughout the interface.

## Sharing with Others

To make the website accessible to others:

1. **For temporary access**: Use ngrok (https://ngrok.com)
   ```
   ngrok http 8080
   ```

2. **For permanent access**: Deploy to PythonAnywhere or similar hosting service
   - See DEPLOYMENT.md for detailed instructions

## File Structure

- `src/` - Contains all source code
  - `src/main.py` - Main application file
  - `src/models/` - Database models
  - `src/routes/` - Route handlers
  - `src/templates/` - HTML templates
  - `src/static/` - Static files (CSS, JS)
- `requirements.txt` - Python dependencies
- `DEPLOYMENT.md` - Detailed deployment instructions

## Troubleshooting

- If you see port conflicts, change the port in src/main.py (line ~90)
- If you have database issues, the application uses SQLite by default
- For any rendering issues, clear your browser cache

For any questions or issues, please refer to the detailed documentation or contact support.
