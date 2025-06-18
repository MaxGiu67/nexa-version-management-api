#!/bin/bash

echo "🔧 Fixing styled-components transient props..."

# Fix in UploadForm.tsx
echo "Fixing UploadForm.tsx..."
sed -i '' 's/<{ isDragging: boolean; hasFile: boolean }>/<{ $isDragging: boolean; $hasFile: boolean }>/g' src/components/UploadForm.tsx
sed -i '' 's/props\.isDragging/props.$isDragging/g' src/components/UploadForm.tsx
sed -i '' 's/props\.hasFile/props.$hasFile/g' src/components/UploadForm.tsx
sed -i '' 's/isDragging={isDragging}/$isDragging={isDragging}/g' src/components/UploadForm.tsx
sed -i '' 's/hasFile={!!file}/$hasFile={!!file}/g' src/components/UploadForm.tsx

# Fix variant props
echo "Fixing variant props..."
sed -i '' 's/<{ variant?: /<{ $variant?: /g' src/components/UploadForm.tsx
sed -i '' 's/<{ variant?: /<{ $variant?: /g' src/components/ApplicationsManager.tsx
sed -i '' 's/<{ variant?: /<{ $variant?: /g' src/components/VersionsList.tsx
sed -i '' 's/props\.variant/props.$variant/g' src/components/UploadForm.tsx
sed -i '' 's/props\.variant/props.$variant/g' src/components/ApplicationsManager.tsx
sed -i '' 's/props\.variant/props.$variant/g' src/components/VersionsList.tsx
sed -i '' 's/variant={/$variant={/g' src/components/UploadForm.tsx
sed -i '' 's/variant={/$variant={/g' src/components/ApplicationsManager.tsx
sed -i '' 's/variant={/$variant={/g' src/components/VersionsList.tsx

# Fix active props
echo "Fixing active props..."
sed -i '' 's/<{ active: boolean }>/<{ $active: boolean }>/g' src/components/AppDetail.tsx
sed -i '' 's/<{ active: boolean }>/<{ $active: boolean }>/g' src/components/ApplicationsManager.tsx
sed -i '' 's/<{ active: boolean }>/<{ $active: boolean }>/g' src/components/SessionsDashboard.tsx
sed -i '' 's/props\.active/props.$active/g' src/components/AppDetail.tsx
sed -i '' 's/props\.active/props.$active/g' src/components/ApplicationsManager.tsx
sed -i '' 's/props\.active/props.$active/g' src/components/SessionsDashboard.tsx
sed -i '' 's/active={/$active={/g' src/components/AppDetail.tsx
sed -i '' 's/active={/$active={/g' src/components/ApplicationsManager.tsx
sed -i '' 's/active={/$active={/g' src/components/SessionsDashboard.tsx

echo "✅ Done! All styled-components props are now transient."