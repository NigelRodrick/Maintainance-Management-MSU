"""
Admin Full Access Routes
Provides comprehensive admin access to all system data and operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import inspect, text
from app.extensions import db
from app.utils.access_control import admin_only, log_admin_action
from app.models import User, JobRequest, Assignment, Material

admin_full_access_bp = Blueprint('admin_full_access', __name__, url_prefix='/admin/full')


@admin_full_access_bp.route('/models')
@login_required
@admin_only()
@log_admin_action('VIEW_ALL_MODELS', 'System')
def list_all_models():
    """Display all database models with their structure and data."""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        model_info = {}
        for table_name in tables:
            # Validate table name to prevent SQL injection
            valid_tables = ['users', 'job_requests', 'assignments', 'materials']
            if table_name not in valid_tables:
                continue
                
            columns = inspector.get_columns(table_name)
            # Safe query with validated table name to prevent SQL injection
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            model_info[table_name] = {
                'columns': [col['name'] for col in columns],
                'column_count': len(columns),
                'row_count': db.session.execute(count_query).scalar()
            }
        
        return render_template('admin/models.html', models=model_info)
    
    except Exception as e:
        flash(f'Error accessing model data: {str(e)}', 'error')
        return redirect(url_for('admin_full_access.list_all_models'))


@admin_full_access_bp.route('/model/<table_name>')
@login_required
@admin_only()
@log_admin_action('VIEW_MODEL_DATA', 'System')
def view_model_data(table_name):
    """View data for a specific model."""
    try:
        # Validate table name
        valid_tables = ['users', 'job_requests', 'assignments', 'materials']
        if table_name not in valid_tables:
            flash('Invalid table name', 'error')
            return redirect(url_for('admin_full_access.list_all_models'))
        
        # Get table data
        inspector = inspect(db.engine)
        columns = inspector.get_columns(table_name)
        
        # Safe query with validated table name to prevent SQL injection
        query = text(f"SELECT * FROM {table_name} LIMIT 100")
        result = db.session.execute(query)
        data = result.fetchall()
        
        return render_template(
            'admin/model_data.html',
            table_name=table_name,
            columns=columns,
            data=data
        )
    
    except Exception as e:
        flash(f'Error accessing table data: {str(e)}', 'error')
        return redirect(url_for('admin_full_access.list_all_models'))


@admin_full_access_bp.route('/users')
@login_required
@admin_only()
@log_admin_action('VIEW_ALL_USERS', 'User')
def view_all_users():
    """View all users with full details."""
    try:
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    except Exception as e:
        flash(f'Error accessing users: {str(e)}', 'error')
        return redirect(url_for('admin_full_access.list_all_models'))


@admin_full_access_bp.route('/impersonate/<int:user_id>')
@login_required
@admin_only()
@log_admin_action('USER_IMPERSONATION', 'User')
def impersonate_user(user_id):
    """Impersonate another user (admin only)."""
    try:
        user = User.query.get_or_404(user_id)
        # Store original admin in session
        session['original_admin_id'] = current_user.id
        session['impersonating_user_id'] = user.id
        
        flash(f'Now impersonating {user.email}', 'info')
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        flash(f'Error impersonating user: {str(e)}', 'error')
        return redirect(url_for('admin_full_access.view_all_users'))


@admin_full_access_bp.route('/stop-impersonation')
@login_required
def stop_impersonation():
    """Stop impersonating and return to original admin account."""
    try:
        if 'original_admin_id' in session:
            # Clear impersonation
            del session['original_admin_id']
            del session['impersonating_user_id']
            
            flash('Stopped impersonating user', 'info')
        
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        flash(f'Error stopping impersonation: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))
