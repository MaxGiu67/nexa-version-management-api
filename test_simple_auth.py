#!/usr/bin/env python3
"""
Test simple authentication integration
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import bcrypt

app = FastAPI()

# Simple models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

# Simple auth endpoint
@app.post("/api/v2/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Simple login endpoint for testing"""
    # Check hardcoded admin credentials
    if credentials.username == "admin" and credentials.password == "admin123":
        return LoginResponse(
            token="test-session-token-123",
            message="Login successful"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v2/auth/test")
async def test_auth():
    """Test endpoint"""
    return {"message": "Auth endpoints are working"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test auth API on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)