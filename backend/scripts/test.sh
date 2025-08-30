#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=test psql -h "postgres" -U "test" -d "test_mahaguru" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml

# Exit with the test result
exit $?
