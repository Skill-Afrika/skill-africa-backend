FROM node:alpine

RUN mkdir -p /usr/src/node-app && chown -R node:node /usr/src/node-app

WORKDIR /usr/src/node-app

COPY package.json pnpm-lock.yaml ./

# Install pnpm globally
RUN npm install -g pnpm

USER node

# Install dependencies (no progress bar for cleaner logs)
RUN pnpm install --frozen-lockfile --prefer-offline

COPY --chown=node:node . .

EXPOSE 3000

# Start the app with PM2
CMD ["pnpm", "start"]