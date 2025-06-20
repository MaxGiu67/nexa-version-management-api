FROM node:18-alpine

WORKDIR /app

# Copy all files
COPY . .

# Remove any existing node_modules and package-lock
RUN rm -rf node_modules package-lock.json

# Install dependencies fresh
RUN npm install --legacy-peer-deps --force

# Fix specific dependency issues
RUN npm install ajv@8.12.0 --save-dev --force

# Set environment variables
ENV CI=false
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_API_URL=https://nexa-version-management-be.up.railway.app
ENV REACT_APP_API_KEY=nexa_internal_app_key_2025

# Build the app
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start command - serve richiede solo la porta, non l'indirizzo
# Per default serve ascolta su tutte le interfacce (0.0.0.0)
CMD ["sh", "-c", "serve -s build -l ${PORT:-3000}"]