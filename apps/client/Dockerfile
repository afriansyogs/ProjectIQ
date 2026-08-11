FROM node:20-alpine AS base

WORKDIR /app

COPY package.json bun.lock* ./
RUN npm install -g bun && bun install

COPY . .

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["bun", "run", "dev"]
