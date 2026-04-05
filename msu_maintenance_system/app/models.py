"""
Database Models for MSU Maintenance System

SQLAlchemy ORM models for user authentication and job management.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .extensions import db

class User(UserMixin, db.Model):
    """User model for authentication with role-based access."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='staff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_staff(self):
        """Check if user has staff role."""
        return self.role == 'staff'
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_maintenance_admin(self):
        """Check if user has maintenance_admin role."""
        return self.role == 'maintenance_admin'
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class JobRequest(db.Model):
    """Job request model for maintenance requests."""
    
    __tablename__ = 'job_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')
    status = db.Column(db.String(20), nullable=False, default='PENDING')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationship
    submitter = db.relationship('User', backref='job_requests')
    
    def __repr__(self):
        return f'<JobRequest {self.id}: {self.category}>'


class Assignment(db.Model):
    """Assignment model for job assignments."""
    
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requests.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ASSIGNED')
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    job = db.relationship('JobRequest', backref='assignments')
    worker = db.relationship('Worker', backref='assignments')
    
    def __repr__(self):
        return f'<Assignment {self.id}: Worker {self.worker_id} -> Job {self.job_id}>'


class Material(db.Model):
    """Material model for job materials."""
    
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requests.id'), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    unit = db.Column(db.String(30), nullable=False, default='units')
    quantity_required = db.Column(db.Numeric(10,2), nullable=False)
    quantity_used = db.Column(db.Numeric(10,2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationship
    job = db.relationship('JobRequest', backref='materials')
    
    def __repr__(self):
        return f'<Material {self.id}: {self.item_name} ({self.quantity_required} {self.unit})>'


class Worker(db.Model):
    """Worker model for maintenance workers."""
    
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    full_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    skill_category = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='worker_profile')
    
    def __repr__(self):
        return f'<Worker {self.id}: {self.full_name} ({self.skill_category})>'


class JobStatusHistory(db.Model):
    """Job status history model for audit trail."""
    
    __tablename__ = 'job_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requests.id'), nullable=False)
    from_status = db.Column(db.String(20), nullable=True)
    to_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    job = db.relationship('JobRequest', backref='status_history')
    changer = db.relationship('User', backref='status_changes')
    
    def __repr__(self):
        return f'<JobStatusHistory {self.id}: Job {self.job_id} {self.from_status} → {self.to_status}>'
