# Frontend Dockerfile - OpenShift compatible
FROM nginx:alpine

# Switch to root to set up permissions
USER root

# Copy HTML file and nginx config
COPY simple_frontend.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx cache directories and set permissions for OpenShift
# OpenShift runs containers with random UIDs, so we need to make these writable by any user
RUN mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp && \
    chmod -R 777 /var/cache/nginx && \
    chmod -R 777 /var/run && \
    chmod -R 777 /var/log/nginx && \
    # Make nginx.conf readable by all
    chmod 644 /etc/nginx/nginx.conf && \
    # Create pid file location
    touch /var/run/nginx.pid && \
    chmod 666 /var/run/nginx.pid && \
    # Make HTML directory writable
    chmod -R 755 /usr/share/nginx/html

# Support arbitrary user IDs (OpenShift requirement)
RUN chgrp -R 0 /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html && \
    chmod -R g=u /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# Expose port 8080 (OpenShift doesn't allow privileged ports < 1024)
EXPOSE 8080

# Switch to non-root user (OpenShift will override this with a random UID)
USER 1001

# Health check - update to use port 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080 || exit 1

CMD ["nginx", "-g", "daemon off;"]