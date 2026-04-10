FROM node:20-alpine

ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

EXPOSE 3000
