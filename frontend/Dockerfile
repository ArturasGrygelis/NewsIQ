# Development Dockerfile for Next.js with hot reload
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

ENV NEXT_TELEMETRY_DISABLED=1

# Run in development mode with hot reload
CMD ["npm", "run", "dev"]
