#!/bin/bash
# Script per creare dashboard Splunk via API
# NOTA: Richiede che Splunk sia completamente avviato

SPLUNK_URL="http://localhost:8000"
SPLUNK_USER="admin"
SPLUNK_PASS="changeme"

echo "🔧 Creazione Dashboard Splunk via API..."
echo "=========================================="

# Login e ottieni token
echo "📝 Login a Splunk..."
SESSION_KEY=$(curl -s -k -u "${SPLUNK_USER}:${SPLUNK_PASS}" \
  "${SPLUNK_URL}/services/auth/login" \
  -d "username=${SPLUNK_USER}&password=${SPLUNK_PASS}" | \
  grep -oP '(?<=<sessionKey>)[^<]+')

if [ -z "$SESSION_KEY" ]; then
    echo "❌ Errore: Impossibile ottenere session key"
    echo "   Verifica che Splunk sia avviato: docker-compose ps splunk"
    exit 1
fi

echo "✅ Login riuscito"

# Crea dashboard XML
DASHBOARD_XML='<?xml version="1.0" encoding="UTF-8"?>
<dashboard>
  <label>Security SOC Dashboard</label>
  <description>Dashboard completa per analisi sicurezza: Suricata IDS + ModSecurity WAF</description>
  <row>
    <panel>
      <title>Timeline Eventi di Sicurezza</title>
      <chart>
        <search>
          <query>index=main OR index=security OR index=modsecurity OR index=suricata | timechart span=1h count by log_source</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
        <option name="charting.chart">line</option>
        <option name="charting.legend.placement">right</option>
      </chart>
    </panel>
    <panel>
      <title>Distribuzione Tipi di Minaccia</title>
      <chart>
        <search>
          <query>index=main OR index=security | stats count by attack_type | sort -count</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
        <option name="charting.chart">pie</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>Top IP Sorgenti</title>
      <chart>
        <search>
          <query>index=main OR index=security | stats count by client_ip | sort -count | head 10</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
        <option name="charting.chart">column</option>
      </chart>
    </panel>
    <panel>
      <title>Top URI Attaccate</title>
      <chart>
        <search>
          <query>index=modsecurity OR index=security | stats count by request_uri | sort -count | head 10</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
        <option name="charting.chart">column</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>Alert Suricata</title>
      <table>
        <search>
          <query>index=suricata OR index=security sourcetype=suricata_eve | stats count by alert.signature, src_ip | sort -count</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
      </table>
    </panel>
  </row>
</dashboard>'

# Crea dashboard
echo "📊 Creazione dashboard..."
RESPONSE=$(curl -s -k -X POST \
  "${SPLUNK_URL}/servicesNS/admin/search/data/ui/views" \
  -H "X-Splunk-Session: ${SESSION_KEY}" \
  -d "name=security_soc_dashboard" \
  -d "eai:data=${DASHBOARD_XML}")

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Dashboard creata con successo!"
    echo ""
    echo "🌐 Accedi alla dashboard:"
    echo "   ${SPLUNK_URL}/app/search/dashboards/security_soc_dashboard"
else
    echo "⚠️  Dashboard potrebbe essere già esistente o errore nella creazione"
    echo "   Risposta: ${RESPONSE}"
    echo ""
    echo "💡 Crea la dashboard manualmente tramite Web UI:"
    echo "   1. Vai su: ${SPLUNK_URL}"
    echo "   2. Dashboards → Create New Dashboard"
    echo "   3. Segui la guida in splunk/DASHBOARD_SPLUNK.md"
fi

