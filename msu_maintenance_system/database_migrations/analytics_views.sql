-- Analytics Views for MSU Maintenance System
-- These views provide read-only data for analytics without affecting transaction tables

-- View 1: Department Summary
CREATE OR ALTER VIEW vw_department_summary AS
SELECT 
    d.id as department_id,
    d.name as department_name,
    COUNT(jr.id) as total_jobs,
    AVG(DATEDIFF(hour, jr.created_at, jr.completed_at)) as avg_resolution_time,
    SUM(CASE WHEN jr.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(jr.id) as completion_rate,
    COUNT(DISTINCT jr.assigned_to) as unique_technicians,
    SUM(CASE WHEN jr.priority = 'urgent' THEN 1 ELSE 0 END) as urgent_jobs
FROM departments d
LEFT JOIN job_requests jr ON d.id = jr.department_id
GROUP BY d.id, d.name;

-- View 2: Worker Performance
CREATE OR ALTER VIEW vw_worker_performance AS
SELECT 
    u.id as worker_id,
    u.full_name as worker_name,
    COUNT(jr.id) as jobs_completed,
    AVG(DATEDIFF(hour, jr.created_at, jr.completed_at)) as avg_resolution_time,
    COUNT(DASE WHEN jr.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(jr.id) as efficiency_score,
    COUNT(DISTINCT jr.category_id) as skill_variety,
    u.skill_level,
    u.department_id
FROM users u
LEFT JOIN job_requests jr ON u.id = jr.assigned_to AND jr.status = 'completed'
GROUP BY u.id, u.full_name, u.skill_level, u.department_id;

-- View 3: Job Trends
CREATE OR ALTER VIEW vw_job_trends AS
SELECT 
    jr.id,
    jr.title,
    jr.category_id,
    c.name as category_name,
    jr.priority,
    jr.status,
    jr.created_date,
    jr.completed_at,
    jr.department_id,
    d.name as department_name,
    DATEDIFF(day, jr.created_date, jr.completed_at) as resolution_days
FROM job_requests jr
JOIN categories c ON jr.category_id = c.id
JOIN departments d ON jr.department_id = d.id;

-- View 4: Material Usage
CREATE OR ALTER VIEW vw_material_usage AS
SELECT 
    m.id as material_id,
    m.name as material_name,
    m.category,
    COUNT(jm.job_id) as usage_count,
    SUM(jm.quantity) as total_quantity,
    SUM(jm.quantity * m.unit_cost) as total_cost,
    AVG(jm.quantity * m.unit_cost) as cost_per_job
FROM materials m
LEFT JOIN job_materials jm ON m.id = jm.material_id
GROUP BY m.id, m.name, m.category;

-- View 5: SLA Compliance
CREATE OR ALTER VIEW vw_sla_compliance AS
SELECT 
    jr.id as job_id,
    jr.priority,
    jr.created_date,
    jr.completed_at,
    DATEDIFF(hour, jr.created_date, jr.completed_at) as resolution_hours,
    CASE 
        WHEN jr.priority = 'urgent' AND DATEDIFF(hour, jr.created_date, jr.completed_at) <= 4 THEN 1
        WHEN jr.priority = 'high' AND DATEDIFF(hour, jr.created_date, jr.completed_at) <= 8 THEN 1
        WHEN jr.priority = 'medium' AND DATEDIFF(hour, jr.created_date, jr.completed_at) <= 24 THEN 1
        WHEN jr.priority = 'low' AND DATEDIFF(hour, jr.created_date, jr.completed_at) <= 72 THEN 1
        ELSE 0
    END as within_sla,
    CASE 
        WHEN jr.priority = 'urgent' AND DATEDIFF(hour, jr.created_date, jr.completed_at) > 4 THEN DATEDIFF(hour, jr.created_date, jr.completed_at) - 4
        WHEN jr.priority = 'high' AND DATEDIFF(hour, jr.created_date, jr.completed_at) > 8 THEN DATEDIFF(hour, jr.created_date, jr.completed_at) - 8
        WHEN jr.priority = 'medium' AND DATEDIFF(hour, jr.created_date, jr.completed_at) > 24 THEN DATEDIFF(hour, jr.created_date, jr.completed_at) - 24
        WHEN jr.priority = 'low' AND DATEDIFF(hour, jr.created_date, jr.completed_at) > 72 THEN DATEDIFF(hour, jr.created_date, jr.completed_at) - 72
        ELSE 0
    END as breach_duration
FROM job_requests jr
WHERE jr.status = 'completed';
