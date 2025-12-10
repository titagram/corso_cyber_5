FROM jasonish/suricata:latest

# Copia la configurazione personalizzata (versione semplificata)
COPY suricata-simple.yaml /etc/suricata/suricata.yaml
COPY rules/ /var/lib/suricata/rules/

# Crea file threshold.config vuoto
RUN touch /var/lib/suricata/rules/threshold.config || true

# Assicurati che i permessi siano corretti
USER root
RUN chmod 644 /etc/suricata/suricata.yaml && \
    chmod 644 /var/lib/suricata/rules/*.rules 2>/dev/null || true && \
    chmod 644 /var/lib/suricata/rules/threshold.config 2>/dev/null || true

USER suricata

