# 🐍 Python API Implementation Guide

## Overview

This folder contains Python implementations for the version management API endpoints in both **FastAPI** and **Flask** frameworks.

## Available Implementations

### 1. FastAPI (Recommended) - `python-implementation.py`
- Modern async Python web framework
- Automatic API documentation (Swagger/OpenAPI)
- Built-in validation with Pydantic
- Better performance with async support
- Type hints support

### 2. Flask - `flask-implementation.py`
- Traditional Python web framework
- Simpler integration if backend already uses Flask
- JWT authentication with flask-jwt-extended
- Synchronous request handling

## Quick Start

### FastAPI Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure database:**
```python
# In python-implementation.py
DB_CONFIG = {
    'host': 'your_host',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database'
}
```

3. **Run the server:**
```bash
uvicorn python-implementation:app --reload --host 0.0.0.0 --port 8000
```

4. **Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Flask Setup

1. **Install Flask dependencies:**
```bash
pip install flask flask-jwt-extended flask-cors pymysql
```

2. **Configure:**
```python
# In flask-implementation.py
app.config['JWT_SECRET_KEY'] = 'your-production-secret'
DB_CONFIG = {
    'host': 'your_host',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database'
}
```

3. **Run the server:**
```bash
python flask-implementation.py
```

## API Endpoints

All endpoints follow the same structure as Node.js/PHP implementations:

### Public Endpoints
- `GET /api/v1/app-version/check` - Check for updates
- `GET /api/v1/app-version/latest` - Get latest version info

### Authenticated Endpoints
- `POST /api/v1/app-version/log-update` - Log user update

### Admin Endpoints
- `GET /api/v1/app-version/history` - Version history
- `GET /api/v1/app-version/stats` - Update statistics
- `POST /api/v1/app-version/version` - Create/update version

## Authentication

### FastAPI
```python
# Headers
Authorization: Bearer <jwt_token>
X-Tenant: NEXA
```

### Flask
```python
# Headers
Authorization: Bearer <jwt_token>
X-Tenant: NEXA
```

## Testing

### Test with curl:
```bash
# Check for updates
curl "http://localhost:8000/api/v1/app-version/check?current_version=1.0.0&platform=android"

# Log update (requires auth)
curl -X POST "http://localhost:8000/api/v1/app-version/log-update" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_version": "1.0.0",
    "to_version": "1.1.0",
    "platform": "android",
    "update_type": "manual"
  }'
```

### Unit tests:
```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

## Production Deployment

### FastAPI with Gunicorn
```bash
gunicorn python-implementation:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Flask with Gunicorn
```bash
gunicorn flask-implementation:app -w 4 --bind 0.0.0.0:5000
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# For FastAPI
CMD ["uvicorn", "python-implementation:app", "--host", "0.0.0.0", "--port", "8000"]

# For Flask
# CMD ["gunicorn", "flask-implementation:app", "-w", "4", "--bind", "0.0.0.0:5000"]
```

## Environment Variables

Create `.env` file:
```env
# Database
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

# JWT
JWT_SECRET_KEY=your-secret-key

# App
ENV=production
DEBUG=false
```

## Security Considerations

1. **JWT Token Validation**: Implement proper JWT validation
2. **SQL Injection**: Use parameterized queries (already implemented)
3. **Rate Limiting**: Add rate limiting for public endpoints
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS properly for your domain

## Integration with Existing Backend

### If using Django:
```python
# urls.py
from django.urls import path, include
from .views import check_for_updates, get_latest_version

urlpatterns = [
    path('api/v1/app-version/check', check_for_updates),
    path('api/v1/app-version/latest', get_latest_version),
    # ... other endpoints
]
```

### If using Pyramid:
```python
# __init__.py
config.add_route('check_updates', '/api/v1/app-version/check')
config.add_route('latest_version', '/api/v1/app-version/latest')
# ... other routes
```

## Monitoring

Add logging and monitoring:
```python
import logging
from prometheus_client import Counter, Histogram

# Metrics
update_checks = Counter('app_update_checks_total', 'Total update checks')
update_duration = Histogram('app_update_check_duration_seconds', 'Update check duration')

# Use in endpoints
@update_duration.time()
def check_for_updates():
    update_checks.inc()
    # ... rest of the code
```

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check DB_CONFIG settings
   - Verify database server is running
   - Check firewall rules

2. **JWT validation fails**
   - Verify JWT_SECRET_KEY matches backend
   - Check token expiration
   - Validate token format

3. **CORS errors**
   - Configure allowed origins
   - Check request headers

### Debug Mode

Enable debug logging:
```python
# FastAPI
import logging
logging.basicConfig(level=logging.DEBUG)

# Flask
app.config['DEBUG'] = True
```

## Performance Tips

1. **Connection Pooling**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'mysql+pymysql://user:pass@host/db',
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

2. **Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_latest_version_cached(platform):
    # ... implementation
```

3. **Async Database (FastAPI)**
```python
import aiomysql

async def get_db():
    async with aiomysql.create_pool(**DB_CONFIG) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                yield cursor
```

## Support

For issues or questions:
1. Check the logs
2. Verify database schema matches
3. Test with curl/Postman
4. Check JWT token validity