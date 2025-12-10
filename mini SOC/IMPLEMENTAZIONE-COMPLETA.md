# ✅ Implementazione Completa - Mini SOC con Suricata + Wazuh

## 🎉 Implementazione Completata!

Ho aggiunto **Suricata** e **Wazuh** al tuo Mini SOC didattico. **Tutto è Open Source - Nessun Abbonamento!**

---

## 📦 Cosa è Stato Aggiunto

### 1. **Suricata IDS/IPS** (Open Source - GPL v2)
- ✅ Configurazione completa (`suricata/suricata.yaml`)
- ✅ Regole personalizzate (`suricata/rules/local.rules`)
- ✅ Integrazione con Logstash
- ✅ Filebeat per raccolta log EVE JSON

### 2. **Wazuh SIEM/EDR** (Open Source - GPL v2)
- ✅ Wazuh Manager (`wazuh/manager/config/ossec.conf`)
- ✅ Wazuh Agent (`wazuh/agent/config/ossec.conf`)
- ✅ File Integrity Monitoring (FIM)
- ✅ Rootkit detection
- ✅ Vulnerability detection

### 3. **Integrazione ELK Stack**
- ✅ Logstash aggiornato per processare log Suricata
- ✅ Indici separati per ogni sorgente log
- ✅ Correlazione eventi multi-sorgente

---

## 📁 Struttura File Creata

```
mini SOC/
├── docker-compose.yml          # ⬆️ AGGIORNATO con Suricata + Wazuh
├── logstash/
│   └── logstash.conf           # ⬆️ AGGIORNATO per Suricata
├── suricata/                   # ✨ NUOVO
│   ├── suricata.yaml
│   └── rules/
│       └── local.rules
├── wazuh/                      # ✨ NUOVO
│   ├── manager/
│   │   └── config/
│   │       └── ossec.conf
│   └── agent/
│       └── config/
│           └── ossec.conf
├── filebeat/
│   └── filebeat-suricata.yml   # ✨ NUOVO
├── ARCHITETTURA-SOC.md         # ✨ NUOVO
├── SURICATA-WAZUH-SETUP.md     # ✨ NUOVO
├── README-SURICATA-WAZUH.md    # ✨ NUOVO
└── IMPLEMENTAZIONE-COMPLETA.md # ✨ NUOVO (questo file)
```

---

## 🚀 Come Avviare

### 1. Avvia Tutti i Servizi

```powershell
cd "mini SOC"
docker-compose up -d
```

### 2. Verifica i Servizi

```powershell
docker-compose ps
```

Dovresti vedere **11 servizi** in esecuzione:
1. elasticsearch
2. kibana
3. logstash
4. filebeat (WAF)
5. filebeat-suricata (Suricata)
6. suricata
7. wazuh-manager
8. wazuh-agent
9. waf
10. webapp (dvwa)
11. db

### 3. Attendi l'Avvio Completo

I servizi hanno bisogno di qualche minuto per inizializzarsi completamente, specialmente:
- Elasticsearch (30-60 secondi)
- Wazuh Manager (1-2 minuti)

---

## 🔍 Verifica Funzionamento

### Suricata

```powershell
# Verifica log Suricata
docker logs suricata

# Verifica log EVE JSON
docker exec suricata tail -f /var/log/suricata/eve.json
```

### Wazuh

```powershell
# Verifica Wazuh Manager
docker logs wazuh-manager

# Verifica Wazuh Agent
docker logs wazuh-agent

# Test API Wazuh
Invoke-WebRequest -Uri "http://localhost:55000" -Headers @{Authorization="Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("wazuh-wui:wazuh-wui"))}
```

### Kibana

1. Vai su **http://localhost:5601**
2. Crea **Data Views** per:
   - `modsec-logs-*` (WAF)
   - `suricata-logs-*` (Suricata)
   - `soc-logs-*` (generale)

---

## 🧪 Test Rapidi

### Test 1: Scansione con Nmap

```powershell
# Suricata dovrebbe rilevare questa scansione
nmap -p 80,443,8080 localhost
```

Poi verifica in Kibana:
```kql
log_source: suricata AND alert.signature: *
```

### Test 2: Attacco HTTP

```powershell
# WAF dovrebbe rilevare questo attacco
Invoke-WebRequest "http://localhost:8080/?id=1' UNION SELECT * FROM users--"
```

Poi verifica in Kibana:
```kql
log_source: modsecurity AND attack_type: "SQL Injection"
```

### Test 3: File Integrity Monitoring

```powershell
# Wazuh dovrebbe rilevare questa modifica
docker exec wazuh-agent touch /etc/test-file.txt
```

Poi verifica nei log Wazuh:
```powershell
docker logs wazuh-manager | Select-String "test-file"
```

---

## 📊 Architettura Finale

```
┌─────────────────────────────────────────────────────────┐
│                  MINI SOC COMPLETO                      │
│            Tutto Open Source - Nessun Abbonamento      │
└─────────────────────────────────────────────────────────┘

Attaccante
    │
    ├── Suricata (IDS/IPS) ──► Filebeat ──► Logstash ──► Elasticsearch
    │                                                           │
    ├── WAF (ModSecurity) ──► Filebeat ──► Logstash ──► Elasticsearch
    │                                                           │
    └── DVWA ──► Wazuh Agent ──► Wazuh Manager ──► Elasticsearch
                                                           │
                                                           ▼
                                                      ┌─────────┐
                                                      │ Kibana  │
                                                      │ (UI)    │
                                                      └─────────┘
```

---

## 🎓 Cosa Puoi Fare Ora

### Livello Rete (Suricata)
- ✅ Rilevare scansioni TCP/UDP
- ✅ Rilevare attacchi di rete
- ✅ Analizzare traffico HTTP
- ✅ Creare regole personalizzate

### Livello Applicazione (WAF)
- ✅ Rilevare attacchi HTTP (SQLi, XSS, ecc.)
- ✅ Rilevare bruteforcing
- ✅ Rilevare scanning HTTP

### Livello Endpoint (Wazuh)
- ✅ File Integrity Monitoring
- ✅ Rootkit detection
- ✅ Vulnerability detection
- ✅ Process monitoring

### Livello SIEM (ELK + Wazuh)
- ✅ Correlazione eventi multi-sorgente
- ✅ Dashboard unificati
- ✅ Analisi avanzata
- ✅ Alerting

---

## 📚 Documentazione

Consulta questi file per maggiori dettagli:

1. **ARCHITETTURA-SOC.md** - Architettura completa del sistema
2. **SURICATA-WAZUH-SETUP.md** - Perché aggiungere Suricata e Wazuh
3. **README-SURICATA-WAZUH.md** - Guida pratica all'utilizzo

---

## ⚠️ Note Importanti

### Suricata
- In Docker, Suricata monitora solo il traffico della rete Docker bridge
- Per monitorare tutto il traffico di sistema, usa `network_mode: host` (solo Linux)
- Le regole personalizzate sono in `suricata/rules/local.rules`

### Wazuh
- Wazuh Manager richiede qualche minuto per inizializzarsi
- L'integrazione completa con Elasticsearch richiede Wazuh Indexer (opzionale)
- Per semplicità didattica, Wazuh funziona standalone con log locali

### Risorse Sistema
- **RAM minima**: 8GB (16GB consigliato)
- **CPU**: 4 core
- **Storage**: 50GB liberi

---

## 🎯 Prossimi Passi

1. ✅ **Setup completato** - Tutto è pronto!
2. ⏳ **Testa i componenti** - Esegui i test rapidi sopra
3. ⏳ **Esplora Kibana** - Crea dashboard personalizzati
4. ⏳ **Crea regole custom** - Personalizza Suricata e Wazuh
5. ⏳ **Simula attacchi** - Pratica scenari reali

---

## 🎉 Conclusione

Ora hai un **Mini SOC Didattico Completo** con:

- ✅ **Suricata** - IDS/IPS di rete (Open Source)
- ✅ **WAF** - Protezione applicativa (Open Source)
- ✅ **Wazuh** - SIEM/EDR (Open Source)
- ✅ **ELK Stack** - Log management (Open Source)

**Tutto Open Source - Nessun Abbonamento Richiesto!** 🎓

Buon apprendimento! 🚀

