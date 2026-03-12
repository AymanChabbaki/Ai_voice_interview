# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – Builder
#   Installs Node dependencies and produces the static Vite build output.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer-cached unless package files change)
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY . .

# VITE_API_URL is injected at build time via --build-arg so the compiled JS
# bundle points at the correct backend URL.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – Runtime
#   Serves the compiled static files with Nginx.
#   Total image size is typically < 30 MB.
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove the default Nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy Vite output from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom Nginx config:
#   • serve index.html for every path (React SPA client-side routing)
#   • proxy /api → backend-service:8000   (optional, enables same-origin API calls)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
