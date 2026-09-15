FROM nginxinc/nginx-unprivileged:1.31.4-alpine3.24

# Upgrade Alpine packages to pick up fixes published after this base image was built
# (e.g. libexpat 2.8.4-r0, util-linux 2.42.3-r1) that resolve known CVEs.
USER root
RUN apk update && apk upgrade --no-cache
USER nginx

RUN ["rm", "/etc/nginx/conf.d/default.conf"]

COPY proxy.conf.template /etc/nginx/templates/proxy.conf.template
COPY settings.conf.template /etc/nginx/templates/settings.conf.template
