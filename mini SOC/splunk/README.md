# 📦 Splunk Enterprise - Configurazione

## 📁 File

- `Dockerfile`: Immagine Docker per Splunk
- `inputs.conf`: Configurazione input (monitor file, TCP, HEC)
- `indexes.conf`: Configurazione indici Splunk
- `props.conf`: Parsing e estrazione campi

## 🚀 Quick Start

```bash
# Avvia Splunk
docker-compose up -d splunk

# Verifica log
docker logs splunk -f

# Accedi alla Web UI
# http://localhost:8000
# Username: admin
# Password: changeme
```

## 🔧 Configurazione

### Inputs

Splunk è configurato per ricevere log da:
- File monitor: `/var/log/modsecurity/*.log`
- File monitor: `/var/log/suricata/*.json`
- TCP Input: porta 9997 (per Logstash/Filebeat)
- HTTP Event Collector: porta 8088

### Indici

- `main`: Log generali
- `security`: Log di sicurezza aggregati
- `modsecurity`: Log ModSecurity
- `suricata`: Log Suricata

## 📝 Modifiche

Dopo modifiche ai file di configurazione:
```bash
docker-compose restart splunk
```

---

**Nota**: Splunk Enterprise è trial gratuito 60 giorni per uso didattico.

