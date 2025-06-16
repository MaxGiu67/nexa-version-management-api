# Correct Database Schema for Version Management API

## app_error_logs Table

The correct schema for `app_error_logs` table is:

```sql
CREATE TABLE app_error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    user_id INT,
    session_id INT,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT,
    metadata JSON,  -- Contains device_info, context, and other metadata
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
    app_version VARCHAR(20) NOT NULL,
    platform ENUM('android', 'ios', 'web') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL,
    INDEX idx_app_errors (app_id, created_at),
    INDEX idx_error_type (error_type, severity),
    INDEX idx_severity (severity),
    INDEX idx_session_errors (session_id),
    INDEX idx_user_errors (user_id),
    INDEX idx_version_platform (app_version, platform)
);
```

### Key Differences from Old Schema:
- **metadata** (JSON) - replaces device_info and context columns
- **session_id** (INT) - new column to link errors to sessions
- **No columns**: is_resolved, resolved_at, resolved_by, error_hash, error_count, etc.

## user_sessions Table

The correct schema for `user_sessions` table is:

```sql
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    app_id INT NOT NULL,
    session_uuid VARCHAR(255) NOT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    duration_seconds INT,
    app_version VARCHAR(20) NOT NULL,
    platform ENUM('android', 'ios', 'web') NOT NULL,
    device_info JSON,
    ip_address VARCHAR(45),
    end_reason VARCHAR(50),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    INDEX idx_user_sessions (user_id, start_time),
    INDEX idx_app_sessions (app_id, start_time),
    INDEX idx_session_dates (start_time, end_time),
    INDEX idx_platform_version (platform, app_version),
    INDEX idx_session_uuid (session_uuid),
    INDEX idx_active_sessions (is_active, start_time)
);
```

### Key Differences from Old Schema:
- **start_time** and **end_time** - instead of session_start and session_end
- **session_uuid** - unique identifier for the session
- **is_active** - boolean flag for active sessions

## API Changes Required

### ErrorReport Model
```python
class ErrorReport(BaseModel):
    app_identifier: str
    user_uuid: Optional[str] = None
    error_type: str
    error_message: str
    error_stack: Optional[str] = None
    app_version: str
    platform: str
    metadata: Optional[Dict[str, Any]] = None  # Changed from device_info and context
    session_id: Optional[int] = None  # New field
    severity: str = "medium"
```

### Error Reporting Endpoint
The `/api/v2/errors/report` endpoint should save metadata as a single JSON field instead of separate device_info and context fields.

### Query Updates
All queries referencing the old columns need to be updated:
- Replace `device_info` and `context` with `metadata`
- Remove references to `is_resolved`, `error_hash`, etc.
- Use `start_time`/`end_time` instead of `session_start`/`session_end`

## Migration Steps

1. Run the `fix_app_error_logs_schema.sql` migration script
2. Deploy the updated API code
3. Update any frontend code to send `metadata` instead of `device_info` and `context`
4. Test thoroughly before removing the old table backup

## Frontend Changes

When reporting errors, the frontend should send:
```json
{
    "app_identifier": "com.nexa.timesheet",
    "user_uuid": "user-123",
    "error_type": "api_error",
    "error_message": "Failed to fetch data",
    "error_stack": "...",
    "app_version": "1.0.0",
    "platform": "android",
    "metadata": {
        "device_info": {
            "model": "Pixel 5",
            "os": "Android 12"
        },
        "context": {
            "screen": "Dashboard",
            "action": "load_data"
        }
    },
    "session_id": 12345,
    "severity": "medium"
}
```