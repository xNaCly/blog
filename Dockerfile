FROM alpine AS build
RUN apk add --no-cache hugo
WORKDIR /blog
COPY . .
RUN hugo --minify --baseURL http://localhost

FROM nginx:alpine
COPY --from=build /blog/public /data/www
COPY nginx.conf /etc/nginx/nginx.conf
