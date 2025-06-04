import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, redirect, url_for
from flask_login import login_required, current_user
from src.models.user import db, User, Role
from src.routes.user import user_bp, login_manager

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')

# Initialize login manager
login_manager.init_app(app)

# Enable database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', '123456')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configure file uploads
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Main routes for department pages
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('user.login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/sales')
@login_required
def sales():
    if not current_user.can_access('sales'):
        return render_template('access_denied.html')
    return render_template('sales.html')

@app.route('/dispatcher')
@login_required
def dispatcher():
    if not current_user.can_access('dispatcher'):
        return render_template('access_denied.html')
    return render_template('dispatcher.html')

@app.route('/purchase')
@login_required
def purchase():
    if not current_user.can_access('purchase'):
        return render_template('access_denied.html')
    return render_template('purchase.html')

# Initialize database and create default roles
@app.before_request
def initialize_database():
    db.create_all()
    
    # Create default roles if they don't exist
    roles = {
        'admin': 'Administrator with full access',
        'employee': 'Regular employee with department-specific access',
        'management': 'Management with access to all departments'
    }
    
    for role_name, description in roles.items():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=description)
            db.session.add(role)
    
    # Create admin user if no users exist
    if not User.query.first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email='admin@example.com',
            department='management'
        )
        admin.set_password('admin123')
        admin.roles.append(admin_role)
        db.session.add(admin)
    
    db.session.commit()

# Fallback route for static files
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
