# Database Setup Guide

## Quick Reference

### Database Credentials (Default)

| Parameter | Value |
|-----------|-------|
| **User** | `interview_user` |
| **Password** | `interview_password` |
| **Database** | `interview_db` |
| **Port** | `5432` |

---

## Option 1: Docker Compose (Easiest)

### Setup
```bash
# 1. Copy environment file
cp .env.example .env

# 2. (Optional) Edit .env to change credentials
# Default credentials are already set in .env.example

# 3. Start services
docker-compose up -d
```

### Connection Details
- **Host from Backend**: `db` (Docker service name)
- **Host from Local Machine**: `localhost`
- **DATABASE_URL**: `postgresql://interview_user:interview_password@db:5432/interview_db`

The database is automatically created and ready to use!

---

## Option 2: Local PostgreSQL

### 1. Install PostgreSQL

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# In psql, run:
CREATE DATABASE interview_db;
CREATE USER interview_user WITH PASSWORD 'interview_password';
GRANT ALL PRIVILEGES ON DATABASE interview_db TO interview_user;

# Grant schema privileges (PostgreSQL 15+)
\c interview_db
GRANT ALL ON SCHEMA public TO interview_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO interview_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO interview_user;

# Exit psql
\q
```

### 3. Update Backend .env

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://interview_user:interview_password@localhost:5432/interview_db
```

### 4. Initialize Database Tables

```bash
cd backend
python -c "from database import init_db; init_db()"
# Or just start the app - tables are created automatically:
python app.py
```

---

## Testing Database Connection

### From Python
```python
# Test connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://interview_user:interview_password@localhost:5432/interview_db')
print('✓ Connection successful!')
conn.close()
"
```

### From Command Line
```bash
# PostgreSQL CLI
psql -U interview_user -d interview_db -h localhost

# In psql:
\dt        # List tables
\du        # List users
\l         # List databases
\q         # Quit
```

### From Docker
```bash
# Connect to database container
docker-compose exec db psql -U interview_user -d interview_db

# Run SQL query
docker-compose exec db psql -U interview_user -d interview_db -c "SELECT 1;"
```

---

## Environment Variables Summary

### Root .env (for docker-compose)
```env
# PostgreSQL Container
POSTGRES_USER=interview_user
POSTGRES_PASSWORD=interview_password
POSTGRES_DB=interview_db

# Backend Connection (use 'db' for Docker)
DATABASE_URL=postgresql://interview_user:interview_password@db:5432/interview_db
```

### backend/.env (for local development)
```env
# Backend Connection (use 'localhost' for local)
DATABASE_URL=postgresql://interview_user:interview_password@localhost:5432/interview_db

SECRET_KEY=your-secret-key-here
```

### backend/.env.test (for testing)
```env
# Test Database (separate from development)
DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_interview_db

SECRET_KEY=test_secret_key_for_testing_only
```

---

## Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
# Docker:
docker-compose ps

# Local:
# Windows:
Get-Service postgresql*
# macOS:
brew services list
# Linux:
sudo systemctl status postgresql
```

### Authentication Failed
```bash
# Verify credentials in .env match database user
# Reset password if needed:
psql -U postgres
ALTER USER interview_user WITH PASSWORD 'interview_password';
```

### Database Does Not Exist
```bash
# Create database:
psql -U postgres -c "CREATE DATABASE interview_db;"

# Or use docker:
docker-compose exec db psql -U postgres -c "CREATE DATABASE interview_db;"
```

### Permission Denied
```bash
# Grant permissions:
psql -U postgres -d interview_db
GRANT ALL ON SCHEMA public TO interview_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO interview_user;
```

### Port Already in Use
```bash
# Check what's using port 5432:
# Windows:
netstat -ano | findstr :5432
# macOS/Linux:
lsof -i :5432

# Change port in docker-compose.yml:
ports:
  - "5433:5432"  # Host:Container
# Update DATABASE_URL accordingly
```

---

## Database Schema

Tables are created automatically on first startup by `database.init_db()`.

**Tables:**
- `users` - User accounts, authentication
- `user_stats` - User statistics, achievements, streaks
- `interview_history` - Completed interview records

See [backend/database.py](backend/database.py) for full schema.

---

## Production Considerations

1. **Strong Credentials**: Change default passwords
2. **SSL/TLS**: Enable encrypted connections
3. **Backups**: Set up automated backups
4. **Monitoring**: Use pg_stat_statements, pgBadger
5. **Connection Pooling**: Consider PgBouncer for high traffic
6. **Managed Services**: Use AWS RDS, Azure PostgreSQL, or similar

### Backup Database
```bash
# Backup
pg_dump -U interview_user -d interview_db -F c -f backup.dump

# Restore
pg_restore -U interview_user -d interview_db backup.dump
```

### Docker Backup
```bash
# Backup
docker-compose exec db pg_dump -U interview_user interview_db > backup.sql

# Restore
docker-compose exec -T db psql -U interview_user interview_db < backup.sql
```
