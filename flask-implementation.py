"""
Implementazione Flask alternativa per gli endpoint di gestione versioni
Più semplice da integrare se il backend usa già Flask
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from datetime import datetime
import pymysql
import pymysql.cursors
import json
import re
import logging

# Configurazione
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'  # Cambiare in produzione
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Inizializza estensioni
jwt = JWTManager(app)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Helper functions
def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def compare_versions(v1, v2):
    """Compare semantic versions"""
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    
    for i in range(3):
        p1 = parts1[i] if i < len(parts1) else 0
        p2 = parts2[i] if i < len(parts2) else 0
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    return 0

def is_valid_version(version):
    """Validate version format"""
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# API Endpoints

@app.route('/api/v1/app-version/check', methods=['GET'])
def check_for_updates():
    """Check if updates are available"""
    try:
        current_version = request.args.get('current_version')
        platform = request.args.get('platform', 'all')
        
        # Validate parameters
        if not current_version:
            return jsonify({'error': 'Missing required parameter: current_version'}), 400
        
        if not is_valid_version(current_version):
            return jsonify({'error': 'Invalid version format. Expected: X.Y.Z'}), 400
        
        db = get_db()
        with db.cursor() as cursor:
            # Get latest active version
            query = """
                SELECT * FROM app_versions 
                WHERE platform IN (%s, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            """
            cursor.execute(query, (platform,))
            latest_version = cursor.fetchone()
            
            if not latest_version:
                return jsonify({
                    'hasUpdate': False,
                    'message': 'No versions available'
                })
            
            # Compare versions
            has_update = compare_versions(current_version, latest_version['version']) < 0
            
            # Check if mandatory
            is_mandatory = bool(latest_version['is_mandatory'])
            if latest_version['min_supported_version']:
                is_mandatory = is_mandatory or compare_versions(
                    current_version, 
                    latest_version['min_supported_version']
                ) < 0
            
            # Parse changelog
            changelog = []
            if latest_version['changelog']:
                try:
                    changelog_data = json.loads(latest_version['changelog'])
                    changelog = changelog_data.get('changes', [])
                except json.JSONDecodeError:
                    logger.error("Failed to parse changelog JSON")
            
            return jsonify({
                'hasUpdate': has_update,
                'latestVersion': latest_version['version'],
                'versionCode': latest_version['version_code'],
                'isMandatory': is_mandatory,
                'minSupportedVersion': latest_version['min_supported_version'],
                'downloadUrl': latest_version['download_url'],
                'changelog': changelog,
                'releaseDate': latest_version['release_date'].isoformat() if latest_version['release_date'] else None
            })
            
    except Exception as e:
        logger.error(f"Error checking updates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/app-version/latest', methods=['GET'])
def get_latest_version():
    """Get information about the latest version"""
    try:
        platform = request.args.get('platform', 'all')
        
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT * FROM app_versions 
                WHERE platform IN (%s, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            """
            cursor.execute(query, (platform,))
            latest_version = cursor.fetchone()
            
            if not latest_version:
                return jsonify({'error': 'No version found'}), 404
            
            # Parse changelog
            changelog = []
            if latest_version['changelog']:
                try:
                    changelog_data = json.loads(latest_version['changelog'])
                    changelog = changelog_data.get('changes', [])
                except json.JSONDecodeError:
                    logger.error("Failed to parse changelog JSON")
            
            return jsonify({
                'version': latest_version['version'],
                'versionCode': latest_version['version_code'],
                'platform': latest_version['platform'],
                'releaseDate': latest_version['release_date'].isoformat(),
                'downloadUrl': latest_version['download_url'],
                'changelog': changelog,
                'isMandatory': bool(latest_version['is_mandatory']),
                'minSupportedVersion': latest_version['min_supported_version']
            })
            
    except Exception as e:
        logger.error(f"Error getting latest version: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/app-version/log-update', methods=['POST'])
@jwt_required()
def log_update():
    """Log a user's app update"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['to_version', 'platform', 'update_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        from_version = data.get('from_version')
        to_version = data['to_version']
        platform = data['platform']
        update_type = data['update_type']
        device_info = data.get('device_info', {})
        
        # Validate version format
        if not is_valid_version(to_version):
            return jsonify({'error': 'Invalid to_version format'}), 400
        
        if from_version and not is_valid_version(from_version):
            return jsonify({'error': 'Invalid from_version format'}), 400
        
        # Validate platform
        if platform not in ['ios', 'android']:
            return jsonify({'error': 'Invalid platform. Must be: ios or android'}), 400
        
        # Validate update type
        if update_type not in ['manual', 'forced', 'auto']:
            return jsonify({'error': 'Invalid update_type. Must be: manual, forced, or auto'}), 400
        
        db = get_db()
        with db.cursor() as cursor:
            query = """
                INSERT INTO app_update_logs 
                (user_id, from_version, to_version, platform, update_type, device_info) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                user_id,
                from_version,
                to_version,
                platform,
                update_type,
                json.dumps(device_info)
            ))
            
            db.commit()
            log_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'Update logged successfully',
                'log_id': log_id
            }), 201
            
    except Exception as e:
        logger.error(f"Error logging update: {str(e)}")
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/app-version/history', methods=['GET'])
@admin_required
def get_version_history():
    """Get version history with update counts (admin only)"""
    try:
        platform = request.args.get('platform', 'all')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Validate limit and offset
        if limit < 1 or limit > 100:
            return jsonify({'error': 'Limit must be between 1 and 100'}), 400
        
        if offset < 0:
            return jsonify({'error': 'Offset must be non-negative'}), 400
        
        db = get_db()
        with db.cursor() as cursor:
            # Get versions with update count
            query = """
                SELECT 
                    v.*,
                    COUNT(DISTINCT ul.user_id) as update_count
                FROM app_versions v
                LEFT JOIN app_update_logs ul ON ul.to_version = v.version
                WHERE (v.platform = %s OR v.platform = 'all')
                GROUP BY v.id
                ORDER BY v.version_code DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (platform, limit, offset))
            versions = cursor.fetchall()
            
            # Get total count
            count_query = """
                SELECT COUNT(*) as total 
                FROM app_versions 
                WHERE platform IN (%s, 'all')
            """
            cursor.execute(count_query, (platform,))
            total = cursor.fetchone()['total']
            
            # Format response
            formatted_versions = []
            for v in versions:
                formatted_versions.append({
                    'version': v['version'],
                    'versionCode': v['version_code'],
                    'platform': v['platform'],
                    'releaseDate': v['release_date'].isoformat() if v['release_date'] else None,
                    'isActive': bool(v['is_active']),
                    'isMandatory': bool(v['is_mandatory']),
                    'downloadUrl': v['download_url'],
                    'updateCount': v['update_count']
                })
            
            return jsonify({
                'versions': formatted_versions,
                'total': total
            })
            
    except Exception as e:
        logger.error(f"Error getting version history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/app-version/stats', methods=['GET'])
@admin_required
def get_update_statistics():
    """Get update statistics (admin only)"""
    try:
        db = get_db()
        with db.cursor() as cursor:
            # Total users
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) as totalUsers FROM app_update_logs"
            )
            total_users = cursor.fetchone()['totalUsers']
            
            # Version distribution (MySQL compatible)
            version_query = """
                SELECT 
                    to_version as version,
                    platform,
                    COUNT(DISTINCT user_id) as count
                FROM (
                    SELECT 
                        ul1.user_id, 
                        ul1.to_version, 
                        ul1.platform
                    FROM app_update_logs ul1
                    INNER JOIN (
                        SELECT user_id, MAX(created_at) as max_created
                        FROM app_update_logs
                        GROUP BY user_id
                    ) ul2 ON ul1.user_id = ul2.user_id AND ul1.created_at = ul2.max_created
                ) latest_updates
                GROUP BY to_version, platform
            """
            
            cursor.execute(version_query)
            version_data = cursor.fetchall()
            
            # Process version distribution
            version_distribution = {}
            for row in version_data:
                version = row['version']
                if version not in version_distribution:
                    version_distribution[version] = {
                        'count': 0,
                        'percentage': 0,
                        'platforms': {}
                    }
                version_distribution[version]['count'] += row['count']
                version_distribution[version]['platforms'][row['platform']] = row['count']
            
            # Calculate percentages
            if total_users > 0:
                for version in version_distribution:
                    version_distribution[version]['percentage'] = round(
                        (version_distribution[version]['count'] / total_users) * 100, 1
                    )
            
            # Last updates
            last_updates_query = """
                SELECT 
                    ul.user_id,
                    CONCAT(p.firstName, ' ', p.lastName) as userName,
                    ul.from_version,
                    ul.to_version,
                    ul.platform,
                    ul.created_at as updatedAt
                FROM app_update_logs ul
                LEFT JOIN accounts a ON ul.user_id = a.id
                LEFT JOIN persons p ON a.person_id = p.id
                ORDER BY ul.created_at DESC
                LIMIT 10
            """
            
            cursor.execute(last_updates_query)
            last_updates = cursor.fetchall()
            
            # Format last updates
            formatted_updates = []
            for update in last_updates:
                formatted_updates.append({
                    'userId': update['user_id'],
                    'userName': update['userName'] or 'Unknown',
                    'fromVersion': update['from_version'],
                    'toVersion': update['to_version'],
                    'platform': update['platform'],
                    'updatedAt': update['updatedAt'].isoformat() if update['updatedAt'] else None
                })
            
            return jsonify({
                'totalUsers': total_users,
                'versionDistribution': version_distribution,
                'lastUpdates': formatted_updates
            })
            
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/app-version/version', methods=['POST'])
@admin_required
def create_or_update_version():
    """Create or update an app version (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['version', 'version_code', 'platform', 'release_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate version format
        if not is_valid_version(data['version']):
            return jsonify({'error': 'Invalid version format'}), 400
        
        db = get_db()
        with db.cursor() as cursor:
            # Check if version exists
            check_query = "SELECT id FROM app_versions WHERE version = %s AND platform = %s"
            cursor.execute(check_query, (data['version'], data['platform']))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing version
                update_query = """
                    UPDATE app_versions SET
                        version_code = %s,
                        release_date = %s,
                        is_mandatory = %s,
                        min_supported_version = %s,
                        download_url = %s,
                        changelog = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(update_query, (
                    data['version_code'],
                    data['release_date'],
                    data.get('is_mandatory', False),
                    data.get('min_supported_version'),
                    data.get('download_url'),
                    json.dumps(data.get('changelog', {'changes': []})),
                    existing['id']
                ))
                message = "Version updated successfully"
            else:
                # Create new version
                insert_query = """
                    INSERT INTO app_versions 
                    (version, version_code, platform, release_date, is_mandatory,
                     min_supported_version, download_url, changelog, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
                """
                cursor.execute(insert_query, (
                    data['version'],
                    data['version_code'],
                    data['platform'],
                    data['release_date'],
                    data.get('is_mandatory', False),
                    data.get('min_supported_version'),
                    data.get('download_url'),
                    json.dumps(data.get('changelog', {'changes': []}))
                ))
                message = "Version created successfully"
            
            db.commit()
            
            return jsonify({
                'success': True,
                'message': message
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating/updating version: {str(e)}")
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'app-version-management',
        'framework': 'flask'
    })

# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)