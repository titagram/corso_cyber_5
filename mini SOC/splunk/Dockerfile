# Splunk Enterprise Dockerfile
# Trial gratuito 60 giorni per uso didattico
FROM splunk/splunk:latest

# Configurazione Splunk
ENV SPLUNK_START_ARGS="--accept-license"
ENV SPLUNK_PASSWORD=changeme
ENV SPLUNK_HOME=/opt/splunk
ENV SPLUNK_CMD=start

# Crea directory per log e configurazioni
USER root
RUN mkdir -p /opt/splunk/var/log/splunk/soc && \
    mkdir -p /opt/splunk/etc/system/local && \
    chown -R splunk:splunk /opt/splunk/var/log/splunk/soc && \
    chown -R splunk:splunk /opt/splunk/etc/system/local

# Copia file di configurazione (invece di montarli come read-only)
COPY inputs.conf /opt/splunk/etc/system/local/inputs.conf
COPY indexes.conf /opt/splunk/etc/system/local/indexes.conf
COPY props.conf /opt/splunk/etc/system/local/props.conf

# Imposta permessi corretti
RUN chown splunk:splunk /opt/splunk/etc/system/local/*.conf && \
    chmod 644 /opt/splunk/etc/system/local/*.conf

USER splunk

