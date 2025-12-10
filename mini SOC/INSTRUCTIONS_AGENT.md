# 📝 Istruzioni per l'Agent - Fix Suricata

## 🎯 Obiettivo

Abilitare **Suricata IDS/IPS** nel Mini SOC per rilevare:
- DDoS (SYN flood, UDP flood, ICMP flood)
- Scansioni di porte TCP/UDP
- Attacchi di rete
- Correlazione con WAF per analisi completa

---

## 🖥️ Ambiente di Test

### Ambiente Attuale (Problemi Riscontrati)
- **OS**: Windows 10/11
- **Docker**: Docker Desktop per Windows
- **Problema**: Suricata non funziona correttamente su Docker Desktop Windows

### Ambiente Target (Dove Risolvere)
- **OS**: Kali Linux
- **Docker**: Docker Engine nativo Linux
- **Vantaggio**: Accesso diretto alle interfacce di rete

---

## ⚠️ Problemi Riscontrati su Windows

### Problema 1: Suricata si Riavvia Continuamente

**Sintomi**:
```
Container suricata: Restarting (1) X seconds ago
```

**Causa Root**:
- Docker Desktop su Windows usa una VM Linux sottostante
- Suricata richiede accesso diretto alle interfacce di rete (AF_PACKET)
- Windows/Docker Desktop non permette accesso diretto alle interfacce

**Errori Specifici**:
```
Error: af-packet: eth0: failed to create socket: Operation not permitted
Error: af-packet: eth0: failed to init socket for interface
Error: runmodes: The custom type "pcap" doesn't exist for this runmode type "AF_PACKET_DEV"
```

### Problema 2: Configurazione Runmode

**Errore**:
- Suricata cerca di usare `af-packet` (non funziona su Docker Windows)
- Tentativo di usare `runmode: pcap` fallisce perché il runmode di default è `AF_PACKET_DEV`

### Problema 3: Permessi File

**Warning** (non critico):
```
chown: changing ownership of '/etc/suricata/suricata.yaml': Read-only file system
```
- Non è critico, ma indica problemi con volumi read-only

---

## 🔧 Cosa Abbiamo Fatto per Risolvere

### Tentativo 1: Configurazione Base
- ✅ Abilitato Suricata nel `docker-compose.yml`
- ✅ Creato configurazione `suricata/suricata.yaml`
- ✅ Aggiunto regole DDoS in `suricata/rules/local.rules`
- ❌ **Risultato**: Suricata si riavvia continuamente

### Tentativo 2: Modifica Runmode
- ✅ Cambiato `runmode: autofp` → `runmode: pcap`
- ✅ Configurato sezione `pcap:` invece di `af-packet:`
- ❌ **Risultato**: Errore "pcap doesn't exist for AF_PACKET_DEV"

### Tentativo 3: Dockerfile Personalizzato
- ✅ Creato `suricata/Dockerfile` per build custom
- ✅ Copiato configurazione durante build
- ✅ Impostato permessi corretti
- ❌ **Risultato**: Stesso problema con runmode

### Tentativo 4: Comando Esplicito
- ✅ Aggiunto `entrypoint` e `command` espliciti nel docker-compose.yml
- ✅ Specificato `-i eth0` e `-S local.rules`
- ❌ **Risultato**: Stesso problema con permessi AF_PACKET

### Tentativo 5: Configurazione Semplificata
- ✅ Creato `suricata-simple.yaml` con configurazione minimale
- ✅ Rimosso riferimenti a `suricata.rules` (non presente)
- ✅ Creato `threshold.config` vuoto
- ❌ **Risultato**: Problema persiste (limite Docker Desktop Windows)

---

## 📋 Stato Attuale

### ✅ Funzionante
- **WAF (ModSecurity)**: ✅ Funziona perfettamente
- **ELK Stack**: ✅ Funziona perfettamente
- **Filebeat**: ✅ Funziona perfettamente
- **Logstash**: ✅ Processa log WAF correttamente
- **Kibana**: ✅ Visualizza log correttamente

### ⚠️ Parzialmente Funzionante
- **Suricata**: ❌ Si riavvia continuamente su Windows
- **Filebeat-Suricata**: ✅ Configurazione corretta, ma non riceve log (Suricata non funziona)

### 📁 File Creati/Modificati
- ✅ `docker-compose.yml` - Suricata abilitato (righe 175-197)
- ✅ `suricata/suricata.yaml` - Configurazione completa
- ✅ `suricata/suricata-simple.yaml` - Configurazione semplificata
- ✅ `suricata/rules/local.rules` - Regole DDoS e scanning
- ✅ `suricata/Dockerfile` - Build custom
- ✅ `filebeat/filebeat-suricata.yml` - Configurazione Filebeat
- ✅ `filebeat/Dockerfile-suricata` - Build Filebeat custom
- ✅ `logstash/logstash.conf` - Aggiornato per processare log Suricata

---

## 🐧 Cosa Fare su Kali Linux

### Step 1: Verifica Ambiente

```bash
# Verifica Docker
docker --version
docker-compose --version

# Verifica che Docker sia in esecuzione
sudo systemctl status docker

# Verifica interfacce di rete disponibili
ip addr show
```

### Step 2: Clona/Accedi al Progetto

```bash
cd /path/to/mini\ SOC
```

### Step 3: Verifica Configurazione Suricata

**File da verificare**:
- `suricata/suricata.yaml` o `suricata/suricata-simple.yaml`
- `suricata/rules/local.rules` (deve esistere)
- `suricata/Dockerfile`

**Configurazione Consigliata per Kali Linux**:

Nel file `suricata.yaml`, usa:
```yaml
runmode: autofp

af-packet:
  - interface: eth0  # o l'interfaccia corretta su Kali
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes
```

**OPPURE** se af-packet non funziona:
```yaml
runmode: pcap

pcap:
  - interface: eth0
    checksum-checks: auto
```

### Step 4: Avvia Suricata

```bash
# Build dell'immagine custom (se necessario)
docker-compose build suricata

# Avvia Suricata
docker-compose up -d suricata filebeat-suricata

# Verifica stato
docker-compose ps suricata

# Controlla log
docker logs suricata --tail 50
```

### Step 5: Verifica Funzionamento

**Cosa cercare nei log**:
```
✅ "13 rules successfully loaded" - Regole caricate
✅ "eve-log output device initialized" - Log EVE attivo
✅ "Suricata version X.X.X RELEASE running" - Versione e stato
✅ Nessun errore "Operation not permitted"
✅ Nessun errore "failed to create socket"
```

**Se vedi errori**:
- `Operation not permitted` → Verifica `cap_add` nel docker-compose.yml
- `interface not found` → Verifica nome interfaccia (`ip addr show`)
- `rules not found` → Verifica che `local.rules` esista

### Step 6: Test DDoS

```bash
# Da un altro terminale, esegui scansione
nmap -p 80,443,8080 localhost

# Oppure SYN scan
nmap -sS -p 1-1000 localhost

# Verifica log Suricata
docker logs suricata --tail 20

# Verifica log EVE JSON
docker exec suricata tail -f /var/log/suricata/eve.json
```

### Step 7: Verifica in Kibana

1. Vai su http://localhost:5601
2. Crea Data View per `suricata-logs-*`
3. Cerca eventi:
   ```kql
   log_source: suricata AND alert.signature: *
   ```

---

## 🔍 Troubleshooting su Kali Linux

### Problema: Suricata non vede traffico

**Possibili cause**:
1. Interfaccia sbagliata → Verifica con `ip addr show`
2. Suricata monitora solo traffico Docker → Normale, non vede traffico esterno
3. Permessi insufficienti → Verifica `cap_add` nel docker-compose.yml

**Soluzione**:
```bash
# Verifica interfacce
ip addr show

# Modifica suricata.yaml con interfaccia corretta
# Oppure usa network_mode: host (solo se necessario)
```

### Problema: Regole non caricate

**Verifica**:
```bash
# Controlla che il file esista
docker exec suricata ls -la /var/lib/suricata/rules/

# Controlla contenuto
docker exec suricata cat /var/lib/suricata/rules/local.rules
```

### Problema: Log non arrivano in Elasticsearch

**Verifica pipeline**:
1. Suricata → Filebeat → Logstash → Elasticsearch
2. Controlla ogni componente:
   ```bash
   docker logs filebeat-suricata
   docker logs logstash
   ```

---

## 📝 Note Importanti

### Limitazioni Docker (anche su Kali)

1. **Traffico Solo tra Container**:
   - Suricata in Docker vede solo traffico della rete Docker bridge
   - Non vede traffico esterno (es. scansioni da host Kali)
   - Per vedere tutto il traffico: usa `network_mode: host` (solo Linux)

2. **Network Mode Host** (Opzionale su Kali):
   ```yaml
   suricata:
     network_mode: host  # Vede tutto il traffico di sistema
     # Rimuovi networks: e ports: quando usi host mode
   ```
   ⚠️ **Attenzione**: Con `host` mode, Suricata vede TUTTO il traffico di sistema

### Configurazione Consigliata per Kali

**Opzione A: Docker Bridge (Sicura)**
- Suricata vede solo traffico tra container
- Perfetto per test interni
- Configurazione attuale va bene

**Opzione B: Host Mode (Completa)**
- Suricata vede tutto il traffico di sistema
- Richiede modifiche al docker-compose.yml
- Più potente ma più invasivo

---

## ✅ Checklist per Kali Linux

- [ ] Docker installato e funzionante
- [ ] Interfaccia di rete identificata (`eth0` o altro)
- [ ] File `suricata/rules/local.rules` presente
- [ ] Configurazione `suricata.yaml` corretta
- [ ] `docker-compose.yml` con Suricata abilitato
- [ ] Build immagine custom completata
- [ ] Suricata avviato senza errori
- [ ] Log EVE JSON generati
- [ ] Filebeat-Suricata riceve log
- [ ] Logstash processa log Suricata
- [ ] Elasticsearch indicizza log
- [ ] Kibana visualizza log Suricata
- [ ] Test DDoS funzionanti

---

## 🎯 Obiettivo Finale

Una volta funzionante su Kali, dovresti avere:

1. **Suricata** che rileva:
   - ✅ SYN Flood (DDoS)
   - ✅ UDP Flood (DDoS)
   - ✅ ICMP Flood (DDoS)
   - ✅ Port Scans
   - ✅ Nmap scans

2. **WAF** che rileva:
   - ✅ SQL Injection
   - ✅ XSS
   - ✅ Brute Force
   - ✅ HTTP Scanning

3. **ELK Stack** che:
   - ✅ Raccoglie log da entrambi
   - ✅ Processa e arricchisce
   - ✅ Visualizza in Kibana

4. **Correlazione**:
   - ✅ Eventi multi-sorgente
   - ✅ Analisi completa attacchi

---

## 📚 File di Riferimento

- `TEST-DDOS.md` - Guida test DDoS
- `RISPOSTA-DDOS.md` - Perché serve Suricata
- `README-SURICATA-WAZUH.md` - Guida generale
- `suricata/rules/local.rules` - Regole DDoS configurate

---

## 🚀 Prossimi Passi su Kali

1. **Verifica ambiente** (Docker, interfacce)
2. **Test configurazione** (avvia Suricata)
3. **Verifica log** (controlla che funzioni)
4. **Test DDoS** (esegui scansioni)
5. **Verifica Kibana** (visualizza eventi)
6. **Documenta risultati** (cosa funziona/non funziona)

---

**Data Creazione**: 2025-12-10
**Ambiente Test**: Windows 10/11 + Docker Desktop
**Ambiente Target**: Kali Linux + Docker Engine
**Status**: Suricata da sistemare su Kali Linux

