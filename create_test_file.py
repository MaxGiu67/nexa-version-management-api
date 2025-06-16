"""
Crea file APK di test per testare l'upload
"""
import os
import zipfile
from datetime import datetime

def create_test_apk():
    """Crea un APK di test per testare l'upload"""
    
    # Crea directory di test
    os.makedirs("test_files", exist_ok=True)
    
    apk_path = "test_files/nexa-timesheet-test.apk"
    
    # Crea un file ZIP (un APK è essenzialmente un ZIP)
    with zipfile.ZipFile(apk_path, 'w') as apk:
        # Aggiungi file fittizi che si trovano in un APK reale
        apk.writestr("AndroidManifest.xml", """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.nexa.timesheet"
    android:versionCode="1"
    android:versionName="1.0.0">
    
    <application android:label="Nexa Timesheet">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>""")
        
        apk.writestr("classes.dex", b"fake dex content for testing")
        apk.writestr("resources.arsc", b"fake resources for testing")
        apk.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nCreated-By: Test\n")
        
        # Aggiungi contenuto per rendere il file più grande
        test_content = f"Test APK created at {datetime.now()}\n" * 1000
        apk.writestr("assets/test.txt", test_content)
    
    size_kb = os.path.getsize(apk_path) / 1024
    print(f"✅ Created test APK: {apk_path} ({size_kb:.1f} KB)")
    return apk_path

def create_test_ipa():
    """Crea un IPA di test per testare l'upload"""
    
    os.makedirs("test_files", exist_ok=True)
    
    ipa_path = "test_files/nexa-timesheet-test.ipa"
    
    # Crea un file ZIP (un IPA è essenzialmente un ZIP)
    with zipfile.ZipFile(ipa_path, 'w') as ipa:
        # Struttura base di un IPA
        ipa.writestr("Payload/NexaTimesheet.app/Info.plist", """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.nexa.timesheet</string>
    <key>CFBundleName</key>
    <string>Nexa Timesheet</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
</dict>
</plist>""")
        
        ipa.writestr("Payload/NexaTimesheet.app/NexaTimesheet", b"fake binary content")
        ipa.writestr("META-INF/com.apple.ZipMetadata.plist", "fake metadata")
        
        # Aggiungi contenuto per test
        test_content = f"Test IPA created at {datetime.now()}\n" * 1000
        ipa.writestr("Payload/NexaTimesheet.app/test.txt", test_content)
    
    size_kb = os.path.getsize(ipa_path) / 1024
    print(f"✅ Created test IPA: {ipa_path} ({size_kb:.1f} KB)")
    return ipa_path

if __name__ == "__main__":
    print("🔧 Creating test files for upload testing...")
    
    apk_path = create_test_apk()
    ipa_path = create_test_ipa()
    
    print(f"\n📁 Test files created in 'test_files/' directory:")
    print(f"  - {apk_path}")
    print(f"  - {ipa_path}")
    
    print(f"\n🧪 You can now test upload with:")
    print(f"  1. Start server: python simple_api.py")
    print(f"  2. Open browser: http://localhost:8000/api/v1/app-version/upload-form")
    print(f"  3. Upload the test files")
    
    print(f"\n📋 Or use curl:")
    print(f"""  curl -X POST "http://localhost:8000/api/v1/app-version/upload" \\
    -F "file=@{apk_path}" \\
    -F "version=1.0.0" \\
    -F "platform=android" \\
    -F "version_code=1" \\
    -F "is_mandatory=false" \\
    -F "changelog={{\\"changes\\": [\\"Test upload\\", \\"Initial version\\"]}}"
    """)