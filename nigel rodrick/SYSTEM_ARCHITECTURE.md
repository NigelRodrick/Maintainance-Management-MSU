# MSU Maintenance System - System Architecture

## Architecture Overview

The MSU Maintenance Management System is designed using a modern, scalable, and maintainable architecture that follows industry best practices for enterprise web applications. The system employs a layered architecture approach with clear separation of concerns, enabling independent development, testing, and deployment of components.

## Architectural Principles

### Core Design Principles
1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Modularity**: Components are loosely coupled and highly cohesive
3. **Scalability**: Architecture supports horizontal and vertical scaling
4. **Security**: Security is built into every layer
5. **Maintainability**: Clean code structure and comprehensive documentation
6. **Testability**: All components are designed for automated testing
7. **Performance**: Optimized for high-volume transaction processing

### Architectural Patterns
- **Layered Architecture**: Clear separation between presentation, business, and data layers
- **Repository Pattern**: Data access abstraction for testability and maintainability
- **Service Layer Pattern**: Business logic encapsulation and reuse
- **Dependency Injection**: Loose coupling and improved testability
- **Factory Pattern**: Object creation and configuration management

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Web UI (HTML/CSS/JS)  │  REST API  │  Mobile App (Future)     │
├─────────────────────────────────────────────────────────────────┤
│                    Application Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Route Controllers  │  Authentication  │  Validation & Security  │
├─────────────────────────────────────────────────────────────────┤
│                     Business Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Service Classes  │  Business Logic  │  Rules Engine  │  Analytics │
├─────────────────────────────────────────────────────────────────┤
│                     Data Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  Repository Pattern  │  ORM (SQLAlchemy)  │  Database (SQL Server) │
├─────────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Caching (Redis)  │  Logging  │  Monitoring  │  File Storage      │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Architecture Layers

### 1. Presentation Layer

#### Web Interface
- **Technology Stack**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Template Engine**: Jinja2 (Flask templating)
- **UI Framework**: Bootstrap 5 with custom styling
- **Chart Library**: Chart.js for data visualization
- **Responsiveness**: Mobile-first responsive design

#### REST API
- **Framework**: Flask-RESTful principles
- **Data Format**: JSON for all API responses
- **Authentication**: JWT tokens for API access
- **Documentation**: Swagger/OpenAPI specification
- **Versioning**: URL-based versioning (/api/v1/)

#### Mobile Application (Future)
- **Technology**: React Native or Flutter
- **Offline Support**: Local data synchronization
- **Push Notifications**: Real-time updates
- **GPS Integration**: Location-based services

### 2. Application Layer

#### Route Controllers
```python
# Route Structure
app/
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main application routes
│   ├── admin.py          # Admin-specific routes
│   ├── supervisor.py     # Supervisor routes
│   ├── staff.py          # Staff routes
│   ├── analytics.py      # Analytics and reporting
│   └── api/              # REST API endpoints
│       ├── auth.py       # API authentication
│       ├── jobs.py       # Job management API
│       ├── users.py      # User management API
│       └── reports.py    # Reporting API
```

#### Authentication & Authorization
- **Authentication**: Flask-Login for session management
- **Authorization**: Role-based access control (RBAC)
- **Security**: CSRF protection, XSS prevention
- **Session Management**: Secure session handling with Redis

#### Input Validation & Security
- **Validation**: Flask-WTF for form validation
- **Sanitization**: Input cleaning and escaping
- **Rate Limiting**: Flask-Limiter for API protection
- **Security Headers**: Flask-Talisman for security headers

### 3. Business Layer

#### Service Classes Architecture
```python
# Service Layer Structure
app/
├── services/
│   ├── auth_service.py         # Authentication business logic
│   ├── job_service.py          # Job management logic
│   ├── assignment_service.py   # Worker assignment logic
│   ├── material_service.py     # Material management logic
│   ├── analytics_service.py    # Data analysis logic
│   ├── report_service.py       # Report generation logic
│   ├── notification_service.py # Notification management
│   └── classification_service.py # Request classification
```

#### Business Logic Components
- **Request Processing**: Automated classification and prioritization
- **Assignment Logic**: Worker recommendation algorithms
- **Material Management**: Inventory tracking and optimization
- **Analytics Engine**: Statistical analysis and reporting
- **Notification System**: Multi-channel communication

#### Rules Engine
- **Classification Rules**: Keyword-based categorization
- **Priority Rules**: Urgency assessment based on content
- **Assignment Rules**: Worker selection criteria
- **Escalation Rules**: Automatic escalation for overdue tasks

### 4. Data Layer

#### Repository Pattern Implementation
```python
# Repository Structure
app/
├── repositories/
│   ├── base_repository.py      # Base repository interface
│   ├── user_repository.py      # User data access
│   ├── job_repository.py       # Job request data access
│   ├── assignment_repository.py # Assignment data access
│   ├── material_repository.py  # Material data access
│   └── analytics_repository.py # Analytics data access
```

#### Object-Relational Mapping (ORM)
- **Framework**: SQLAlchemy 3.0.5
- **Models**: Declarative model definitions
- **Relationships**: Proper foreign key relationships
- **Migrations**: Automatic schema migration system
- **Query Optimization**: Efficient query generation

#### Database Design
```sql
-- Core Tables
Users                 -- User authentication and roles
JobRequests          -- Maintenance requests
Assignments          -- Worker assignments
Materials            -- Material tracking
Categories           -- Maintenance categories
Priorities           -- Priority levels
Departments          -- University departments
Workers              -- Maintenance workers
Notifications        -- System notifications
AuditLog            -- System audit trail
```

### 5. Infrastructure Layer

#### Caching Strategy
- **Application Cache**: Redis for session storage and caching
- **Query Cache**: SQLAlchemy query result caching
- **Static Cache**: Browser caching for static assets
- **CDN Integration**: Content delivery network for static files

#### Logging System
- **Application Logging**: Structured logging with Python logging
- **Security Logging**: Authentication and authorization events
- **Audit Logging**: All data modifications tracked
- **Performance Logging**: Response time and resource usage

#### Monitoring & Health Checks
- **Application Health**: Custom health check endpoints
- **Database Health**: Connection and query performance monitoring
- **System Metrics**: CPU, memory, and disk usage tracking
- **Error Tracking**: Comprehensive error reporting and alerting

## Component Architecture

### Authentication Component
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │───▶│ Auth Controller │───▶│  Auth Service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Session Store  │    │ User Repository │
                       │     (Redis)     │    │   (Database)    │
                       └─────────────────┘    └─────────────────┘
```

### Job Management Component
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Form UI   │───▶│ Job Controller  │───▶│  Job Service    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
│ Classification   │    │ Job Repository │
│     Service      │    │   (Database)    │
└─────────────────┘    └─────────────────┘
```

### Analytics Component
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Dashboard UI    │───▶│Analytics Ctrl   │───▶│Analytics Service│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
│  Data Processing  │    │ Analytics Repo  │
│     Engine       │    │   (Database)    │
└─────────────────┘    └─────────────────┘
```

## Data Flow Architecture

### Request Processing Flow
```
1. User Request
   ↓
2. Route Controller
   ↓
3. Input Validation
   ↓
4. Authentication/Authorization
   ↓
5. Business Logic (Service Layer)
   ↓
6. Data Access (Repository Layer)
   ↓
7. Database Operations
   ↓
8. Response Processing
   ↓
9. UI Update/API Response
```

### Data Persistence Flow
```
1. Business Logic Request
   ↓
2. Repository Method Call
   ↓
3. ORM Query Generation
   ↓
4. Database Transaction
   ↓
5. Transaction Commit/Rollback
   ↓
6. Cache Update (if needed)
   ↓
7. Event Logging
   ↓
8. Response to Service Layer
```

## Security Architecture

### Authentication Flow
```
1. User Login Request
   ↓
2. Credential Validation
   ↓
3. Role Assignment
   ↓
4. Session Creation
   ↓
5. Security Context Setup
   ↓
6. Access Granted/Denied
```

### Authorization Model
```python
# Role-Based Access Control
ROLES = {
    'admin': ['all'],
    'supervisor': ['jobs', 'assignments', 'reports'],
    'staff': ['requests', 'status'],
    'worker': ['assigned_jobs', 'materials']
}

# Permission Matrix
PERMISSIONS = {
    'create': ['admin', 'supervisor', 'staff'],
    'read': ['admin', 'supervisor', 'staff', 'worker'],
    'update': ['admin', 'supervisor', 'worker'],
    'delete': ['admin']
}
```

## Deployment Architecture

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │───▶│   Web Servers   │───▶│  Database Server│
│   (Nginx)       │    │   (Flask App)   │    │  (SQL Server)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
│   Redis Cache    │    │   File Storage  │
│   (Sessions)     │    │   (Reports)     │
└─────────────────┘    └─────────────────┘
```

### High Availability Setup
```
┌─────────────────┐    ┌─────────────────┐
│   Primary DB    │◄──▶│   Secondary DB  │
│   (Master)      │    │   (Replica)     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   App Server 1  │    │   App Server 2  │
│   (Active)      │    │   (Standby)     │
└─────────────────┘    └─────────────────┘
```

## Integration Architecture

### External System Integration
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  University AD  │───▶│  Auth Service   │───▶│  Application    │
│  (LDAP/SSO)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Email Service  │───▶│ Notification    │───▶│  Application    │
│  (SMTP)         │    │ Service         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ERP System     │───▶│  Integration    │───▶│  Application    │
│  (Financial)    │    │ Service         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Performance Architecture

### Caching Strategy
```
┌─────────────────┐    ┌─────────────────┐
│  Application    │───▶│  Redis Cache    │
│  Cache Layer    │    │  (L1 Cache)     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Database       │───▶│  Query Cache    │
│  Query Cache    │    │  (L2 Cache)     │
└─────────────────┘    └─────────────────┘
```

### Load Balancing
```
┌─────────────────┐
│   Load Balancer │
│   (Round Robin) │
└─────────────────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
┌─────┐┌─────┐┌─────┐
│App 1││App 2││App 3│
└─────┘└─────┘└─────┘
```

## Scalability Architecture

### Horizontal Scaling
- **Web Servers**: Multiple application servers behind load balancer
- **Database**: Read replicas for read-heavy operations
- **Cache**: Redis cluster for distributed caching
- **File Storage**: Distributed file system for reports and attachments

### Vertical Scaling
- **CPU Scaling**: Multi-core processor utilization
- **Memory Scaling**: Increased RAM for caching and session storage
- **Storage Scaling**: SSD storage for improved I/O performance
- **Network Scaling**: Increased bandwidth for concurrent users

## Monitoring Architecture

### Application Monitoring
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Application    │───▶│  Metrics        │───▶│  Monitoring     │
│  Metrics        │    │  Collection     │    │  Dashboard      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Error Logs     │───▶│  Log Aggregation│───▶│  Alert System   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Health Checks  │───▶│  Status         │───▶│  Uptime Monitor │
└─────────────────┘    │  Monitoring     │    └─────────────────┘
                       └─────────────────┘
```

## Future Architecture Enhancements

### Microservices Migration
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │  Job Service    │    │  Analytics Svc  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                       ┌─────────────────┐
                       │  API Gateway    │
                       └─────────────────┘
```

### Event-Driven Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Event Producer │───▶│  Message Queue  │───▶│  Event Consumer │
└─────────────────┘    │   (RabbitMQ)    │    └─────────────────┘
                       └─────────────────┘
```

---

**Architecture Version**: 1.0  
**Last Updated**: 2026-04-05  
**Status**: Production-Ready  
**Review Cycle**: Quarterly
