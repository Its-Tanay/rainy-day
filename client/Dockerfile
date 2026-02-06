FROM node:18-alpine AS base

WORKDIR /app

COPY package*.json ./

FROM base AS development

RUN npm install

COPY . .

EXPOSE 3001

ENV REACT_APP_BASE_URL_DEV=http://localhost:3000/

CMD ["npm", "start"]
