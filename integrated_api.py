"""
Multi-App Version Management API with Authentication
Integrates the existing API with authentication and 2FA support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_app_api import app, DB_CONFIG
from auth_endpoints import router as auth_router
from auth_module import get_current_user, require_superadmin
from fastapi import Depends, HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Add database config to app state
app.state.db_config = DB_CONFIG

# Include authentication router
app.include_router(auth_router)

# Modify existing endpoints to require authentication for admin operations
# The following endpoints will require authentication:
# - POST /api/v2/apps (create app)
# - PUT /api/v2/apps/{app_identifier} (update app)
# - DELETE /api/v2/apps/{app_identifier} (delete app)
# - POST /api/v2/version/upload (upload version)
# - DELETE /api/v2/versions/{app}/{platform}/{version} (delete version)
# - GET /api/v2/analytics/* (view analytics - optional)

# Override specific endpoints with authentication
@app.post("/api/v2/apps/protected")
async def create_app_protected(
    app_data: dict,
    current_user = Depends(get_current_user)
):
    """Create a new app (requires authentication)"""
    # Call the original endpoint logic
    # This is a placeholder - in production, refactor the original endpoint
    return {"message": "App creation requires authentication", "user": current_user['username']}

# Add new admin dashboard endpoints
@app.get("/api/v2/admin/dashboard")
async def admin_dashboard(
    current_user = Depends(require_superadmin)
):
    """Get admin dashboard data (superadmin only)"""
    return {
        "total_apps": 0,  # Implement actual logic
        "total_versions": 0,
        "total_users": 0,
        "recent_activity": []
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Multi-App Version Management API with Authentication...")
    print("API Docs: http://localhost:8000/docs")
    print("\nDefault admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  Please change the password after first login!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
