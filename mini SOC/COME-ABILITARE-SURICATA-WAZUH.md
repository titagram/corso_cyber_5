# 🚀 Come Abilitare Suricata e Wazuh

## 📋 Situazione Attuale

Suricata e Wazuh sono **commentati** nel `docker-compose.yml` perché richiedono configurazione aggiuntiva.

---

## 🔧 Opzione 1: Abilitare Solo Suricata (Più Semplice)

### Passo 1: Decommenta Suricata nel docker-compose.yml

Apri `docker-compose.yml` e decommenta le righe 180-196:

```yaml
  ###########################################################
  # 8. Suricata IDS/IPS (Open Source - GPL v2)
  ###########################################################
  suricata:
    image: jasonish/suricata:latest
    container_name: suricata
    depends_on:
      - webapp
      - waf
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_NICE
    volumes:
      - ./suricata/suricata.yaml:/etc/suricata/suricata.yaml:ro
      - ./suricata/rules:/var/lib/suricata/rules:ro
      - suricata-logs:/var/log/suricata
    networks:
      - soc-network
    restart: unless-stopped
```

### Passo 2: Decommenta Filebeat-Suricata

Decommenta anche le righe 202-215:

```yaml
  ###########################################################
  # 9. Filebeat per Suricata (raccolta log EVE)
  ###########################################################
  filebeat-suricata:
    build:
      context: ./filebeat
      dockerfile: Dockerfile-suricata
    container_name: filebeat-suricata
    depends_on:
      - suricata
      - logstash
    user: root
    volumes:
      - suricata-logs:/var/log/suricata:ro
    networks:
      - soc-network
    restart: unless-stopped
```

### Passo 3: Configura le Regole Suricata

Il problema principale è che Suricata ha bisogno di regole. Hai due opzioni:

#### Opzione A: Usa Solo Regole Locali (Più Semplice)

Modifica `suricata/suricata.yaml` e assicurati che la sezione `rule-files` sia così:

```yaml
rule-files:
  - local.rules
  # Commenta suricata.rules se non disponibile
```

Le regole in `suricata/rules/local.rules` sono già configurate!

#### Opzione B: Scarica Regole ET (Più Completo)

1. Avvia Suricata:
   ```powershell
   docker-compose up -d suricata
   ```

2. Entra nel container:
   ```powershell
   docker exec -it suricata sh
   ```

3. Scarica le regole:
   ```bash
   suricata-update
   ```

4. Esci e riavvia:
   ```powershell
   docker-compose restart suricata
   ```

### Passo 4: Avvia Suricata

```powershell
cd "mini SOC"
docker-compose up -d suricata filebeat-suricata
```

### Verifica Funzionamento

```powershell
# Controlla lo stato
docker ps | Select-String suricata

# Controlla i log
docker logs suricata --tail 20

# Se vedi errori sulle regole, usa solo local.rules
```

---

## 🔧 Opzione 2: Abilitare Wazuh (Più Complesso)

### Problema

Le immagini Docker ufficiali di Wazuh (`wazuh/wazuh-manager:latest`) **non sono disponibili** su Docker Hub standard.

### Soluzioni

#### Soluzione A: Wazuh All-in-One (Consigliato)

Wazuh fornisce un'immagine all-in-one che include tutto:

1. **Modifica docker-compose.yml** e aggiungi:

```yaml
  wazuh:
    image: wazuh/wazuh:latest
    container_name: wazuh
    depends_on:
      - elasticsearch
    environment:
      - WAZUH_API_USERNAME=wazuh-wui
      - WAZUH_API_PASSWORD=wazuh-wui
    volumes:
      - wazuh-data:/var/ossec/data
      - wazuh-logs:/var/ossec/logs
    networks:
      - soc-network
    restart: unless-stopped
    ports:
      - "55000:55000/tcp"  # Wazuh API
```

2. **Verifica che l'immagine esista:**
   ```powershell
   docker pull wazuh/wazuh:latest
   ```

#### Soluzione B: Installazione Manuale (Più Complessa)

Segui la guida ufficiale:
- https://documentation.wazuh.com/current/installation-guide/

#### Soluzione C: Usa Solo Suricata + ELK

Per scopi didattici, **Suricata + ELK Stack** fornisce già:
- ✅ Rilevamento rete (Suricata)
- ✅ Rilevamento applicativo (WAF)
- ✅ SIEM base (ELK Stack)

---

## 🎯 Raccomandazione

### Per Iniziare Subito

1. **Abilita solo Suricata** (Opzione 1)
2. **Usa solo regole locali** (più semplice)
3. **Aggiungi Wazuh dopo** se necessario

### Sistema Attuale Funziona Benissimo

Anche **senza Suricata e Wazuh**, hai già:
- ✅ **WAF** - Rileva attacchi HTTP
- ✅ **ELK Stack** - Log management completo
- ✅ **Kibana** - Dashboard e visualizzazione

**Perfetto per scopi didattici!** 🎓

---

## 📝 Quick Start - Abilita Suricata Ora

Se vuoi abilitare Suricata subito, esegui questi comandi:

```powershell
cd "C:\Users\A502\Desktop\corso_cyber_5\mini SOC"

# 1. Modifica suricata.yaml per usare solo regole locali
# (Apri il file e verifica che rule-files contenga solo "local.rules")

# 2. Decommenta Suricata e Filebeat-Suricata nel docker-compose.yml
# (Rimuovi i # dalle righe 180-196 e 202-215)

# 3. Avvia Suricata
docker-compose up -d suricata filebeat-suricata

# 4. Verifica
docker ps | Select-String suricata
docker logs suricata --tail 20
```

---

## ⚠️ Troubleshooting

### Suricata si riavvia continuamente

**Causa**: Mancano le regole o configurazione errata

**Soluzione**:
1. Verifica che `suricata/rules/local.rules` esista
2. Usa solo `local.rules` nel file di configurazione
3. Controlla i log: `docker logs suricata`

### Wazuh immagine non trovata

**Causa**: Immagine non disponibile su Docker Hub

**Soluzione**:
1. Prova `wazuh/wazuh:latest` (all-in-one)
2. Oppure installa manualmente seguendo la guida ufficiale
3. Oppure usa solo Suricata + ELK

---

## 🎓 Conclusione

- **Suricata**: Può essere abilitato facilmente con regole locali
- **Wazuh**: Richiede setup più complesso o immagine alternativa
- **Sistema attuale**: Funziona perfettamente anche senza Suricata/Wazuh

**Vuoi che ti aiuti ad abilitare Suricata ora?** 🚀

