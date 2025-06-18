#!/usr/bin/env python3
"""
Mock API for local development without database
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
import uvicorn

app = FastAPI(title="Mock Version Management API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_APPS = [
    {
        "id": 1,
        "name": "nexa-timesheet",
        "package_name": "com.nexa.timesheet",
        "description": "Nexa Timesheet Mobile App",
        "created_at": "2024-01-15T10:00:00"
    }
]

MOCK_VERSIONS = [
    {
        "id": 1,
        "app_id": 1,
        "version": "0.6.1",
        "version_code": 3,
        "platform": "android",
        "file_size": 45000000,
        "changelog": {"en": ["Bug fixes", "Performance improvements"]},
        "is_mandatory": False,
        "download_count": 42,
        "created_at": "2024-01-15T10:00:00"
    }
]

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "mock",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v2/apps")
async def list_apps(x_api_key: Optional[str] = Header(None)):
    if x_api_key != "nexa_internal_app_key_2025":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return MOCK_APPS

@app.get("/api/v2/apps/{app_id}/versions")
async def list_versions(app_id: int, x_api_key: Optional[str] = Header(None)):
    if x_api_key != "nexa_internal_app_key_2025":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return [v for v in MOCK_VERSIONS if v["app_id"] == app_id]

@app.get("/api/v2/version/check")
async def check_version(app_name: str, platform: str, current_version: str):
    return {
        "update_available": current_version != "0.6.1",
        "latest_version": "0.6.1",
        "is_mandatory": False,
        "changelog": {"en": ["Bug fixes", "Performance improvements"]},
        "download_url": f"/api/v2/download/{app_name}/{platform}/0.6.1"
    }

@app.get("/api/v2/analytics/{app_name}/overview")
async def analytics_overview(app_name: str):
    return {
        "total_users": 156,
        "active_sessions": 12,
        "total_downloads": 423,
        "versions": {
            "0.6.1": {"users": 120, "percentage": 77},
            "0.6.0": {"users": 36, "percentage": 23}
        }
    }

if __name__ == "__main__":
    print("🚀 Starting MOCK API (no database required)")
    print("📌 Use this for development when Railway is down")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)