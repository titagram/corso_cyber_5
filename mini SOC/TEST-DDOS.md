# 🎯 Guida Test DDoS - Mini SOC Didattico

## 📋 Perché Serve Suricata per DDoS?

### Differenza WAF vs Suricata

| Componente | Livello | Cosa Rileva |
|-----------|---------|-------------|
| **WAF (ModSecurity)** | Applicazione (Layer 7) | Solo attacchi HTTP/HTTPS |
| **Suricata** | Rete (Layer 3-4) | DDoS, scansioni, attacchi TCP/UDP/ICMP |

**Per intercettare DDoS serve Suricata!** Il WAF non può vedere attacchi a livello di rete.

---

## 🚀 Setup Suricata per DDoS Detection

### 1. Verifica che Suricata sia Abilitato

```powershell
cd "mini SOC"
docker-compose ps | Select-String suricata
```

Se non vedi Suricata, abilitalo nel `docker-compose.yml` (già fatto!).

### 2. Avvia Suricata

```powershell
docker-compose up -d suricata filebeat-suricata
```

### 3. Verifica Funzionamento

```powershell
# Controlla i log
docker logs suricata --tail 20

# Verifica che stia monitorando
docker exec suricata suricatasc -c "uptime"
```

---

## 🧪 Test DDoS - Scenari Didattici

### ⚠️ ATTENZIONE
Questi test sono per **scopi didattici** su un ambiente controllato. **NON usare su sistemi di produzione o senza autorizzazione!**

---

### Test 1: SYN Flood (DDoS TCP)

**Cosa fa**: Inonda il target con richieste SYN TCP senza completare l'handshake.

**Come testare** (da un altro terminale):

```powershell
# Usa hping3 (se disponibile) o PowerShell
# Esempio con hping3:
hping3 -S -p 8080 --flood localhost

# Oppure con script PowerShell (simula molte connessioni):
1..1000 | ForEach-Object -Parallel {
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", 8080)
        Start-Sleep -Milliseconds 10
        $tcpClient.Close()
    } catch {}
} -ThrottleLimit 100
```

**Cosa vedrai in Suricata**:
```json
{
  "timestamp": "2025-12-10T...",
  "event_type": "alert",
  "alert": {
    "action": "allowed",
    "gid": 1,
    "signature_id": 1000003,
    "rev": 1,
    "signature": "SURICATA Possible SYN Flood DDoS Attack",
    "category": "Attempted Denial of Service",
    "severity": 1
  },
  "src_ip": "172.x.x.x",
  "dest_ip": "172.x.x.x",
  "proto": "TCP"
}
```

**Visualizza in Kibana**:
```kql
log_source: suricata AND alert.signature: "*SYN Flood*"
```

---

### Test 2: Port Scan (Reconnaissance)

**Cosa fa**: Scansiona molte porte per trovare servizi aperti.

**Come testare**:

```powershell
# Con nmap
nmap -p 1-1000 localhost

# Oppure con PowerShell
1..1000 | ForEach-Object {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    try {
        $tcpClient.Connect("localhost", $_)
        Write-Host "Porta $_ aperta"
        $tcpClient.Close()
    } catch {
        # Porta chiusa
    }
}
```

**Cosa vedrai**:
- Alert: "SURICATA Port Scan Detected"
- Alert: "SURICATA Nmap Scan Detected"

---

### Test 3: HTTP Flood (DDoS Layer 7)

**Cosa fa**: Inonda il server con molte richieste HTTP.

**Come testare**:

```powershell
# PowerShell - molte richieste HTTP simultanee
1..1000 | ForEach-Object -Parallel {
    try {
        Invoke-WebRequest -Uri "http://localhost:8080/" -UseBasicParsing -TimeoutSec 1
    } catch {}
} -ThrottleLimit 100
```

**Cosa vedrai**:
- **WAF**: Rileverà il traffico HTTP anomalo
- **Suricata**: Rileverà il high connection rate

---

### Test 4: UDP Flood

**Cosa fa**: Inonda con pacchetti UDP.

**Come testare** (richiede strumenti avanzati):

```bash
# Con hping3
hping3 --udp -p 53 --flood localhost

# Con nping (Nmap)
nping --udp -p 53 --rate 1000 localhost
```

**Cosa vedrai**:
- Alert: "SURICATA Possible UDP Flood DDoS Attack"

---

## 📊 Visualizzazione in Kibana

### Dashboard DDoS

1. **Vai su Kibana**: http://localhost:5601
2. **Crea Data View** per `suricata-logs-*`
3. **Crea Visualizzazioni**:

#### Grafico: Alert DDoS nel Tempo
- Tipo: Line Chart
- X-axis: `@timestamp`
- Y-axis: Count
- Filter: `alert.signature: "*DDoS*" OR alert.signature: "*Flood*"`

#### Tabella: Top IP Attaccanti
- Tipo: Data Table
- Rows: `src_ip`
- Metric: Count
- Filter: `alert.category: "Attempted Denial of Service"`

#### Mappa: Origine Attacchi
- Tipo: Coordinate Map
- Geo-point: `geoip.location` (se disponibile)
- Filter: `alert.signature: "*DDoS*"`

---

## 🔍 Query Kibana Utili

### Tutti gli Alert DDoS
```kql
log_source: suricata AND (alert.signature: "*Flood*" OR alert.signature: "*DDoS*")
```

### SYN Flood Specifico
```kql
log_source: suricata AND alert.signature: "*SYN Flood*"
```

### Top 10 IP Attaccanti
```kql
log_source: suricata AND alert.category: "Attempted Denial of Service"
```
Poi usa aggregazione su `src_ip`.

### Correlazione WAF + Suricata
```kql
(client_ip: "192.168.1.100" AND log_source: modsecurity) OR 
(src_ip: "192.168.1.100" AND log_source: suricata)
```

---

## 🎓 Scenari Didattici Completi

### Scenario 1: Attacco Multi-Livello

1. **Attaccante esegue scansione porte** → Suricata rileva
2. **Attaccante trova porta 8080 aperta**
3. **Attaccante esegue SYN flood** → Suricata rileva DDoS
4. **Attaccante esegue HTTP flood** → WAF + Suricata rilevano

**Correlazione in Kibana**:
```kql
src_ip: "ATTACKER_IP" OR client_ip: "ATTACKER_IP"
```

### Scenario 2: Analisi Timeline

1. Visualizza eventi in ordine temporale
2. Identifica pattern:
   - Prima: Port scan
   - Poi: SYN flood
   - Infine: HTTP flood

---

## 📈 Metriche da Monitorare

### Suricata Dashboard

- **Alert per tipo**: DDoS, Port Scan, etc.
- **Traffico sospetto**: Connessioni anomale
- **Top IP attaccanti**: Chi sta attaccando
- **Porte target**: Quali porte sono sotto attacco

---

## ⚠️ Note Importanti

1. **Ambiente Controllato**: Questi test sono solo per scopi didattici
2. **Performance**: DDoS test possono rallentare il sistema
3. **Limiti**: Suricata in Docker ha limitazioni rispetto a installazione nativa
4. **Regole**: Le regole in `local.rules` sono configurabili

---

## 🔧 Personalizzazione Regole DDoS

Modifica `suricata/rules/local.rules` per cambiare le soglie:

```suricata
# Più sensibile (rileva 50 SYN in 1 secondo invece di 100)
alert tcp any any -> $HOME_NET any (msg:"SURICATA SYN Flood"; flags:S; threshold: type both, track by_dst, count 50, seconds 1; classtype:attempted-dos; sid:1000003; rev:1;)
```

Poi riavvia Suricata:
```powershell
docker-compose restart suricata
```

---

## 🎯 Conclusione

Con **Suricata abilitato**, puoi ora:
- ✅ Rilevare DDoS (SYN flood, UDP flood, ICMP flood)
- ✅ Rilevare scansioni di porte
- ✅ Correlare eventi rete + applicazione
- ✅ Mostrare attacchi multi-livello

**Perfetto per scopi didattici!** 🎓

