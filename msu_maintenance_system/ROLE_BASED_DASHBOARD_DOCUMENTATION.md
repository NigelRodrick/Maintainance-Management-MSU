# Role-Based Dashboard System Documentation

## Overview

The Role-Based Dashboard System implements strict access control with three distinct user roles, each having dedicated dashboards and specific capabilities. This ensures proper separation of concerns and security boundaries within the MSU Maintenance Management System.

## 🎯 Roles and Capabilities

### Role Hierarchy

```
ADMIN (Level 3)
├── Full system access
├── User management
├── System administration
└── All capabilities

SUPERVISOR (Level 2)  
├── Job management
├── Technician assignment
├── Report generation
└── Limited system access

USER (Level 1)
├── Job submission
├── Own job tracking
└── Basic access only
```

### Role Capabilities Matrix

| Capability | ADMIN | SUPERVISOR | USER |
|------------|---------|-------------|------|
| create_users | ✅ | ❌ | ❌ |
| view_users | ✅ | ❌ | ❌ |
| view_all_jobs | ✅ | ✅ | ❌ |
| assign_technicians | ✅ | ✅ | ❌ |
| update_job_status | ✅ | ✅ | ❌ |
| submit_jobs | ✅ | ✅ | ✅ |
| view_own_jobs | ✅ | ✅ | ✅ |
| system_overview | ✅ | ❌ | ❌ |
| export_reports | ✅ | ✅ | ❌ |
| view_analytics | ✅ | ✅ | ❌ |

## 🏗️ Architecture

### Directory Structure

```
app/
├── constants/
│   └── roles.py              # Role definitions and capabilities
├── decorators/
│   └── auth_decorators.py     # Authentication decorators
├── services/
│   ├── dashboard_service.py    # Dashboard data access
│   └── auth_service.py       # Authentication logic
├── routes/
│   ├── admin_routes.py        # Admin routes
│   ├── supervisor_routes.py   # Supervisor routes  
│   ├── user_routes.py         # User routes
│   └── auth.py               # Authentication routes
└── templates/
    ├── admin/                 # Admin templates
    ├── supervisor/            # Supervisor templates
    └── user/                  # User templates
```

### Database Schema

#### Updated Users Table
```sql
CREATE TABLE Users (
    id INT PRIMARY KEY IDENTITY,
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    password VARCHAR(255)
);

-- Role constraint
ALTER TABLE Users 
ADD CONSTRAINT CK_Users_role 
CHECK (role IN ('ADMIN', 'SUPERVISOR', 'USER'));
```

#### New Tables
```sql
-- User activity logging
CREATE TABLE UserActivityLog (
    id INT PRIMARY KEY IDENTITY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NULL,
    resource_id INT NULL,
    ip_address VARCHAR(45) NULL,
    timestamp DATETIME DEFAULT GETDATE()
);

-- Job tracking enhancement
ALTER TABLE JobRequests 
ADD submitted_by INT NULL;
```

## 🔐 Authentication & Authorization

### Role-Based Decorators

#### `@role_required(role)`
```python
@role_required("ADMIN")
def admin_dashboard():
    # Only ADMIN role can access
    return render_template('admin/dashboard.html')
```

#### `@capability_required(capability)`
```python
@capability_required("create_users")
def manage_users():
    # Only users with 'create_users' capability can access
    return render_template('admin/users.html')
```

#### Access Control Flow
1. **Authentication Check**: Verify user is logged in
2. **Role Validation**: Validate user role exists
3. **Permission Check**: Verify role can access resource
4. **Audit Logging**: Log access attempt
5. **Grant/Deny**: Allow access or return 403

### Login Redirection Logic

```python
def get_redirect_dashboard(user_role):
    dashboard_map = {
        'ADMIN': 'admin.dashboard',
        'SUPERVISOR': 'supervisor.dashboard', 
        'USER': 'user.dashboard'
    }
    return url_for(dashboard_map.get(user_role, 'user.dashboard'))
```

## 🌐 API Endpoints

### Admin Endpoints

| Method | Endpoint | Description | Protection |
|---------|-----------|-------------|------------|
| GET | `/admin/dashboard` | Admin dashboard | `@role_required("ADMIN")` |
| GET | `/admin/users` | User management | `@role_required("ADMIN")` |
| POST | `/admin/users/create` | Create user | `@role_required("ADMIN")` |
| DELETE | `/admin/users/{id}/delete` | Delete user | `@role_required("ADMIN")` |
| GET | `/admin/activity` | Activity logs | `@role_required("ADMIN")` |
| GET | `/admin/system` | System overview | `@role_required("ADMIN")` |
| GET | `/admin/api/metrics` | Real-time metrics | `@role_required("ADMIN")` |

### Supervisor Endpoints

| Method | Endpoint | Description | Protection |
|---------|-----------|-------------|------------|
| GET | `/supervisor/dashboard` | Supervisor dashboard | `@role_required("SUPERVISOR")` |
| GET | `/supervisor/jobs/{id}/assign` | Assign technician | `@role_required("SUPERVISOR")` |
| POST | `/supervisor/jobs/{id}/status` | Update job status | `@role_required("SUPERVISOR")` |
| GET | `/supervisor/jobs/{id}/predictions` | ML predictions | `@role_required("SUPERVISOR")` |
| GET | `/supervisor/reports` | Generate reports | `@role_required("SUPERVISOR")` |
| GET | `/supervisor/api/queue-metrics` | Queue metrics | `@role_required("SUPERVISOR")` |

### User Endpoints

| Method | Endpoint | Description | Protection |
|---------|-----------|-------------|------------|
| GET | `/user/dashboard` | User dashboard | `@any_authenticated_user` |
| POST | `/user/submit` | Submit job | `@any_authenticated_user` |
| GET | `/user/jobs/{id}` | View job details | `@any_authenticated_user` |
| GET | `/user/jobs/{id}/status` | Job status tracking | `@any_authenticated_user` |
| GET | `/user/history` | Job history | `@any_authenticated_user` |
| GET | `/user/profile` | User profile | `@any_authenticated_user` |
| GET | `/user/api/my-jobs` | User's jobs API | `@any_authenticated_user` |

## 🎨 Frontend Implementation

### Admin Dashboard Features

#### System Metrics Cards
- **Total Users**: Count of all system users
- **Total Jobs**: Overall job statistics
- **Completed Jobs**: Completion metrics
- **Role Distribution**: Users by role type

#### Management Actions
- **User Management**: Create, edit, delete users
- **Activity Logs**: View system audit trail
- **System Overview**: Health and performance metrics

#### Quick Actions
```html
<a href="{{ url_for('admin.manage_users') }}" class="btn btn-primary">
    <span>👥</span> Manage Users
</a>
<a href="{{ url_for('admin.activity_logs') }}" class="btn btn-secondary">
    <span>📋</span> Activity Logs
</a>
```

### Supervisor Dashboard Features

#### Job Queue Management
- **Tabbed Interface**: Pending, In Progress, Completed
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Quick Actions**: Assign technicians, update status

#### Job Assignment
- **Worker Selection**: Dropdown with recommendations
- **ML Predictions**: View AI-powered insights
- **Status Updates**: Direct status change forms

#### Queue Metrics
```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <h4>{{ queue_metrics.pending_count }}</h4>
        <p>Pending Jobs</p>
    </div>
</div>
```

### User Dashboard Features

#### Job Submission
- **Simple Form**: Department, description fields
- **ML Integration**: Automatic category/priority prediction
- **Confirmation**: Success/error feedback

#### Job Tracking
- **Status Indicators**: Visual status badges
- **Progress Timeline**: Status change history
- **Activity Summary**: Personal statistics

#### Status Display
```html
<span class="status-badge" style="background-color: {{ status_color }};">
    {{ status_icon }} {{ job.status }}
</span>
```

## 🤖 ML Integration (Supervisor Only)

### Prediction Display
When viewing a job, supervisors see:

```json
{
  "completion_time": {
    "prediction": "IN_PROGRESS",
    "confidence": 0.85
  },
  "urgency": {
    "prediction": "HIGH", 
    "confidence": 0.92
  },
  "team_type": {
    "prediction": "Electrician",
    "confidence": 0.88
  }
}
```

### Integration Points
- **No Model Retraining**: Uses existing trained models
- **Real-time Predictions**: Load-on-demand predictions
- **Confidence Scores**: Display prediction reliability
- **Fallback Logic**: Handle prediction failures gracefully

## 📊 Data Access Patterns

### Admin Data Access
```python
def get_admin_metrics():
    # Full system access
    return {
        'total_users': User.query.count(),
        'users_by_role': get_user_role_distribution(),
        'total_jobs': JobRequest.query.count(),
        'system_health': get_system_metrics()
    }
```

### Supervisor Data Access
```python
def get_supervisor_jobs():
    # All jobs, no user filtering
    return JobRequest.query.all()
```

### User Data Access
```python
def get_user_jobs(user_id):
    # Only user's own jobs
    return JobRequest.query.filter_by(submitted_by=user_id).all()
```

## 🔍 Security Implementation

### Access Control Validation

#### Role Validation
```python
def validate_role_access(target_role, user_role):
    try:
        user_role_enum = UserRole(user_role)
        target_role_enum = UserRole(target_role)
        return RoleHierarchy.is_higher_or_equal(user_role_enum, target_role_enum)
    except ValueError:
        return False
```

#### Capability Checking
```python
def check_capability(user_role, required_capability):
    return RoleCapabilities.has_capability(UserRole(user_role), required_capability)
```

### Audit Logging

#### Access Logging
```python
def log_access(user_id, action, resource_type, resource_id):
    query = """
        INSERT INTO UserActivityLog (user_id, action, resource_type, resource_id, timestamp)
        VALUES (?, ?, ?, ?, GETDATE())
    """
    db_service.execute_insert(query, (user_id, action, resource_type, resource_id))
```

#### Failed Access Attempts
```python
@log_access
def protected_route():
    # Automatically logs failed access attempts
    # Returns 403 for unauthorized access
```

## 📋 Business Rules

### Strict Separation
1. **No Dashboard Merging**: Each role has dedicated dashboard
2. **No Role Escalation**: Users cannot access higher role features
3. **No Cross-Role Data**: Users limited to own data
4. **Mandatory Authentication**: All routes require login
5. **Audit Trail**: All actions logged with user attribution

### Data Constraints
- **Role Validation**: Database constraints prevent invalid roles
- **Foreign Keys**: Maintain data integrity
- **Check Constraints**: Enforce business rules at DB level
- **Indexing**: Optimized for role-based queries

## 🧪 Testing

### Unit Tests
```python
def test_role_hierarchy():
    assert RoleHierarchy.is_higher_or_equal(UserRole.ADMIN, UserRole.USER)
    assert not RoleHierarchy.is_higher_or_equal(UserRole.USER, UserRole.ADMIN)

def test_capability_access():
    assert RoleCapabilities.has_capability(UserRole.ADMIN, 'create_users')
    assert not RoleCapabilities.has_capability(UserRole.USER, 'create_users')
```

### Integration Tests
```python
def test_dashboard_access():
    # Test admin dashboard access
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200
    
    # Test user accessing admin dashboard
    client.session['role'] = 'USER'
    response = client.get('/admin/dashboard')
    assert response.status_code == 403
```

### Security Tests
```python
def test_unauthorized_access():
    # Test access without authentication
    response = client.get('/admin/dashboard')
    assert response.status_code == 302  # Redirect to login
    
    # Test role manipulation
    client.session['role'] = 'ADMIN'  # Try to escalate
    response = client.get('/supervisor/dashboard')
    assert response.status_code == 403
```

## 🚀 Deployment Instructions

### 1. Database Migration
```bash
sqlcmd -S your_server -d CentralServices_AM_DB -i database_migrations/add_role_based_system.sql
```

### 2. Create Admin User
```sql
-- Insert default admin (change password immediately)
INSERT INTO Users (email, role, password) 
VALUES ('admin@msu.ac.zw', 'ADMIN', '$2b$12$secure_password_hash');
```

### 3. Test Role Access
1. **Admin Account**: Full system access
2. **Supervisor Account**: Job management only
3. **User Account**: Limited personal access

### 4. Verify Restrictions
- Users cannot access admin/supervisor dashboards
- Supervisors cannot access admin dashboard
- All role transitions properly enforced

## 📈 Monitoring

### Access Metrics
- Login attempts by role
- Dashboard access patterns
- Failed authorization attempts
- Feature usage by role

### Security Alerts
- Unauthorized access attempts
- Role escalation attempts
- Suspicious activity patterns
- Multiple failed logins

## 🔮 Future Enhancements

### Planned Features
1. **Role-Based API Rate Limiting**: Different limits per role
2. **Dynamic Permissions**: Runtime permission management
3. **Multi-Factor Authentication**: For admin roles
4. **Session Management**: Enhanced session security
5. **Advanced Audit Trail**: More detailed logging
6. **Role-Based Workflows**: Automated approval chains

### Scalability Considerations
- **Horizontal Scaling**: Multiple instances per role
- **Database Sharding**: Role-based data partitioning
- **Caching Strategy**: Role-specific cache layers
- **Load Balancing**: Role-based request distribution

---

**MSU Central Services Amenities & Maintenance**  
*Role-Based Dashboard System Documentation*
