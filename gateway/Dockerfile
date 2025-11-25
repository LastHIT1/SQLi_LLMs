FROM openresty/openresty:alpine-fat

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
COPY guardrail.lua /usr/local/openresty/nginx/guardrail.lua

RUN /usr/local/openresty/luajit/bin/luarocks install lua-resty-http