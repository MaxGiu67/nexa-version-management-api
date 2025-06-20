#!/usr/bin/env python3
"""
Railway startup script that ensures all modules are loaded correctly
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

logger.info(f"Python path: {sys.path}")
logger.info(f"Current directory: {current_dir}")

# Test imports before starting
try:
    import pymysql
    logger.info("✅ PyMySQL imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import PyMySQL: {e}")

try:
    import bcrypt
    logger.info("✅ bcrypt imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import bcrypt: {e}")

try:
    import pyotp
    logger.info("✅ pyotp imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import pyotp: {e}")

try:
    import email_validator
    logger.info("✅ email_validator imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import email_validator: {e}")

try:
    import auth_module
    logger.info("✅ auth_module imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import auth_module: {e}")

try:
    import auth_endpoints
    logger.info("✅ auth_endpoints imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import auth_endpoints: {e}")

# Now import and run the main app
try:
    import multi_app_api
    logger.info("✅ multi_app_api imported successfully")
    
    # Run uvicorn
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    # Railway sometimes sets PORT to MySQL port (3306)
    if port == 3306:
        logger.warning(f"PORT {port} is MySQL port, using 8080 instead")
        port = 8080
    
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "multi_app_api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
except Exception as e:
    logger.error(f"Failed to start application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)