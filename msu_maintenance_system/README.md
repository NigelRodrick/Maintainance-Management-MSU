# MSU Maintenance Management System

A comprehensive, data-driven maintenance management system for Midlands State University that leverages machine learning, informatics principles, and enterprise-grade architecture to automate, optimize, and analyze institutional maintenance operations.

## 🎯 Academic Alignment

This system demonstrates:
- **Data Science**: ML classification, trend analysis, and predictive modeling
- **Informatics**: Decision-making support, process automation, and information flow
- **Systems Thinking**: End-to-end workflow management
- **Enterprise Context**: Real-world maintenance department operations

## 🚀 Key Features

### 🤖 Machine Learning
- **Automatic Classification**: Categorizes maintenance requests (plumbing, electrical, mechanical, civil)
- **Priority Prediction**: AI-powered priority assignment (Low/Medium/High)
- **Worker Recommendations**: Smart worker assignment based on historical performance

### 📊 Analytics & Insights
- **Trend Analysis**: Jobs per category and temporal patterns
- **Hotspot Detection**: Identify departments with highest maintenance issues
- **Performance Metrics**: Worker productivity and completion rates
- **Visual Dashboards**: Interactive charts and graphs

### 📋 Reporting
- **Excel Reports**: Multi-sheet comprehensive reports
- **Automated Generation**: One-click report creation
- **Data Export**: Jobs, assignments, materials, and summaries

### 🔐 Security
- **MSU Email Validation**: Enforces `xxxxxxxxxx@staff.msu.ac.zw` format
- **Password Hashing**: Secure credential storage
- **Session Management**: Protected routes and user sessions

## 🏗️ Architecture

```
msu_maintenance_system/
│
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/                  # Blueprint architecture
│   │   ├── auth.py             # Authentication routes
│   │   ├── main.py             # Core functionality
│   │   ├── analytics.py        # Analytics endpoints
│   │   └── reports.py          # Reporting system
│   ├── services/               # Business logic layer
│   │   ├── database.py         # Database abstraction
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── job_service.py      # Job management
│   │   ├── assignment_service.py # Worker assignments
│   │   ├── material_service.py # Material tracking
│   │   ├── analytics_service.py # Data analysis
│   │   └── report_service.py   # Report generation
│   ├── ml/                     # Machine learning layer
│   │   ├── prediction_service.py # Model inference
│   │   └── training_service.py  # Model training
│   ├── auth.py                 # Authentication decorators
│   └── utils.py                # Utility functions
│
├── config.py                   # Centralized configuration
├── run.py                      # Application entry point
├── train_models.py             # ML training script
├── requirements.txt             # Dependencies
│
├── data/                       # Training data
├── models/                     # Trained ML models
├── reports/                    # Generated reports
├── templates/                  # UI templates
└── static/                     # CSS and assets
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQL Server
- **ML**: Scikit-learn (TF-IDF + Logistic Regression)
- **Data Processing**: Pandas
- **Visualization**: Matplotlib
- **Reporting**: OpenPyXL
- **Security**: Werkzeug

## 📦 Installation

1. **Clone and Setup**
```bash
cd msu_maintenance_system
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
```sql
CREATE DATABASE CentralServices_AM_DB;
GO

USE CentralServices_AM_DB;

CREATE TABLE Users (
    id INT PRIMARY KEY IDENTITY,
    email VARCHAR(100),
    role VARCHAR(50),
    password VARCHAR(255)
);

CREATE TABLE JobRequests (
    id INT PRIMARY KEY IDENTITY,
    department VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Pending',
    date_created DATETIME DEFAULT GETDATE()
);

CREATE TABLE Assignments (
    id INT PRIMARY KEY IDENTITY,
    job_id INT,
    worker_name VARCHAR(100),
    start_time DATETIME,
    end_time DATETIME
);

CREATE TABLE Materials (
    id INT PRIMARY KEY IDENTITY,
    job_id INT,
    item VARCHAR(100),
    quantity_required INT,
    quantity_used INT
);
```

4. **Generate Training Data**
```bash
python generate_data.py
```

5. **Train ML Models**
```bash
python train_models.py
```

6. **Run Application**
```bash
python run.py
```

Access the system at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
SQL_SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS
SQL_DATABASE=CentralServices_AM_DB

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

### Database Connection
Update `config.py` with your SQL Server details:
```python
SQL_SERVER = 'your-server-name'
SQL_DATABASE = 'CentralServices_AM_DB'
```

## 📊 Usage Guide

### 1. Login
- Use MSU staff email: `xxxxxxxxxx@staff.msu.ac.zw`
- Default users can be created via registration

### 2. Submit Maintenance Requests
- Select department
- Describe the issue
- System auto-classifies and prioritizes

### 3. Job Management
- **Dashboard**: View all maintenance requests
- **Assign**: Allocate workers (with AI recommendations)
- **Track**: Monitor job status (Pending → In Progress → Completed)
- **Materials**: Record material usage per job

### 4. Analytics
- **Overview**: System-wide statistics
- **Performance**: Worker productivity metrics
- **Hotspots**: Department-wise issue analysis

### 5. Reports
- **Generate**: Create comprehensive Excel reports
- **Download**: Export reports with multiple sheets
- **Analyze**: Review summaries and trends

## 🤖 Machine Learning Pipeline

### Training Process
1. **Data Loading**: CSV with description, category, priority
2. **Preprocessing**: Text cleaning and validation
3. **Feature Extraction**: TF-IDF vectorization (max_features=1000)
4. **Model Training**: Logistic Regression with train/test split
5. **Evaluation**: Accuracy metrics and classification reports
6. **Persistence**: Models saved as `.pkl` files

### Inference Pipeline
1. **Input**: Job description text
2. **Vectorization**: Using trained TF-IDF vectorizer
3. **Prediction**: Category and priority classification
4. **Fallback**: Default values if models unavailable

## 📈 Analytics Features

### Trend Analysis
- Jobs per category distribution
- Temporal job patterns
- Department-wise breakdowns

### Performance Metrics
- Worker completion rates
- Average job duration
- Material usage patterns

### Hotspot Detection
- High-frequency problem areas
- Department issue clustering
- Resource optimization insights

## 🔐 Security Features

### Authentication
- MSU email format validation
- Secure password hashing
- Session-based authentication
- Protected route access

### Data Protection
- SQL injection prevention
- Input validation
- Error handling
- Secure file operations

## 📋 Report Structure

### Excel Reports contain:
1. **Jobs Sheet**: Complete maintenance request log
2. **Assignments Sheet**: Worker assignments and timelines
3. **Materials Sheet**: Material usage tracking
4. **Summary Sheet**: Aggregated statistics and insights

## 🔄 Workflow Process

```
Request Submission → ML Classification → Priority Assignment 
→ Supervisor Review → Worker Assignment → Job Execution 
→ Material Tracking → Completion → Analytics Update
```

## 🚀 Production Deployment

### Environment Setup
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret
```

### Database Considerations
- Use dedicated SQL Server instance
- Implement regular backups
- Monitor connection pooling
- Optimize query performance

### Security Best Practices
- Use environment variables for secrets
- Implement HTTPS
- Regular security updates
- Access logging

## 🎓 Educational Value

This system demonstrates:
- **Software Architecture**: Modular, scalable design
- **Data Science**: Real-world ML implementation
- **Database Design**: Enterprise schema design
- **Security**: Authentication and authorization
- **UI/UX**: Clean, functional interface design
- **Analytics**: Business intelligence concepts

## 🤝 Contributing

1. Follow the existing architecture patterns
2. Maintain clean code principles
3. Update documentation
4. Test thoroughly
5. Use meaningful commit messages

## 📞 Support

For technical issues or questions:
- Check the configuration settings
- Verify database connectivity
- Review ML model availability
- Consult the error logs

---

**MSU Central Services Amenities & Maintenance**  
*Data-Driven Maintenance Management System*
