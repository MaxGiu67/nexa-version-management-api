-- Script per creare l'app nel database
INSERT INTO apps (app_identifier, app_name, description, created_at, updated_at)
VALUES (
    'com.nexa.timesheet',
    'Nexa Timesheet',
    'Mobile app per la gestione dei timesheet NEXA DATA',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    app_name = VALUES(app_name),
    updated_at = NOW();

-- Verifica che l'app sia stata creata
SELECT * FROM apps WHERE app_identifier = 'com.nexa.timesheet';