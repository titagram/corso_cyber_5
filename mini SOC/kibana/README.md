# 🚀 Script Automatico Dashboard Kibana

## Script Completo Disponibile!

Ho creato uno script Python completo che crea automaticamente tutta la dashboard con un solo comando.

---

## 📋 Prerequisiti

1. **Python 3** installato
2. **Libreria requests** installata:
   ```bash
   pip3 install requests
   ```
3. **Kibana** accessibile su http://localhost:5601
4. **Data View "Security SOC"** creata (lo script ti guida)

---

## 🚀 Uso Rapido

```bash
cd "mini SOC/kibana"
python3 create_dashboard_complete.py
```

Lo script:
1. ✅ Verifica connessione a Kibana
2. ✅ Controlla se la Data View esiste (ti guida se manca)
3. ✅ Crea automaticamente 8 visualizzazioni
4. ✅ Crea la dashboard con tutti i pannelli
5. ✅ Configura i filtri interattivi
6. ✅ Ti fornisce il link diretto alla dashboard

---

## 📊 Cosa Crea Automaticamente

### Visualizzazioni (8)
1. 📈 Timeline Eventi di Sicurezza
2. 🎯 Distribuzione Tipi di Minaccia
3. 🔍 Sorgente Log (Suricata vs ModSecurity)
4. 🌐 Top IP Sorgenti
5. 📊 Codici Risposta HTTP
6. 🔗 Top URI Attaccate
7. 📋 Tabella Eventi Dettagliata
8. 🚨 Alert Suricata per Categoria

### Dashboard
- ✅ Layout ottimizzato
- ✅ 3 filtri interattivi (Tipo Minaccia, Sorgente, IP)
- ✅ Auto-refresh ogni 30 secondi
- ✅ Time range: Last 24 hours

---

## 🔧 Troubleshooting

### Errore: "Data View non trovata"
Lo script ti guida passo-passo. Crea la Data View:
- **Name**: `Security SOC`
- **Pattern**: `suricata-logs-*,modsec-logs-*`
- **Timestamp**: `@timestamp`

### Errore: "Module 'requests' not found"
```bash
pip3 install requests
```

### Errore: "Kibana non raggiungibile"
Verifica che Kibana sia avviato:
```bash
docker-compose ps kibana
```

---

## 📝 Note

- Lo script può essere eseguito più volte (aggiorna se esistente)
- Le visualizzazioni vengono create anche se la dashboard fallisce
- Puoi modificare lo script per personalizzare le visualizzazioni

---

## 🎯 Risultato

Dopo l'esecuzione, avrai:
- ✅ Dashboard completa e funzionante
- ✅ Tutte le visualizzazioni configurate
- ✅ Link diretto per accedere

**URL Dashboard**: http://localhost:5601/app/dashboards#/view/security-soc-dashboard

---

**Script**: `create_dashboard_complete.py`
**Versione**: Completa e funzionale
**Status**: ✅ Pronto all'uso

