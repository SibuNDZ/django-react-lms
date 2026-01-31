# Multi-stage Dockerfile for React frontend
# Stage 1: Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL
ARG VITE_PAYPAL_CLIENT_ID
ARG VITE_STRIPE_PUBLIC_KEY

# Set environment variables for build
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_PAYPAL_CLIENT_ID=${VITE_PAYPAL_CLIENT_ID}
ENV VITE_STRIPE_PUBLIC_KEY=${VITE_STRIPE_PUBLIC_KEY}

# Build the application
RUN npm run build

# Stage 2: Production stage with nginx
FROM nginx:alpine as production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create script for runtime environment variable injection
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-envsubst-config.sh && \
    echo 'if [ -f /usr/share/nginx/html/env-config.js ]; then' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo '  envsubst < /usr/share/nginx/html/env-config.js.template > /usr/share/nginx/html/env-config.js' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo 'fi' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    chmod +x /docker-entrypoint.d/40-envsubst-config.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
