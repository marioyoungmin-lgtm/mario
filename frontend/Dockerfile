FROM node:20-alpine

WORKDIR /app

# Install dependencies.
COPY package*.json ./
RUN npm install

# Copy app source.
COPY . .

EXPOSE 3000

# Start Next.js dev server for quick demo iteration.
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
