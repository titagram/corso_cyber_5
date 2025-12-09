FROM docker.elastic.co/beats/filebeat:8.13.0

# Copia il file di configurazione con i permessi corretti
COPY --chown=root:root filebeat.yml /usr/share/filebeat/filebeat.yml

# Imposta permessi corretti (richiesto da Filebeat)
USER root
RUN chmod 644 /usr/share/filebeat/filebeat.yml

USER filebeat

