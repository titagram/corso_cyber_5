# Usa immagine alternativa hackinsdn/suricata invece di jasonish/suricata
# Questa immagine ha una configurazione più semplice e potrebbe evitare problemi con runmode
FROM hackinsdn/suricata:latest

# Copia la configurazione personalizzata (versione semplificata per Kali Linux)
# NOTA: Non specifichiamo runmode nel YAML, Suricata lo rileva automaticamente da -i eth0
COPY suricata-simple.yaml /etc/suricata/suricata.yaml
COPY rules/ /var/lib/suricata/rules/

# Crea file threshold.config vuoto
RUN touch /var/lib/suricata/rules/threshold.config || true

# Assicurati che i permessi siano corretti
# L'immagine hackinsdn/suricata usa root come utente di default
RUN chmod 644 /etc/suricata/suricata.yaml && \
    chmod 644 /var/lib/suricata/rules/*.rules 2>/dev/null || true && \
    chmod 644 /var/lib/suricata/rules/threshold.config 2>/dev/null || true && \
    mkdir -p /var/log/suricata && \
    chmod 755 /var/log/suricata

