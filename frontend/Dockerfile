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

# Install envsubst (part of gettext)
RUN apk add --no-cache gettext

# Copy nginx config as template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Set default PORT
ENV PORT=80

# Expose port (Railway will override with PORT env var)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-80}/ || exit 1

# Start nginx with envsubst to replace PORT variable
CMD ["/bin/sh", "-c", "envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
