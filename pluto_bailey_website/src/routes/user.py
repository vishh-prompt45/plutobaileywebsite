from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash, abort, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from src.models.user import db, User, Role, SIPDocument
import os
from datetime import datetime
import uuid

user_bp = Blueprint('user', __name__)

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'user.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists')
            return redirect(url_for('user.register'))
        
        # Create new user
        user = User(username=username, email=email, department=department)
        user.set_password(password)
        
        # Assign default role (employee)
        employee_role = Role.query.filter_by(name='employee').first()
        if employee_role:
            user.roles.append(employee_role)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('user.login'))
    
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

# SIP document upload routes
@user_bp.route('/upload_sip', methods=['GET', 'POST'])
@login_required
def upload_sip():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        department = request.form.get('department')
        description = request.form.get('description')
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        # Check if user has permission to upload for this department
        if not current_user.can_access(department):
            flash('You do not have permission to upload files for this department')
            return redirect(request.url)
            
        if file:
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Secure filename and add unique identifier
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(uploads_dir, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create SIP document record
            sip_doc = SIPDocument(
                filename=filename,
                department=department,
                upload_date=datetime.now(),
                file_path=unique_filename,
                description=description,
                uploader_id=current_user.id
            )
            
            db.session.add(sip_doc)
            db.session.commit()
            
            flash('File successfully uploaded')
            return redirect(url_for('main.department', department=department))
    
    return render_template('upload_sip.html')

@user_bp.route('/download_sip/<int:doc_id>')
@login_required
def download_sip(doc_id):
    document = SIPDocument.query.get_or_404(doc_id)
    
    # Check if user has permission to access this document
    if not current_user.can_access(document.department):
        abort(403)
    
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(uploads_dir, document.file_path, as_attachment=True, download_name=document.filename)

# API routes for user management
@user_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
        
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if not current_user.is_admin() and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>/roles', methods=['PUT'])
@login_required
def update_user_roles(user_id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
        
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'roles' in data:
        # Clear existing roles
        user.roles = []
        
        # Add new roles
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.commit()
        return jsonify(user.to_dict())
    
    return jsonify({'error': 'Invalid request'}), 400
