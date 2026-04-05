
"""
SQL Injection Protection Guide and Fixes
====================================

IDENTIFIED VULNERABILITIES:
- Direct string formatting in SQL queries
- Unsafe parameter substitution
- Missing input validation

RECOMMENDED FIXES:

1. USE PARAMETERIZED QUERIES:
   ❌ BAD: f"SELECT * FROM users WHERE username = '{username}'"
   ✅ GOOD: text("SELECT * FROM users WHERE username = :username").params(username=username)

2. USE SQLALCHEMY ORM:
   ❌ BAD: db.session.execute(f"SELECT * FROM jobs WHERE status = '{status}'")
   ✅ GOOD: Job.query.filter_by(status=status).all()

3. VALIDATE INPUTS:
   ✅ GOOD: Validate and sanitize all user inputs before database operations

4. USE STORED PROCEDURES:
   ✅ GOOD: Use stored procedures for complex database operations

EXAMPLE FIXES:

Repository Pattern Fix:
----------------------
class UserRepository:
    def find_by_username(self, username: str) -> User:
        # ❌ BAD
        # query = f"SELECT * FROM users WHERE username = '{username}'"
        
        # ✅ GOOD
        query = text("SELECT * FROM users WHERE username = :username")
        result = db.session.execute(query, {'username': username})
        return result.fetchone()

Service Layer Fix:
------------------
class JobService:
    def get_jobs_by_status(self, status: str):
        # ❌ BAD
        # jobs = db.session.execute(f"SELECT * FROM jobs WHERE status = '{status}'")
        
        # ✅ GOOD
        jobs = Job.query.filter_by(status=status).all()
        return jobs

Input Validation Fix:
--------------------
def validate_status(status: str) -> bool:
    allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    return status in allowed_statuses
