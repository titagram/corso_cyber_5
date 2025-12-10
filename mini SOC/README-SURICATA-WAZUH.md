# 🛡️ Guida Setup Suricata + Wazuh - Mini SOC Completo

## 📋 Panoramica

- ✅ Suricata: GPL v2
- ✅ Wazuh: GPL v2
- ✅ ELK Stack: Apache 2.0

---

## 🚀 Quick Start

### 1. Avvia il Sistema Completo

```powershell
cd "mini SOC"
docker-compose up -d
```

### 2. Verifica i Servizi

```powershell
docker-compose ps
```

Dovresti vedere:
- ✅ elasticsearch
- ✅ kibana
- ✅ logstash
- ✅ filebeat
- ✅ filebeat-suricata
- ✅ suricata
- ✅ wazuh-manager
- ✅ wazuh-agent
- ✅ waf
- ✅ webapp (dvwa)
- ✅ db

---

## 🔍 Suricata IDS/IPS

### Accesso ai Log

**Log EVE JSON** (formato strutturato):
```powershell
docker exec suricata tail -f /var/log/suricata/eve.json
```

**Log Fast** (alert rapidi):
```powershell
docker exec suricata tail -f /var/log/suricata/fast.log
```

### Visualizzazione in Kibana

1. Vai su **http://localhost:5601**
2. Crea un **Data View** per `suricata-logs-*`
3. Cerca eventi con:
   ```kql
   log_source: suricata
   ```

### Test di Scansione

**Scansione TCP:**
```powershell
nmap -p 80,443,8080 localhost
```

**Scansione SYN:**
```powershell
nmap -sS -p 1-1000 localhost
```

Suricata rileverà queste scansioni e le loggherà!

---

## 🎯 Wazuh SIEM/EDR

### Accesso Wazuh Dashboard

**Wazuh Manager API:**
- URL: http://localhost:55000
- Username: `wazuh-wui`
- Password: `wazuh-wui`

**Nota**: Wazuh ha anche una dashboard web che può essere integrata con Kibana.

### File Integrity Monitoring (FIM)

Wazuh monitora automaticamente:
- `/etc`
- `/usr/bin`
- `/usr/sbin`
- `/bin`
- `/sbin`
- `/boot`

**Test FIM:**
```powershell
# Modifica un file monitorato
docker exec wazuh-agent touch /etc/test-file.txt
```

Wazuh rileverà la modifica!

### Visualizzazione Eventi

Gli eventi Wazuh vengono inviati a Elasticsearch e possono essere visualizzati in Kibana.

---

## 📊 Query Kibana Utili

### Suricata

```kql
# Tutti gli alert Suricata
log_source: suricata AND alert.signature: *

# Scansioni rilevate
log_source: suricata AND event_type: alert AND alert.category: "Attempted Information Leak"

# Attacchi HTTP
log_source: suricata AND event_type: http
```

### Wazuh

```kql
# Eventi Wazuh
log_source: wazuh

# File Integrity Monitoring
rule.id: 5503

# Rootkit detection
rule.id: 510
```

### Correlazione Multi-Sorgente

```kql
# Eventi da tutte le sorgenti per un IP
client_ip: "192.168.1.100"

# Attacchi rilevati da più sistemi
(attack_type: * OR alert.signature: *) AND (log_source: suricata OR log_source: modsecurity)
```

---

## 🧪 Scenari Didattici

### Scenario 1: Scansione Porte

1. **Esegui scansione:**
   ```powershell
   nmap -p 1-1000 localhost
   ```

2. **Verifica in Suricata:**
   ```powershell
   docker exec suricata tail -f /var/log/suricata/fast.log
   ```

3. **Visualizza in Kibana:**
   - Cerca: `log_source: suricata AND alert.signature: "Port Scan"`

### Scenario 2: Attacco HTTP

1. **Esegui attacco SQLi:**
   ```powershell
   Invoke-WebRequest "http://localhost:8080/?id=1' UNION SELECT * FROM users--"
   ```

2. **Verifica in WAF:**
   - Kibana: `log_source: modsecurity AND attack_type: "SQL Injection"`

3. **Verifica in Suricata:**
   - Kibana: `log_source: suricata AND event_type: http AND http.url: "*UNION*"`

### Scenario 3: File Integrity

1. **Modifica file monitorato:**
   ```powershell
   docker exec wazuh-agent echo "test" >> /etc/test.txt
   ```

2. **Verifica in Wazuh:**
   - Kibana: `log_source: wazuh AND rule.id: 5503`

---

## 🔧 Configurazione Avanzata

### Suricata - Aggiungere Regole Personalizzate

Modifica `suricata/rules/local.rules` e aggiungi le tue regole.

Esempio:
```suricata
alert http any any -> $HTTP_SERVERS $HTTP_PORTS (msg:"Custom Rule - Test"; content:"test"; http_uri; sid:1000100; rev:1;)
```

Riavvia Suricata:
```powershell
docker-compose restart suricata
```

### Wazuh - Modificare Monitoraggio FIM

Modifica `wazuh/agent/config/ossec.conf` nella sezione `<syscheck>`.

---

## 📚 Risorse Utili

- **Suricata Docs**: https://suricata.readthedocs.io/
- **Wazuh Docs**: https://documentation.wazuh.com/
- **ELK Stack Docs**: https://www.elastic.co/guide/

---

## ⚠️ Troubleshooting

### Suricata non rileva traffico

1. Verifica che Suricata sia in esecuzione:
   ```powershell
   docker logs suricata
   ```

2. Verifica la configurazione di rete:
   ```powershell
   docker network inspect mini-soc_soc-network
   ```

### Wazuh Agent non si connette

1. Verifica la connessione:
   ```powershell
   docker logs wazuh-agent
   ```

2. Verifica che il Manager sia raggiungibile:
   ```powershell
   docker exec wazuh-agent ping wazuh-manager
   ```

### Log non arrivano in Kibana

1. Verifica Logstash:
   ```powershell
   docker logs logstash
   ```

2. Verifica Filebeat:
   ```powershell
   docker logs filebeat-suricata
   ```

---

## 🎓 Conclusione

Ora hai un **Mini SOC Completo** con:
- ✅ **Suricata** per rilevamento rete
- ✅ **WAF** per protezione applicativa
- ✅ **Wazuh** per SIEM/EDR
- ✅ **ELK Stack** per visualizzazione

**Tutto Open Source - Nessun Abbonamento!** 🎉

