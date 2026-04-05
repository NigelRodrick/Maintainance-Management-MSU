# Job Progress Tracker Documentation

## Overview

The Job Progress Tracker is a comprehensive system for managing maintenance job status lifecycle within the MSU Maintenance Management System. It provides real-time status tracking, audit logging, and role-based permissions for job status updates.

## 🎯 Features

### Status Lifecycle
- **PENDING**: Initial status when job is created
- **IN_PROGRESS**: Job is being worked on
- **COMPLETED**: Job has been finished

### Key Capabilities
- ✅ Role-based status updates (supervisor/admin only)
- ✅ Status transition validation
- ✅ Comprehensive audit logging
- ✅ Real-time status tracking
- ✅ RESTful API endpoints
- ✅ Database integrity constraints

## 🏗️ Architecture

### Database Schema

#### Updated JobRequests Table
```sql
CREATE TABLE JobRequests (
    id INT PRIMARY KEY IDENTITY,
    department VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(50),
    status VARCHAR(20) DEFAULT 'PENDING',  -- Updated
    date_created DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()  -- New column
);
```

#### JobStatusAudit Table (New)
```sql
CREATE TABLE JobStatusAudit (
    id INT PRIMARY KEY IDENTITY,
    job_id INT NOT NULL,
    old_status VARCHAR(20) NULL,
    new_status VARCHAR(20) NOT NULL,
    updated_by INT NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
    notes VARCHAR(500) NULL,
    
    FOREIGN KEY (job_id) REFERENCES JobRequests(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES Users(id)
);
```

### Service Layer Architecture

```
JobStatusService
├── update_job_status()           # Core update logic
├── get_job_status_history()      # Audit trail
├── get_jobs_by_status()          # Filter by status
├── get_status_summary()          # Statistics
├── can_user_update_job_status()  # Permission check
└── get_user_permission_level()    # Role checking
```

## 🔧 Implementation Details

### 1. Status Constants and Validation

```python
class JobStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class JobStatusTransition:
    VALID_TRANSITIONS = {
        JobStatus.PENDING: [JobStatus.IN_PROGRESS],
        JobStatus.IN_PROGRESS: [JobStatus.COMPLETED],
        JobStatus.COMPLETED: []  # Terminal state
    }
    
    # Override transitions for supervisors/admins
    OVERRIDE_TRANSITIONS = {
        JobStatus.PENDING: [JobStatus.IN_PROGRESS, JobStatus.COMPLETED],
        JobStatus.IN_PROGRESS: [JobStatus.PENDING, JobStatus.COMPLETED],
        JobStatus.COMPLETED: [JobStatus.PENDING, JobStatus.IN_PROGRESS]
    }
```

### 2. Business Rules

#### Standard User Transitions
- PENDING → IN_PROGRESS
- IN_PROGRESS → COMPLETED

#### Supervisor/Admin Override Transitions
- PENDING → IN_PROGRESS or COMPLETED
- IN_PROGRESS → PENDING or COMPLETED
- COMPLETED → PENDING or IN_PROGRESS (reopen jobs)

#### Permission Levels
- **Standard Users**: Cannot update status
- **Supervisors**: Standard transitions + override
- **Administrators**: Full override capabilities

### 3. Core Service Method

```python
def update_job_status(self, job_id: int, new_status: str, updated_by: int, 
                     is_override: bool = False) -> Dict[str, Any]:
    """
    Update job status with validation and logging.
    
    Args:
        job_id: ID of the job to update
        new_status: New status value
        updated_by: ID of the user making the update
        is_override: Whether to allow override transitions
        
    Returns:
        Dictionary with update result
        
    Raises:
        ValueError: If validation fails
        RuntimeError: If database operation fails
    """
```

## 🌐 API Endpoints

### PUT /jobs/{job_id}/status
Update job status

**Request:**
```json
{
  "status": "IN_PROGRESS"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Job status updated successfully",
  "job_id": 1,
  "old_status": "PENDING",
  "new_status": "IN_PROGRESS",
  "updated_at": "2024-03-29T13:30:00"
}
```

### GET /jobs/{job_id}/status
Get job status and history

**Response:**
```json
{
  "success": true,
  "job_id": 1,
  "current_status": "IN_PROGRESS",
  "status_history": [
    {
      "old_status": null,
      "new_status": "PENDING",
      "updated_by": null,
      "timestamp": "2024-03-29T10:00:00"
    },
    {
      "old_status": "PENDING",
      "new_status": "IN_PROGRESS",
      "updated_by": 123,
      "timestamp": "2024-03-29T13:30:00"
    }
  ]
}
```

### GET /jobs/status/summary
Get status summary

**Response:**
```json
{
  "success": true,
  "summary": {
    "PENDING": 15,
    "IN_PROGRESS": 8,
    "COMPLETED": 42
  },
  "total_jobs": 65
}
```

## 🎨 Frontend Integration

### Status Display with Colors and Icons

```html
<span class="status-badge" 
      style="background-color: #ffc107; color: white;">
    ⏳ Pending
</span>
```

### Status Update Dropdown

```html
<form method="POST" action="/update-status/{{ job.id }}">
    <select name="status">
        <option value="PENDING" selected>⏳ Pending</option>
        <option value="IN_PROGRESS">⚡ In Progress</option>
        <option value="COMPLETED">✅ Completed</option>
    </select>
    <button type="submit">🔄 Update</button>
</form>
```

## 📊 Database Migration

Run the migration script to update the database:

```bash
# Using SQL Server Management Studio
sqlcmd -S your_server -d CentralServices_AM_DB -i database_migrations/add_job_status_tracking.sql
```

### Migration Features
1. ✅ Adds `updated_at` column to JobRequests
2. ✅ Creates JobStatusAudit table
3. ✅ Adds status validation constraints
4. ✅ Standardizes existing status values
5. ✅ Creates automatic timestamp trigger
6. ✅ Adds indexes for performance
7. ✅ Creates stored procedures
8. ✅ Creates summary views

## 🔐 Security Considerations

### Authentication & Authorization
- Only authenticated users can access endpoints
- Role-based access control (RBAC)
- Supervisor/admin role validation

### Data Integrity
- Database constraints prevent invalid status values
- Atomic transactions prevent partial updates
- Audit trail tracks all changes

### Input Validation
- Status value validation against allowed values
- Job ID existence verification
- User permission checking

## 📝 Logging and Audit

### Application Logging
```python
logger.info(f"Job {job_id} status updated from {current_status} to {new_status} by user {updated_by}")
```

### Database Audit Trail
Every status change is logged in JobStatusAudit table:
- job_id
- old_status
- new_status
- updated_by
- timestamp
- notes (optional)

## 🚀 Usage Examples

### Python Service Usage

```python
from app.services.job_status_service import job_status_service

# Update job status
result = job_status_service.update_job_status(
    job_id=123,
    new_status="IN_PROGRESS",
    updated_by=456,
    is_override=True
)

if result['success']:
    print(f"Job {result['job_id']} updated to {result['new_status']}")
```

### Frontend JavaScript

```javascript
// Update job status via AJAX
async function updateJobStatus(jobId, newStatus) {
    try {
        const response = await fetch(`/jobs/${jobId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('Status updated successfully');
            location.reload();
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}
```

## 🧪 Testing

### Unit Tests
```python
def test_valid_status_transition():
    result = job_status_service.update_job_status(1, "IN_PROGRESS", 123)
    assert result['success'] == True
    assert result['new_status'] == "IN_PROGRESS"

def test_invalid_status_transition():
    with pytest.raises(ValueError):
        job_status_service.update_job_status(1, "PENDING", 123)  # Invalid transition
```

### Integration Tests
```python
def test_api_status_update():
    response = client.put('/jobs/1/status', 
                         json={'status': 'IN_PROGRESS'})
    assert response.status_code == 200
    assert response.json['success'] == True
```

## 📈 Performance Considerations

### Database Optimization
- Indexes on JobStatusAudit.job_id for fast lookups
- Index on timestamp for chronological queries
- Stored procedures for complex operations

### Caching
- Status summary can be cached for dashboard performance
- Job status history cached for frequently accessed jobs

## 🔧 Configuration

### Status Colors and Icons
```python
STATUS_COLORS = {
    'PENDING': '#ffc107',      # Yellow
    'IN_PROGRESS': '#17a2b8',  # Blue  
    'COMPLETED': '#28a745'     # Green
}

STATUS_ICONS = {
    'PENDING': '⏳',
    'IN_PROGRESS': '🔧',
    'COMPLETED': '✅'
}
```

## 🚨 Error Handling

### Common Error Scenarios
1. **Invalid Job ID**: "Job with ID {job_id} not found"
2. **Invalid Status**: "Invalid status value: {status}"
3. **Invalid Transition**: "Invalid status transition from {old} to {new}"
4. **Unauthorized**: "User not authorized to update job status"
5. **Database Error**: "Database error: {error_message}"

### Error Response Format
```json
{
  "success": false,
  "message": "Invalid status transition from PENDING to COMPLETED",
  "valid_transitions": ["IN_PROGRESS"]
}
```

## 📋 Monitoring and Maintenance

### Health Checks
- Monitor status update frequency
- Track failed status transitions
- Audit trail integrity checks

### Maintenance Tasks
- Archive old audit records
- Optimize database indexes
- Review status transition rules

## 🔮 Future Enhancements

### Planned Features
1. **Status SLA Tracking**: Time spent in each status
2. **Automatic Status Updates**: Based on completion dates
3. **Status Notifications**: Email/SMS alerts
4. **Bulk Status Updates**: For multiple jobs
5. **Status Workflows**: Custom approval chains
6. **Mobile App Support**: Native status updates

### API v2 Considerations
- GraphQL support for complex queries
- WebSocket real-time updates
- Advanced filtering and sorting

---

**MSU Central Services Amenities & Maintenance**  
*Job Progress Tracker Documentation*
