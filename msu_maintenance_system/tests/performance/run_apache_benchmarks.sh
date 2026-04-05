#!/bin/bash
echo "Running Apache Benchmarks"

ab -n 100 -c 10 -t application/json -p '{"email":"test@msu.ac.zw","password":"testpassword"}' http://localhost:5000/auth/login
ab -n 100 -c 10 http://localhost:5000/dashboard
ab -n 100 -c 10 http://localhost:5000/api/v1/jobs

echo "Apache benchmarks completed"
