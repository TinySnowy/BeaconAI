FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the Next.js application
# RUN npm run build

# Expose the port for the frontend
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev"] 