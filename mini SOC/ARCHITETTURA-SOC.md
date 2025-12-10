# 🛡️ Architettura Mini SOC Didattico Completo

## 📊 Panoramica Architettura

Questo documento descrive l'architettura proposta per trasformare il sistema attuale in un **Mini SOC (Security Operations Center) Didattico Completo**.

---

## 🎯 Obiettivi del Mini SOC

1. **Apprendimento pratico** di tecnologie SOC reali
2. **Copertura completa** dei livelli di sicurezza:
   - **Rete** (Suricata IDS/IPS)
   - **Applicazione** (ModSecurity WAF)
   - **Endpoint** (Wazuh EDR)
   - **SIEM** (ELK Stack + Wazuh)
3. **Simulazione realistica** di attacchi e rilevamento

---

## 🏗️ Architettura Attuale vs Proposta

### ✅ Componenti Attuali

| Componente | Funzione | Livello |
|-----------|----------|---------|
| **DVWA** | Applicazione vulnerabile (target) | Applicazione |
| **ModSecurity WAF** | Protezione applicativa HTTP | Applicazione |
| **ELK Stack** | Log management e visualizzazione | SIEM Base |
| **Filebeat** | Raccolta log WAF | Collector |
| **Logstash** | Processamento e arricchimento log | Pipeline |
| **Elasticsearch** | Storage e ricerca log | Database |
| **Kibana** | Dashboard e visualizzazione | UI |

### 🆕 Componenti da Aggiungere

| Componente | Funzione | Livello | Beneficio Didattico |
|-----------|----------|---------|---------------------|
| **Suricata** | IDS/IPS di rete | Rete | Rileva scansioni TCP/UDP, attacchi di rete |
| **Wazuh Manager** | SIEM avanzato + correlazione | SIEM | Correlazione eventi, regole avanzate |
| **Wazuh Agent** | EDR + FIM + monitoraggio | Endpoint | Monitoraggio endpoint, integrità file |
| **Filebeat (Suricata)** | Raccolta log Suricata | Collector | Integrazione log IDS |

---

## 🔄 Flusso Dati Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    MINI SOC ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   Attacker  │
└──────┬──────┘
       │
       ├──────────────────────────────────────────────┐
       │                                              │
       ▼                                              ▼
┌──────────────┐                              ┌──────────────┐
│   Suricata   │                              │   ModSecurity│
│   (IDS/IPS) │                              │     (WAF)    │
│              │                              │              │
│ • Scansioni  │                              │ • Attacchi   │
│   TCP/UDP    │                              │   HTTP       │
│ • Attacchi   │                              │ • SQLi, XSS   │
│   di rete    │                              │ • Brute Force│
└──────┬───────┘                              └──────┬───────┘
       │                                              │
       │ EVE JSON                                    │ JSON Logs
       │                                              │
       ▼                                              ▼
┌──────────────┐                              ┌──────────────┐
│   Filebeat   │                              │   Filebeat   │
│  (Suricata)  │                              │    (WAF)     │
└──────┬───────┘                              └──────┬───────┘
       │                                              │
       └──────────────┬───────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │   Logstash   │
              │   Pipeline   │
              │              │
              │ • Parse      │
              │ • Enrich     │
              │ • Correlate  │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Elasticsearch│
              │   (Storage)  │
              └──────┬───────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Kibana  │ │ Wazuh   │ │ Wazuh   │
    │(Dashboard│ │ Manager │ │ Agent   │
    │   UI)   │ │ (SIEM)  │ │  (EDR)  │
    └─────────┘ └─────────┘ └─────────┘
         │           │           │
         └───────────┴───────────┘
                     │
                     ▼
              ┌──────────────┐
              │   Analyst    │
              │  (Studente)  │
              └──────────────┘

┌──────────────┐
│     DVWA     │◄─── Target (vulnerabile)
│  (Web App)   │
└──────────────┘
```

---

## 🎓 Cosa Imparerai con Questa Architettura

### 1. **Suricata IDS/IPS** (Livello Rete)
- ✅ Rilevamento scansioni porte TCP/UDP
- ✅ Rilevamento attacchi di rete (DDoS, port scanning)
- ✅ Analisi traffico con regole personalizzate
- ✅ Integrazione log EVE con ELK Stack

### 2. **Wazuh SIEM** (Correlazione e Analisi)
- ✅ Correlazione eventi multi-sorgente
- ✅ Regole di sicurezza avanzate
- ✅ Alerting automatico
- ✅ Compliance monitoring (PCI-DSS, GDPR, ecc.)

### 3. **Wazuh EDR** (Endpoint Detection & Response)
- ✅ File Integrity Monitoring (FIM)
- ✅ Monitoraggio processi sospetti
- ✅ Rilevamento rootkit
- ✅ Log analysis avanzata

### 4. **Integrazione Completa**
- ✅ Correlazione eventi tra WAF, IDS e EDR
- ✅ Dashboard unificati
- ✅ Workflow di analisi completo

---

## 📋 Stack Tecnologico Completo

### Livello Rete
- **Suricata** 7.x - IDS/IPS open-source
- **EVE JSON** - Formato log strutturato

### Livello Applicazione
- **ModSecurity** + **OWASP CRS** - WAF
- **Nginx** - Reverse proxy

### Livello SIEM
- **Elasticsearch** 8.x - Database NoSQL
- **Logstash** 8.x - Pipeline dati
- **Kibana** 8.x - Visualizzazione
- **Wazuh** 4.x - SIEM avanzato

### Livello Endpoint
- **Wazuh Agent** - Monitoraggio endpoint
- **Filebeat** - Raccolta log

### Target Didattico
- **DVWA** - Applicazione vulnerabile
- **MariaDB** - Database

---

## 🚀 Vantaggi Didattici

### 1. **Copertura Completa**
- **Rete**: Suricata rileva attacchi a livello di rete
- **Applicazione**: WAF rileva attacchi HTTP
- **Endpoint**: Wazuh monitora il sistema

### 2. **Scenari Realistici**
- Scansioni nmap → Rilevate da Suricata
- Attacchi SQLi → Rilevati da WAF
- Modifiche file → Rilevate da Wazuh FIM
- Correlazione → Wazuh correla eventi multipli

### 3. **Skills Pratiche**
- Analisi log multi-sorgente
- Correlazione eventi
- Creazione regole personalizzate
- Dashboard e visualizzazioni

---

## 📊 Metriche e KPI

Con questa architettura potrai monitorare:

- **Attacchi di rete** (Suricata)
- **Attacchi applicativi** (WAF)
- **Anomalie endpoint** (Wazuh)
- **Tentativi di accesso** (tutti)
- **Scansioni** (Suricata + WAF)
- **Modifiche file** (Wazuh FIM)
- **Compliance** (Wazuh)

---

## 🔧 Requisiti Sistema

### Minimo Consigliato
- **RAM**: 8GB (16GB consigliato)
- **CPU**: 4 core
- **Storage**: 50GB liberi
- **OS**: Linux (Ubuntu/Debian) o Docker Desktop su Windows/Mac

### Note
- Suricata richiede accesso alla rete (promiscuous mode)
- Wazuh può essere resource-intensive
- Elasticsearch richiede memoria dedicata

---

## 📚 Prossimi Passi

1. ✅ **Analisi architettura** (questo documento)
2. ⏳ **Setup Suricata** (configurazione IDS/IPS)
3. ⏳ **Setup Wazuh** (Manager + Agent)
4. ⏳ **Integrazione Logstash** (pipeline per Suricata)
5. ⏳ **Dashboard Kibana** (visualizzazioni unificate)
6. ⏳ **Documentazione** (guide pratiche)

---

## 🎯 Conclusione

Questa architettura trasforma il sistema attuale in un **vero Mini SOC didattico** che copre:
- ✅ **Rete** (Suricata)
- ✅ **Applicazione** (WAF)
- ✅ **Endpoint** (Wazuh)
- ✅ **SIEM** (ELK + Wazuh)

**Perfetto per apprendere tecnologie SOC reali in un ambiente controllato!** 🎓

