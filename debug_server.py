"""
Server di debug per capire il problema
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Debug API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Debug API is working"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "debug"}

@app.get("/test")
def test():
    return {"test": "endpoint working"}

if __name__ == "__main__":
    print("🔧 Starting debug server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")