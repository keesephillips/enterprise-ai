from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from.models import User  
from.audit import log_audit_event, app_logger 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat')) 
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip_address = request.remote_addr

        app_logger.info(f"Login attempt for user: {username} from IP: {ip_address}")

        user_object = User.find_by_username(username)

        if user_object and User.check_password(username, password):
            login_user(user_object)
            log_audit_event(action="LOGIN_SUCCESS", details=f"User '{username}' logged in.", username=username, ip_address=ip_address)
            app_logger.info(f"User '{username}' logged in successfully.")
            return redirect(url_for('main.chat')) 
        else:
            flash('Invalid username or password.') 
            log_audit_event(action="LOGIN_FAILURE", details=f"Failed login attempt for user '{username}'.", username=username, ip_address=ip_address)
            app_logger.warning(f"Failed login attempt for user '{username}'.")
            return render_template('login.html', info='Invalid username or password.') 

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    ip_address = request.remote_addr
    logout_user()
    log_audit_event(action="LOGOUT", details=f"User '{username}' logged out.", username=username, ip_address=ip_address)
    app_logger.info(f"User '{username}' logged out.")
    flash('You have been logged out.') 
    return redirect(url_for('auth.login')) 