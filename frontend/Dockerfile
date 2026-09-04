FROM node:20-alpine as build

WORKDIR /app

# Package setup would go here
# COPY package*.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# Nginx setup
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
