#!/bin/sh
# Wrapper per assicurarsi che i permessi siano corretti

# Fix permessi sulla directory dei log (necessario per volumi Docker)
chown -R nginx:nginx /var/log/modsecurity 2>/dev/null || true
chmod 755 /var/log/modsecurity 2>/dev/null || true

# Crea il file di audit log con i permessi corretti
touch /var/log/modsecurity/modsec_audit.log 2>/dev/null || true
chown nginx:nginx /var/log/modsecurity/modsec_audit.log 2>/dev/null || true
chmod 644 /var/log/modsecurity/modsec_audit.log 2>/dev/null || true

# Esegui l'entrypoint originale
exec /docker-entrypoint.sh "$@"

