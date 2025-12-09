FROM owasp/modsecurity-crs:nginx-alpine

# Crea la directory log con permessi corretti
USER root
RUN mkdir -p /var/log/modsecurity && \
    chown -R nginx:nginx /var/log/modsecurity && \
    chmod 755 /var/log/modsecurity

# Copia lo script di entrypoint personalizzato
COPY docker-entrypoint-wrapper.sh /docker-entrypoint-wrapper.sh
RUN chmod +x /docker-entrypoint-wrapper.sh

ENTRYPOINT ["/docker-entrypoint-wrapper.sh"]
CMD ["nginx", "-g", "daemon off;"]

