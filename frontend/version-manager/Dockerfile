# Build stage
FROM node:18-alpine as builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./

# Create npmrc
RUN echo "legacy-peer-deps=true" > .npmrc

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy all source files
COPY . .

# List files to debug
RUN ls -la
RUN ls -la src/

# Set build environment
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV REACT_APP_API_URL=https://nexa-version-management-be.up.railway.app
ENV REACT_APP_API_KEY=nexa_internal_app_key_2025
ENV CI=false
ENV GENERATE_SOURCEMAP=false
ENV SKIP_PREFLIGHT_CHECK=true

# Try to build and show errors
RUN npm run build 2>&1 || (echo "Build failed with exit code $?" && exit 1)

# Production stage
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/build ./build
ENV PORT=3000
EXPOSE $PORT
CMD serve -s build -l $PORT