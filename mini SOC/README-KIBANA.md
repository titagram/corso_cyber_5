# 📊 Configurazione Kibana - Mini SOC

Guida alla configurazione di Kibana per visualizzare i log del WAF (ModSecurity).

---

## 🚀 Accesso a Kibana

Apri il browser e vai su: **http://localhost:5601**

---

## 📝 Step 1: Crea un Data View

1. Clicca sul menu **☰** (hamburger) in alto a sinistra
2. Vai su **Stack Management** (nella sezione "Management")
3. Clicca su **Data Views** (sotto "Kibana")
4. Clicca il pulsante **Create data view**
5. Compila i campi:
   - **Name:** `ModSecurity Logs`
   - **Index pattern:** `modsec-logs-*`
   - **Timestamp field:** `@timestamp`
6. Clicca **Save data view to Kibana**

---

## 🔍 Step 2: Visualizza i Log in Discover

1. Clicca sul menu **☰**
2. Vai su **Analytics** → **Discover**
3. In alto a sinistra, seleziona il data view **ModSecurity Logs**
4. Imposta il time range in alto a destra (es. "Last 15 minutes")
5. Dovresti vedere tutti i log del WAF!

### Campi utili da visualizzare

Clicca su **+ Add field** per aggiungere colonne alla tabella:

| Campo | Descrizione |
|-------|-------------|
| `transaction.client_ip` | IP del client |
| `transaction.request.uri` | URL richiesto |
| `transaction.request.method` | Metodo HTTP (GET, POST, etc.) |
| `transaction.response.http_code` | Codice risposta HTTP |
| `transaction.messages` | Messaggi/alert di ModSecurity |
| `attack_detected` | Flag attacco rilevato |

---

## 🧪 Step 3: Genera Traffico di Test

Apri PowerShell e esegui questi comandi per generare log di attacchi:

```powershell
# SQL Injection
Invoke-WebRequest "http://localhost:8080/?id=1' UNION SELECT * FROM users--" -UseBasicParsing

# Cross-Site Scripting (XSS)
Invoke-WebRequest "http://localhost:8080/?name=<script>alert(1)</script>" -UseBasicParsing

# Path Traversal
Invoke-WebRequest "http://localhost:8080/?file=../../../../etc/passwd" -UseBasicParsing

# Command Injection
Invoke-WebRequest "http://localhost:8080/?cmd=cat /etc/passwd" -UseBasicParsing

# Genera traffico multiplo
1..10 | ForEach-Object { Invoke-WebRequest "http://localhost:8080/?test=$_" -UseBasicParsing }
```

Torna su Kibana Discover e clicca **Refresh** per vedere i nuovi log.

---

## 📈 Step 4: Crea una Dashboard (Opzionale)

### Grafico: Richieste nel tempo

1. Vai su **☰** → **Analytics** → **Dashboard**
2. Clicca **Create dashboard**
3. Clicca **Create visualization**
4. Seleziona **Lens**
5. Trascina `@timestamp` sull'asse X
6. L'asse Y mostrerà automaticamente il conteggio
7. Clicca **Save and return**

### Grafico: Top Client IP

1. Nella dashboard, clicca **Create visualization**
2. Seleziona **Lens**
3. Cambia il tipo di grafico in **Pie** o **Bar horizontal**
4. Trascina `transaction.client_ip` nel campo
5. Clicca **Save and return**

### Grafico: Top URI Richiesti

1. Clicca **Create visualization**
2. Seleziona **Lens** → **Bar horizontal**
3. Trascina `transaction.request.uri.keyword` nel campo
4. Clicca **Save and return**

### Salva la Dashboard

1. Clicca **Save** in alto a destra
2. Nome: `WAF Security Dashboard`
3. Clicca **Save**

---

## 🔎 Query Utili (KQL)

Nella barra di ricerca di Discover puoi usare queste query:

```
# Tutti gli attacchi rilevati
attack_detected: "true"

# Richieste da un IP specifico
transaction.client_ip: "192.168.1.100"

# Richieste con errori (4xx, 5xx)
transaction.response.http_code >= 400

# Ricerca nel URI
transaction.request.uri: *passwd*

# Metodo POST
transaction.request.method: "POST"

# Combinazione di filtri
transaction.request.method: "POST" AND transaction.response.http_code: 403
```

---

## ⚠️ Troubleshooting

### Non vedo dati in Discover

1. **Verifica il time range** - Imposta "Last 1 hour" o "Today"
2. **Verifica che i container siano attivi:**
   ```powershell
   docker-compose ps
   ```
3. **Controlla se ci sono documenti in Elasticsearch:**
   ```powershell
   Invoke-WebRequest "http://localhost:9200/modsec-logs-*/_count" -UseBasicParsing
   ```
4. **Genera traffico di test** e attendi 10-15 secondi

### Errore "Detection engine permissions required"

Questo errore appare nella sezione **Security → Alerts**. È normale - quella sezione richiede una licenza Enterprise. Usa invece **Discover** e **Dashboard** per visualizzare i log.

### I log non arrivano in Elasticsearch

1. Verifica che il WAF stia generando log:
   ```powershell
   docker exec waf ls -la /var/log/modsecurity/
   ```
2. Controlla i log di Filebeat:
   ```powershell
   docker logs filebeat
   ```
3. Controlla i log di Logstash:
   ```powershell
   docker logs logstash
   ```

---

## 📚 Risorse Utili

- [Kibana Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [KQL (Kibana Query Language)](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)
- [ModSecurity Reference Manual](https://github.com/owasp-modsecurity/ModSecurity/wiki/Reference-Manual)
- [OWASP CRS Documentation](https://coreruleset.org/docs/)

