// Implementazione Node.js/Express per gli endpoint di gestione versioni
const express = require('express');
const router = express.Router();
const db = require('../database'); // Assumendo un modulo database

// Middleware per autenticazione
const authenticateToken = require('../middleware/auth');
const requireAdmin = require('../middleware/admin');

// Helper per confrontare versioni semver
function compareVersions(v1, v2) {
  const parts1 = v1.split('.').map(Number);
  const parts2 = v2.split('.').map(Number);
  
  for (let i = 0; i < 3; i++) {
    if ((parts1[i] || 0) < (parts2[i] || 0)) return -1;
    if ((parts1[i] || 0) > (parts2[i] || 0)) return 1;
  }
  
  return 0;
}

// Helper per validare versione
function isValidVersion(version) {
  return /^\d+\.\d+\.\d+$/.test(version);
}

// 1. Check for updates
router.get('/check', async (req, res) => {
  try {
    const { current_version, platform = 'all' } = req.query;
    
    // Validazione parametri
    if (!current_version) {
      return res.status(400).json({ 
        error: 'Missing required parameter: current_version' 
      });
    }
    
    if (!isValidVersion(current_version)) {
      return res.status(400).json({ 
        error: 'Invalid version format. Expected: X.Y.Z' 
      });
    }
    
    // Query per l'ultima versione attiva
    const query = `
      SELECT * FROM app_versions 
      WHERE platform IN (?, 'all') 
      AND is_active = true 
      ORDER BY version_code DESC 
      LIMIT 1
    `;
    
    const [latestVersion] = await db.query(query, [platform]);
    
    if (!latestVersion) {
      return res.json({ 
        hasUpdate: false,
        message: 'No versions available'
      });
    }
    
    // Confronta versioni
    const hasUpdate = compareVersions(current_version, latestVersion.version) < 0;
    
    // Controlla se è obbligatorio
    const isMandatory = latestVersion.is_mandatory || 
      (latestVersion.min_supported_version && 
       compareVersions(current_version, latestVersion.min_supported_version) < 0);
    
    res.json({
      hasUpdate,
      latestVersion: latestVersion.version,
      versionCode: latestVersion.version_code,
      isMandatory,
      minSupportedVersion: latestVersion.min_supported_version,
      downloadUrl: latestVersion.download_url,
      changelog: latestVersion.changelog?.changes || [],
      releaseDate: latestVersion.release_date
    });
    
  } catch (error) {
    console.error('Error checking updates:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 2. Get latest version info
router.get('/latest', async (req, res) => {
  try {
    const { platform = 'all' } = req.query;
    
    const query = `
      SELECT * FROM app_versions 
      WHERE platform IN (?, 'all') 
      AND is_active = true 
      ORDER BY version_code DESC 
      LIMIT 1
    `;
    
    const [latestVersion] = await db.query(query, [platform]);
    
    if (!latestVersion) {
      return res.status(404).json({ error: 'No version found' });
    }
    
    res.json({
      version: latestVersion.version,
      versionCode: latestVersion.version_code,
      platform: latestVersion.platform,
      releaseDate: latestVersion.release_date,
      downloadUrl: latestVersion.download_url,
      changelog: latestVersion.changelog?.changes || [],
      isMandatory: latestVersion.is_mandatory,
      minSupportedVersion: latestVersion.min_supported_version
    });
    
  } catch (error) {
    console.error('Error getting latest version:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 3. Log update (richiede autenticazione)
router.post('/log-update', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id; // Dal JWT decodificato
    const { from_version, to_version, platform, update_type, device_info } = req.body;
    
    // Validazione
    if (!to_version || !platform || !update_type) {
      return res.status(400).json({ 
        error: 'Missing required fields: to_version, platform, update_type' 
      });
    }
    
    if (!isValidVersion(to_version) || (from_version && !isValidVersion(from_version))) {
      return res.status(400).json({ 
        error: 'Invalid version format' 
      });
    }
    
    const validPlatforms = ['ios', 'android'];
    const validUpdateTypes = ['manual', 'forced', 'auto'];
    
    if (!validPlatforms.includes(platform)) {
      return res.status(400).json({ 
        error: 'Invalid platform. Must be: ios or android' 
      });
    }
    
    if (!validUpdateTypes.includes(update_type)) {
      return res.status(400).json({ 
        error: 'Invalid update_type. Must be: manual, forced, or auto' 
      });
    }
    
    // Inserisci log
    const query = `
      INSERT INTO app_update_logs 
      (user_id, from_version, to_version, platform, update_type, device_info) 
      VALUES (?, ?, ?, ?, ?, ?)
    `;
    
    const result = await db.query(query, [
      userId, 
      from_version || null, 
      to_version, 
      platform, 
      update_type, 
      JSON.stringify(device_info || {})
    ]);
    
    res.status(201).json({
      success: true,
      message: 'Update logged successfully',
      log_id: result.insertId
    });
    
  } catch (error) {
    console.error('Error logging update:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 4. Get version history (richiede admin)
router.get('/history', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { platform = 'all', limit = 10, offset = 0 } = req.query;
    
    // Query per storico versioni con conteggio aggiornamenti
    const query = `
      SELECT 
        v.*,
        COUNT(DISTINCT ul.user_id) as update_count
      FROM app_versions v
      LEFT JOIN app_update_logs ul ON ul.to_version = v.version
      WHERE (v.platform = ? OR v.platform = 'all')
      GROUP BY v.id
      ORDER BY v.version_code DESC
      LIMIT ? OFFSET ?
    `;
    
    const versions = await db.query(query, [platform, parseInt(limit), parseInt(offset)]);
    
    // Conteggio totale
    const [{ total }] = await db.query(
      'SELECT COUNT(*) as total FROM app_versions WHERE platform IN (?, "all")',
      [platform]
    );
    
    res.json({
      versions: versions.map(v => ({
        version: v.version,
        versionCode: v.version_code,
        platform: v.platform,
        releaseDate: v.release_date,
        isActive: v.is_active,
        isMandatory: v.is_mandatory,
        downloadUrl: v.download_url,
        updateCount: v.update_count
      })),
      total
    });
    
  } catch (error) {
    console.error('Error getting version history:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 5. Get update statistics (richiede admin)
router.get('/stats', authenticateToken, requireAdmin, async (req, res) => {
  try {
    // Conteggio utenti totali
    const [{ totalUsers }] = await db.query(
      'SELECT COUNT(DISTINCT user_id) as totalUsers FROM app_update_logs'
    );
    
    // Distribuzione versioni
    const versionQuery = `
      SELECT 
        to_version as version,
        platform,
        COUNT(DISTINCT user_id) as count
      FROM (
        SELECT 
          user_id, 
          to_version, 
          platform,
          ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
        FROM app_update_logs
      ) latest_updates
      WHERE rn = 1
      GROUP BY to_version, platform
    `;
    
    const versionData = await db.query(versionQuery);
    
    // Raggruppa per versione
    const versionDistribution = {};
    versionData.forEach(row => {
      if (!versionDistribution[row.version]) {
        versionDistribution[row.version] = {
          count: 0,
          percentage: 0,
          platforms: {}
        };
      }
      versionDistribution[row.version].count += row.count;
      versionDistribution[row.version].platforms[row.platform] = row.count;
    });
    
    // Calcola percentuali
    Object.keys(versionDistribution).forEach(version => {
      versionDistribution[version].percentage = 
        (versionDistribution[version].count / totalUsers * 100).toFixed(1);
    });
    
    // Ultimi aggiornamenti
    const lastUpdatesQuery = `
      SELECT 
        ul.user_id,
        u.name as userName,
        ul.from_version,
        ul.to_version,
        ul.platform,
        ul.created_at as updatedAt
      FROM app_update_logs ul
      LEFT JOIN users u ON ul.user_id = u.id
      ORDER BY ul.created_at DESC
      LIMIT 10
    `;
    
    const lastUpdates = await db.query(lastUpdatesQuery);
    
    res.json({
      totalUsers,
      versionDistribution,
      lastUpdates
    });
    
  } catch (error) {
    console.error('Error getting statistics:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Endpoint per creare/aggiornare versione (admin)
router.post('/version', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { 
      version, version_code, platform, release_date, 
      is_mandatory, min_supported_version, download_url, changelog 
    } = req.body;
    
    // Validazione completa
    if (!version || !version_code || !platform || !release_date) {
      return res.status(400).json({ 
        error: 'Missing required fields' 
      });
    }
    
    const query = `
      INSERT INTO app_versions 
      (version, version_code, platform, release_date, is_mandatory, 
       min_supported_version, download_url, changelog, is_active)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, true)
      ON DUPLICATE KEY UPDATE
        version_code = VALUES(version_code),
        release_date = VALUES(release_date),
        is_mandatory = VALUES(is_mandatory),
        min_supported_version = VALUES(min_supported_version),
        download_url = VALUES(download_url),
        changelog = VALUES(changelog),
        updated_at = CURRENT_TIMESTAMP
    `;
    
    await db.query(query, [
      version, version_code, platform, release_date,
      is_mandatory || false, min_supported_version || null,
      download_url || null, JSON.stringify(changelog || {})
    ]);
    
    res.json({ 
      success: true, 
      message: 'Version created/updated successfully' 
    });
    
  } catch (error) {
    console.error('Error creating version:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;