FROM node:18-alpine

WORKDIR /app

# Install a lightweight HTTP server
RUN npm install -g http-server

# Copy public files
COPY public ./public

# Expose port
EXPOSE 3000

# Start the server
CMD ["http-server", "public", "-p", "3000"]
