"""
Form Validation Classes
WTForms validators for server-side input validation.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField,
    FloatField, PasswordField, BooleanField, HiddenField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, NumberRange, Regexp,
    Optional, ValidationError
)
from app.domain import JobStatus, Priority, UserRole, SkillCategory
import re


class LoginForm(FlaskForm):
    """Login form with validation."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=100, message='Email must be less than 100 characters'),
        Regexp(r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$', 
               message='Must be a valid MSU staff email (username@staff.msu.ac.zw)')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=1, message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """User registration form with validation."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=100, message='Email must be less than 100 characters'),
        Regexp(r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$', 
               message='Must be a valid MSU staff email (username@staff.msu.ac.zw)')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=10, message='Password must be at least 10 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])', 
               message='Password must contain uppercase, lowercase, digit, and special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('staff', 'Staff'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
        ('maintenance_admin', 'Maintenance Admin')
    ], validators=[DataRequired(message='Role is required')])
    
    def validate_password(self, field):
        """Custom password validation."""
        password = field.data
        
        # Check for common weak passwords
        weak_passwords = ['password', '1234567890', 'qwertyuiop', 'admin123', 'staff123']
        if password.lower() in weak_passwords:
            raise ValidationError('Password is too common and weak')
        
        # Check for sequential characters
        if any(ord(password[i]) + 1 == ord(password[i + 1]) for i in range(len(password) - 1)):
            raise ValidationError('Password cannot contain sequential characters')


class ChangePasswordForm(FlaskForm):
    """Password change form with validation."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=10, message='Password must be at least 10 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])', 
               message='Password must contain uppercase, lowercase, digit, and special character')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    def validate_new_password(self, field):
        """Custom new password validation."""
        password = field.data
        
        # Check for common weak passwords
        weak_passwords = ['password', '1234567890', 'qwertyuiop', 'admin123', 'staff123']
        if password.lower() in weak_passwords:
            raise ValidationError('Password is too common and weak')
        
        # Check for sequential characters
        if any(ord(password[i]) + 1 == ord(password[i + 1]) for i in range(len(password) - 1)):
            raise ValidationError('Password cannot contain sequential characters')


class JobRequestForm(FlaskForm):
    """Job request form with validation."""
    department = StringField('Department', validators=[
        DataRequired(message='Department is required'),
        Length(min=2, max=100, message='Department must be 2-100 characters'),
        Regexp(r'^[a-zA-Z\s\-]+$', message='Department can only contain letters, spaces, and hyphens')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=10, max=2000, message='Description must be 10-2000 characters')
    ])
    category = SelectField('Category', choices=[
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('mechanical', 'Mechanical'),
        ('civil', 'Civil'),
        ('carpentry', 'Carpentry'),
        ('general', 'General'),
        ('hvac', 'HVAC'),
        ('painting', 'Painting')
    ], validators=[DataRequired(message='Category is required')])
    priority = SelectField('Priority', choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ], validators=[DataRequired(message='Priority is required')])
    
    def validate_description(self, field):
        """Custom description validation."""
        description = field.data
        
        # Check for potentially malicious content
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                raise ValidationError('Description contains potentially unsafe content')


class AssignmentForm(FlaskForm):
    """Assignment form with validation."""
    job_id = IntegerField('Job ID', validators=[
        DataRequired(message='Job ID is required'),
        NumberRange(min=1, message='Job ID must be a positive number')
    ])
    worker_id = IntegerField('Worker ID', validators=[
        DataRequired(message='Worker ID is required'),
        NumberRange(min=1, message='Worker ID must be a positive number')
    ])


class WorkerForm(FlaskForm):
    """Worker form with validation."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=3, max=150, message='Full name must be 3-150 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Full name can only contain letters, spaces, hyphens, and periods')
    ])
    department = StringField('Department', validators=[
        DataRequired(message='Department is required'),
        Length(min=2, max=100, message='Department must be 2-100 characters'),
        Regexp(r'^[a-zA-Z\s\-]+$', message='Department can only contain letters, spaces, and hyphens')
    ])
    skill_category = SelectField('Skill Category', choices=[
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('carpentry', 'Carpentry'),
        ('mechanical', 'Mechanical'),
        ('civil', 'Civil'),
        ('general', 'General')
    ], validators=[DataRequired(message='Skill category is required')])
    is_active = BooleanField('Active', default=True)


class MaterialForm(FlaskForm):
    """Material form with validation."""
    item_name = StringField('Item Name', validators=[
        DataRequired(message='Item name is required'),
        Length(min=2, max=150, message='Item name must be 2-150 characters'),
        Regexp(r'^[a-zA-Z0-9\s\-\.\,]+$', message='Item name can only contain letters, numbers, spaces, and basic punctuation')
    ])
    unit = StringField('Unit', validators=[
        DataRequired(message='Unit is required'),
        Length(min=1, max=30, message='Unit must be 1-30 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Unit can only contain letters and spaces')
    ])
    quantity_required = FloatField('Quantity Required', validators=[
        DataRequired(message='Quantity required is required'),
        NumberRange(min=0.01, message='Quantity must be greater than 0')
    ])
    quantity_used = FloatField('Quantity Used', validators=[
        NumberRange(min=0, message='Quantity used cannot be negative')
    ])
    
    def validate_quantity_used(self, field):
        """Validate that quantity used doesn't exceed quantity required."""
        if field.data and self.quantity_required.data:
            if field.data > self.quantity_required.data:
                raise ValidationError('Quantity used cannot exceed quantity required')


class SearchForm(FlaskForm):
    """Search form with validation."""
    keyword = StringField('Search', validators=[
        Optional(),
        Length(min=2, max=100, message='Search term must be 2-100 characters'),
        Regexp(r'^[a-zA-Z0-9\s\-\.]+$', message='Search term can only contain letters, numbers, spaces, hyphens, and periods')
    ])
    status = SelectField('Status', choices=[
        ('', 'All'),
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ], validators=[Optional()])
    department = StringField('Department', validators=[
        Optional(),
        Length(max=100, message='Department must be less than 100 characters')
    ])
    priority = SelectField('Priority', choices=[
        ('', 'All'),
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ], validators=[Optional()])


class UserManagementForm(FlaskForm):
    """User management form for admins."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=100, message='Email must be less than 100 characters'),
        Regexp(r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$', 
               message='Must be a valid MSU staff email (username@staff.msu.ac.zw)')
    ])
    role = SelectField('Role', choices=[
        ('staff', 'Staff'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
        ('maintenance_admin', 'Maintenance Admin')
    ], validators=[DataRequired(message='Role is required')])
    is_active = BooleanField('Active', default=True)
