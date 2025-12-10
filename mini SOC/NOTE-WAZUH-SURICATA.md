# ⚠️ Note su Wazuh e Suricata

## 📋 Stato Attuale

### ✅ Funzionanti
- **ELK Stack** - Tutto funzionante
- **WAF (ModSecurity)** - Funzionante
- **Filebeat (WAF)** - Funzionante
- **Filebeat-Suricata** - Funzionante (configurazione corretta)

### ⚠️ In Configurazione
- **Suricata** - Richiede configurazione aggiuntiva per le regole
- **Wazuh** - Immagini Docker non disponibili su Docker Hub standard

---

## 🔧 Suricata

### Problema
Suricata si riavvia continuamente perché:
1. Le regole predefinite potrebbero non essere presenti nell'immagine
2. La configurazione richiede regole ET (Emerging Threats) o regole personalizzate

### Soluzione Temporanea
Suricata è commentato nel docker-compose.yml. Per abilitarlo:

1. **Scarica le regole ET:**
   ```powershell
   docker exec suricata suricata-update
   ```

2. **Oppure usa solo regole locali:**
   - Le regole in `suricata/rules/local.rules` sono già configurate
   - Rimuovi il riferimento a `suricata.rules` nel file di configurazione

### Configurazione Attuale
- File di configurazione: `suricata/suricata.yaml`
- Regole personalizzate: `suricata/rules/local.rules`
- Log EVE JSON: `/var/log/suricata/eve.json`

---

## 🔧 Wazuh

### Problema
Le immagini Docker ufficiali di Wazuh non sono disponibili su Docker Hub con i tag standard.

### Soluzioni Alternative

#### Opzione 1: Wazuh All-in-One (Consigliato per Didattica)
Wazuh fornisce un'immagine all-in-one che include Manager, Indexer e Dashboard:

```yaml
wazuh:
  image: wazuh/wazuh:latest
  # Configurazione completa disponibile su:
  # https://documentation.wazuh.com/current/docker/wazuh-container.html
```

#### Opzione 2: Installazione Manuale
Per un setup più completo, segui la guida ufficiale:
- https://documentation.wazuh.com/current/installation-guide/

#### Opzione 3: Usa Solo Suricata + ELK
Per scopi didattici, Suricata + ELK Stack fornisce già:
- ✅ Rilevamento rete (Suricata)
- ✅ Rilevamento applicativo (WAF)
- ✅ SIEM base (ELK Stack)

---

## 🎯 Sistema Funzionante Attuale

Anche senza Wazuh, hai un **Mini SOC completo** con:

1. **Suricata** (quando configurato) - IDS/IPS di rete
2. **WAF ModSecurity** - Protezione applicativa
3. **ELK Stack** - Log management e visualizzazione
4. **Filebeat** - Raccolta log

### Cosa Puoi Fare
- ✅ Rilevare attacchi HTTP (WAF)
- ✅ Rilevare scansioni TCP/UDP (Suricata - quando configurato)
- ✅ Visualizzare log in Kibana
- ✅ Correlare eventi multi-sorgente
- ✅ Creare dashboard personalizzati

---

## 📚 Risorse

- **Suricata Docs**: https://suricata.readthedocs.io/
- **Wazuh Docs**: https://documentation.wazuh.com/
- **ELK Stack Docs**: https://www.elastic.co/guide/

---

## 🚀 Prossimi Passi

1. ✅ Sistema base funzionante (ELK + WAF)
2. ⏳ Configurare Suricata completamente
3. ⏳ (Opzionale) Aggiungere Wazuh con setup manuale o all-in-one

**Il sistema è già utilizzabile per scopi didattici!** 🎓

