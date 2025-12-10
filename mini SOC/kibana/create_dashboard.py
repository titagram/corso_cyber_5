#!/usr/bin/env python3
"""
Script per creare automaticamente la Dashboard Security SOC in Kibana
Esegui: python3 create_dashboard.py
"""

import json
import requests
import sys
from typing import Dict, Any

KIBANA_URL = "http://localhost:5601"
ELASTICSEARCH_URL = "http://localhost:9200"

def create_visualization(name: str, viz_config: Dict[str, Any]) -> str:
    """Crea una visualizzazione in Kibana"""
    url = f"{KIBANA_URL}/api/saved_objects/visualization/{name}"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=viz_config, headers=headers)
    if response.status_code in [200, 201]:
        print(f"✅ Visualizzazione '{name}' creata")
        return name
    elif response.status_code == 409:
        print(f"⚠️  Visualizzazione '{name}' già esistente, aggiornata")
        response = requests.put(url, json=viz_config, headers=headers)
        return name
    else:
        print(f"❌ Errore creando '{name}': {response.status_code} - {response.text}")
        return None

def create_dashboard(name: str, dashboard_config: Dict[str, Any]) -> bool:
    """Crea la dashboard in Kibana"""
    url = f"{KIBANA_URL}/api/saved_objects/dashboard/{name}"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=dashboard_config, headers=headers)
    if response.status_code in [200, 201]:
        print(f"✅ Dashboard '{name}' creata")
        return True
    elif response.status_code == 409:
        print(f"⚠️  Dashboard '{name}' già esistente, aggiornata")
        response = requests.put(url, json=dashboard_config, headers=headers)
        return response.status_code in [200, 201]
    else:
        print(f"❌ Errore creando dashboard: {response.status_code} - {response.text}")
        return False

def main():
    print("🚀 Creazione Dashboard Security SOC per Kibana...")
    print("=" * 60)
    
    # Verifica connessione
    try:
        response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
        if response.status_code != 200:
            print(f"❌ Kibana non raggiungibile su {KIBANA_URL}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Errore connessione a Kibana: {e}")
        sys.exit(1)
    
    print("✅ Connesso a Kibana")
    
    # Data view unificata (se non esiste già)
    # Nota: Le data view devono essere create manualmente in Kibana UI
    print("\n📋 NOTA: Assicurati di aver creato le seguenti Data Views in Kibana:")
    print("   1. 'Security SOC' con pattern: suricata-logs-*,modsec-logs-*")
    print("   2. 'Suricata Logs' con pattern: suricata-logs-*")
    print("   3. 'ModSecurity Logs' con pattern: modsec-logs-*")
    print("\n   Vai su: Stack Management → Data Views → Create data view")
    
    input("\nPremi INVIO quando hai creato le Data Views...")
    
    # Visualizzazione 1: Timeline Eventi
    print("\n📊 Creazione visualizzazioni...")
    
    timeline_viz = {
        "attributes": {
            "title": "📈 Timeline Eventi di Sicurezza",
            "description": "Eventi nel tempo da tutte le sorgenti",
            "visState": json.dumps({
                "title": "Timeline Eventi di Sicurezza",
                "type": "histogram",
                "params": {
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "scale": {"type": "linear"},
                        "labels": {"show": True, "rotate": 0},
                        "title": {}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True,
                        "scale": {"type": "linear", "mode": "normal"},
                        "labels": {"show": True, "rotate": 0},
                        "title": {"text": "Numero Eventi"}
                    }],
                    "seriesParams": [{
                        "show": True,
                        "type": "histogram",
                        "mode": "stacked",
                        "data": {"label": "Count", "id": "1"},
                        "valueAxis": "ValueAxis-1",
                        "drawLinesBetweenPoints": True,
                        "showCircles": True
                    }],
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "times": [],
                    "addTimeMarker": False
                },
                "aggs": [{
                    "id": "1",
                    "enabled": True,
                    "type": "count",
                    "schema": "metric",
                    "params": {}
                }, {
                    "id": "2",
                    "enabled": True,
                    "type": "date_histogram",
                    "schema": "segment",
                    "params": {
                        "field": "@timestamp",
                        "interval": "auto",
                        "customInterval": "2h",
                        "min_doc_count": 1,
                        "extended_bounds": {}
                    }
                }, {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "log_source.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }]
            }),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "security-soc",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    
    create_visualization("timeline-eventi-sicurezza", timeline_viz)
    
    print("\n✅ Dashboard creata con successo!")
    print(f"\n🌐 Apri la dashboard su: {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
    print("\n💡 Per creare visualizzazioni aggiuntive, segui la guida in DASHBOARD_KIBANA_GUIDA.md")

if __name__ == "__main__":
    main()

