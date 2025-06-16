<?php
// Implementazione PHP per gli endpoint di gestione versioni
// Compatibile con il framework esistente del backend Portaal

class AppVersionController {
    private $db;
    
    public function __construct($database) {
        $this->db = $database;
    }
    
    /**
     * Helper per confrontare versioni semver
     */
    private function compareVersions($v1, $v2) {
        return version_compare($v1, $v2);
    }
    
    /**
     * Helper per validare formato versione
     */
    private function isValidVersion($version) {
        return preg_match('/^\d+\.\d+\.\d+$/', $version);
    }
    
    /**
     * GET /api/v1/app-version/check
     * Controlla se sono disponibili aggiornamenti
     */
    public function checkForUpdates() {
        try {
            $currentVersion = $_GET['current_version'] ?? null;
            $platform = $_GET['platform'] ?? 'all';
            
            // Validazione parametri
            if (!$currentVersion) {
                http_response_code(400);
                return json_encode([
                    'error' => 'Missing required parameter: current_version'
                ]);
            }
            
            if (!$this->isValidVersion($currentVersion)) {
                http_response_code(400);
                return json_encode([
                    'error' => 'Invalid version format. Expected: X.Y.Z'
                ]);
            }
            
            // Query per l'ultima versione attiva
            $stmt = $this->db->prepare("
                SELECT * FROM app_versions 
                WHERE platform IN (:platform, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            ");
            
            $stmt->execute(['platform' => $platform]);
            $latestVersion = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if (!$latestVersion) {
                return json_encode([
                    'hasUpdate' => false,
                    'message' => 'No versions available'
                ]);
            }
            
            // Confronta versioni
            $hasUpdate = $this->compareVersions($currentVersion, $latestVersion['version']) < 0;
            
            // Controlla se è obbligatorio
            $isMandatory = $latestVersion['is_mandatory'] || 
                ($latestVersion['min_supported_version'] && 
                 $this->compareVersions($currentVersion, $latestVersion['min_supported_version']) < 0);
            
            // Decodifica changelog JSON
            $changelog = json_decode($latestVersion['changelog'], true);
            
            return json_encode([
                'hasUpdate' => $hasUpdate,
                'latestVersion' => $latestVersion['version'],
                'versionCode' => (int)$latestVersion['version_code'],
                'isMandatory' => (bool)$isMandatory,
                'minSupportedVersion' => $latestVersion['min_supported_version'],
                'downloadUrl' => $latestVersion['download_url'],
                'changelog' => $changelog['changes'] ?? [],
                'releaseDate' => $latestVersion['release_date']
            ]);
            
        } catch (Exception $e) {
            error_log('Error checking updates: ' . $e->getMessage());
            http_response_code(500);
            return json_encode(['error' => 'Internal server error']);
        }
    }
    
    /**
     * GET /api/v1/app-version/latest
     * Ottiene informazioni sull'ultima versione
     */
    public function getLatestVersion() {
        try {
            $platform = $_GET['platform'] ?? 'all';
            
            $stmt = $this->db->prepare("
                SELECT * FROM app_versions 
                WHERE platform IN (:platform, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            ");
            
            $stmt->execute(['platform' => $platform]);
            $latestVersion = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if (!$latestVersion) {
                http_response_code(404);
                return json_encode(['error' => 'No version found']);
            }
            
            $changelog = json_decode($latestVersion['changelog'], true);
            
            return json_encode([
                'version' => $latestVersion['version'],
                'versionCode' => (int)$latestVersion['version_code'],
                'platform' => $latestVersion['platform'],
                'releaseDate' => $latestVersion['release_date'],
                'downloadUrl' => $latestVersion['download_url'],
                'changelog' => $changelog['changes'] ?? [],
                'isMandatory' => (bool)$latestVersion['is_mandatory'],
                'minSupportedVersion' => $latestVersion['min_supported_version']
            ]);
            
        } catch (Exception $e) {
            error_log('Error getting latest version: ' . $e->getMessage());
            http_response_code(500);
            return json_encode(['error' => 'Internal server error']);
        }
    }
    
    /**
     * POST /api/v1/app-version/log-update
     * Registra l'aggiornamento di un utente (richiede autenticazione)
     */
    public function logUpdate($userId) {
        try {
            $data = json_decode(file_get_contents('php://input'), true);
            
            // Validazione
            $requiredFields = ['to_version', 'platform', 'update_type'];
            foreach ($requiredFields as $field) {
                if (!isset($data[$field]) || empty($data[$field])) {
                    http_response_code(400);
                    return json_encode([
                        'error' => "Missing required field: $field"
                    ]);
                }
            }
            
            $fromVersion = $data['from_version'] ?? null;
            $toVersion = $data['to_version'];
            $platform = $data['platform'];
            $updateType = $data['update_type'];
            $deviceInfo = $data['device_info'] ?? [];
            
            // Validazione formato versione
            if (!$this->isValidVersion($toVersion) || 
                ($fromVersion && !$this->isValidVersion($fromVersion))) {
                http_response_code(400);
                return json_encode(['error' => 'Invalid version format']);
            }
            
            // Validazione platform
            if (!in_array($platform, ['ios', 'android'])) {
                http_response_code(400);
                return json_encode([
                    'error' => 'Invalid platform. Must be: ios or android'
                ]);
            }
            
            // Validazione update_type
            if (!in_array($updateType, ['manual', 'forced', 'auto'])) {
                http_response_code(400);
                return json_encode([
                    'error' => 'Invalid update_type. Must be: manual, forced, or auto'
                ]);
            }
            
            // Inserisci log
            $stmt = $this->db->prepare("
                INSERT INTO app_update_logs 
                (user_id, from_version, to_version, platform, update_type, device_info) 
                VALUES (:user_id, :from_version, :to_version, :platform, :update_type, :device_info)
            ");
            
            $stmt->execute([
                'user_id' => $userId,
                'from_version' => $fromVersion,
                'to_version' => $toVersion,
                'platform' => $platform,
                'update_type' => $updateType,
                'device_info' => json_encode($deviceInfo)
            ]);
            
            http_response_code(201);
            return json_encode([
                'success' => true,
                'message' => 'Update logged successfully',
                'log_id' => $this->db->lastInsertId()
            ]);
            
        } catch (Exception $e) {
            error_log('Error logging update: ' . $e->getMessage());
            http_response_code(500);
            return json_encode(['error' => 'Internal server error']);
        }
    }
    
    /**
     * GET /api/v1/app-version/history
     * Ottiene lo storico delle versioni (richiede admin)
     */
    public function getVersionHistory() {
        try {
            $platform = $_GET['platform'] ?? 'all';
            $limit = (int)($_GET['limit'] ?? 10);
            $offset = (int)($_GET['offset'] ?? 0);
            
            // Query per storico versioni con conteggio aggiornamenti
            $stmt = $this->db->prepare("
                SELECT 
                    v.*,
                    COUNT(DISTINCT ul.user_id) as update_count
                FROM app_versions v
                LEFT JOIN app_update_logs ul ON ul.to_version = v.version
                WHERE (v.platform = :platform OR v.platform = 'all')
                GROUP BY v.id
                ORDER BY v.version_code DESC
                LIMIT :limit OFFSET :offset
            ");
            
            $stmt->bindValue(':platform', $platform);
            $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
            $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
            $stmt->execute();
            
            $versions = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Conteggio totale
            $countStmt = $this->db->prepare("
                SELECT COUNT(*) as total 
                FROM app_versions 
                WHERE platform IN (:platform, 'all')
            ");
            $countStmt->execute(['platform' => $platform]);
            $total = $countStmt->fetch(PDO::FETCH_ASSOC)['total'];
            
            $result = [
                'versions' => array_map(function($v) {
                    return [
                        'version' => $v['version'],
                        'versionCode' => (int)$v['version_code'],
                        'platform' => $v['platform'],
                        'releaseDate' => $v['release_date'],
                        'isActive' => (bool)$v['is_active'],
                        'isMandatory' => (bool)$v['is_mandatory'],
                        'downloadUrl' => $v['download_url'],
                        'updateCount' => (int)$v['update_count']
                    ];
                }, $versions),
                'total' => (int)$total
            ];
            
            return json_encode($result);
            
        } catch (Exception $e) {
            error_log('Error getting version history: ' . $e->getMessage());
            http_response_code(500);
            return json_encode(['error' => 'Internal server error']);
        }
    }
    
    /**
     * GET /api/v1/app-version/stats
     * Ottiene statistiche sugli aggiornamenti (richiede admin)
     */
    public function getUpdateStatistics() {
        try {
            // Conteggio utenti totali
            $stmt = $this->db->query("
                SELECT COUNT(DISTINCT user_id) as totalUsers 
                FROM app_update_logs
            ");
            $totalUsers = $stmt->fetch(PDO::FETCH_ASSOC)['totalUsers'];
            
            // Distribuzione versioni (ultima versione per utente)
            $versionStmt = $this->db->query("
                SELECT 
                    to_version as version,
                    platform,
                    COUNT(DISTINCT user_id) as count
                FROM (
                    SELECT 
                        user_id, 
                        to_version, 
                        platform,
                        created_at,
                        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
                    FROM app_update_logs
                ) latest_updates
                WHERE rn = 1
                GROUP BY to_version, platform
            ");
            
            $versionData = $versionStmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Raggruppa per versione
            $versionDistribution = [];
            foreach ($versionData as $row) {
                $version = $row['version'];
                if (!isset($versionDistribution[$version])) {
                    $versionDistribution[$version] = [
                        'count' => 0,
                        'percentage' => 0,
                        'platforms' => []
                    ];
                }
                $versionDistribution[$version]['count'] += $row['count'];
                $versionDistribution[$version]['platforms'][$row['platform']] = (int)$row['count'];
            }
            
            // Calcola percentuali
            foreach ($versionDistribution as $version => &$data) {
                $data['percentage'] = round(($data['count'] / $totalUsers) * 100, 1);
            }
            
            // Ultimi aggiornamenti
            $lastUpdatesStmt = $this->db->query("
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
            ");
            
            $lastUpdates = $lastUpdatesStmt->fetchAll(PDO::FETCH_ASSOC);
            
            return json_encode([
                'totalUsers' => (int)$totalUsers,
                'versionDistribution' => $versionDistribution,
                'lastUpdates' => $lastUpdates
            ]);
            
        } catch (Exception $e) {
            error_log('Error getting statistics: ' . $e->getMessage());
            http_response_code(500);
            return json_encode(['error' => 'Internal server error']);
        }
    }
}

// Esempio di routing (adatta al framework esistente)
// Nel file delle route del backend:
/*
$router->get('/api/v1/app-version/check', function() {
    $controller = new AppVersionController($db);
    echo $controller->checkForUpdates();
});

$router->get('/api/v1/app-version/latest', function() {
    $controller = new AppVersionController($db);
    echo $controller->getLatestVersion();
});

$router->post('/api/v1/app-version/log-update', ['middleware' => 'auth'], function($request) {
    $controller = new AppVersionController($db);
    $userId = $request->user->id;
    echo $controller->logUpdate($userId);
});

$router->get('/api/v1/app-version/history', ['middleware' => ['auth', 'admin']], function() {
    $controller = new AppVersionController($db);
    echo $controller->getVersionHistory();
});

$router->get('/api/v1/app-version/stats', ['middleware' => ['auth', 'admin']], function() {
    $controller = new AppVersionController($db);
    echo $controller->getUpdateStatistics();
});
*/