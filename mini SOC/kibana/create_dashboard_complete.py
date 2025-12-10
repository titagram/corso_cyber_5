#!/usr/bin/env python3
"""
Script completo per creare automaticamente la Dashboard Security SOC in Kibana
Crea tutte le visualizzazioni e la dashboard con un solo comando.

Uso: python3 create_dashboard_complete.py
"""

import json
import requests
import sys
import time
from typing import Dict, Any, Optional

KIBANA_URL = "http://localhost:5601"
ELASTICSEARCH_URL = "http://localhost:9200"

class KibanaDashboardCreator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        })
        self.created_vizs = []
        
    def check_connection(self) -> bool:
        """Verifica connessione a Kibana"""
        try:
            response = self.session.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                print("✅ Connesso a Kibana")
                return True
            else:
                print(f"❌ Kibana non raggiungibile: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def check_data_view(self, name: str) -> bool:
        """Verifica se una data view esiste"""
        try:
            url = f"{KIBANA_URL}/api/data_views/data_view/{name}"
            response = self.session.get(url)
            return response.status_code == 200
        except:
            return False
    
    def create_data_view(self, name: str, pattern: str, time_field: str = "@timestamp") -> bool:
        """Crea una data view se non esiste"""
        if self.check_data_view(name):
            print(f"✅ Data View '{name}' già esistente")
            return True
        
        try:
            # API corretta per Kibana 8.x
            url = f"{KIBANA_URL}/api/data_views/data_view"
            body = {
                "data_view": {
                    "title": name,
                    "name": name,
                    "timeFieldName": time_field
                },
                "override": False
            }
            
            response = self.session.post(url, json=body)
            
            if response.status_code in [200, 201]:
                print(f"✅ Data View '{name}' creata")
                # Ora aggiungi il pattern
                try:
                    url_pattern = f"{KIBANA_URL}/api/data_views/data_view/{name}"
                    body_pattern = {
                        "data_view": {
                            "title": name,
                            "name": name,
                            "timeFieldName": time_field,
                            "sourceFilters": []
                        }
                    }
                    # Aggiorna con il pattern
                    self.session.put(url_pattern, json=body_pattern)
                except:
                    pass
                return True
            else:
                # Prova metodo alternativo con index pattern
                try:
                    url_alt = f"{KIBANA_URL}/api/saved_objects/index-pattern"
                    body_alt = {
                        "attributes": {
                            "title": pattern,
                            "timeFieldName": time_field
                        }
                    }
                    response_alt = self.session.post(url_alt, json=body_alt)
                    if response_alt.status_code in [200, 201]:
                        print(f"✅ Data View '{name}' creata (come index-pattern)")
                        return True
                except:
                    pass
                
                print(f"⚠️  Impossibile creare Data View automaticamente: {response.status_code}")
                if response.status_code != 404:
                    print(f"   Risposta: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"⚠️  Errore creando Data View: {e}")
            return False
    
    def create_or_update_saved_object(self, obj_type: str, obj_id: str, attributes: Dict[str, Any], references: list = None) -> bool:
        """Crea o aggiorna un saved object"""
        url = f"{KIBANA_URL}/api/saved_objects/{obj_type}/{obj_id}"
        
        body = {
            "attributes": attributes
        }
        if references:
            body["references"] = references
        
        try:
            response = self.session.post(url, json=body)
            if response.status_code in [200, 201]:
                return True
            elif response.status_code == 409:
                # Esiste già, aggiorna
                response = self.session.put(url, json=body)
                return response.status_code in [200, 201]
            else:
                print(f"   ⚠️  Errore: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            return False
    
    def create_visualization(self, viz_id: str, title: str, vis_state: Dict, search_source: Dict) -> bool:
        """Crea una visualizzazione"""
        # Per Kibana 8.x, NON usiamo kibanaSavedObjectMeta ma references alla Data View
        attributes = {
            "title": title,
            "visState": json.dumps(vis_state),
            "uiStateJSON": "{}"
            # NON includiamo kibanaSavedObjectMeta - Kibana 8.x usa references
        }
        
        # Ottieni l'ID della Data View dal search_source
        data_view_id = search_source.get("index")
        references = []
        if data_view_id:
            references.append({
                "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
                "type": "index-pattern",
                "id": data_view_id
            })
        
        if self.create_or_update_saved_object("visualization", viz_id, attributes, references):
            self.created_vizs.append(viz_id)
            print(f"   ✅ '{title}' creata")
            return True
        else:
            print(f"   ❌ Errore creando '{title}'")
            return False
    
    def create_timeline_viz(self) -> bool:
        """Timeline Eventi di Sicurezza"""
        vis_state = {
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
                    "labels": {"show": True}
                }],
                "valueAxes": [{
                    "id": "ValueAxis-1",
                    "type": "value",
                    "position": "left",
                    "show": True,
                    "scale": {"type": "linear"}
                }],
                "seriesParams": [{
                    "show": True,
                    "type": "histogram",
                    "mode": "stacked",
                    "data": {"label": "Count", "id": "1"},
                    "valueAxis": "ValueAxis-1"
                }],
                "addTooltip": True,
                "addLegend": True,
                "legendPosition": "right"
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "date_histogram",
                    "schema": "segment",
                    "params": {
                        "field": "@timestamp",
                        "interval": "auto",
                        "min_doc_count": 1
                    }
                },
                {
                    "id": "3",
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "log_source.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {"match_all": {}},
            "filter": []
        }
        
        return self.create_visualization(
            "timeline-eventi-sicurezza",
            "📈 Timeline Eventi di Sicurezza",
            vis_state,
            search_source
        )
    
    def create_attack_types_viz(self) -> bool:
        """Distribuzione Tipi di Minaccia"""
        vis_state = {
            "title": "Distribuzione Tipi di Minaccia",
            "type": "pie",
            "params": {
                "addTooltip": True,
                "addLegend": True,
                "legendPosition": "right",
                "isDonut": False
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "attack_type.keyword",
                        "size": 15,
                        "order": "desc",
                        "orderBy": "1",
                        "exclude": ["No Attack Detected", "Unknown/Analyst Review"]
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {
                "bool": {
                    "must_not": [
                        {"term": {"attack_type.keyword": "No Attack Detected"}},
                        {"term": {"attack_type.keyword": "Unknown/Analyst Review"}}
                    ]
                }
            },
            "filter": []
        }
        
        return self.create_visualization(
            "distribuzione-tipi-minaccia",
            "🎯 Distribuzione Tipi di Minaccia",
            vis_state,
            search_source
        )
    
    def create_log_source_viz(self) -> bool:
        """Sorgente Log"""
        vis_state = {
            "title": "Sorgente Log",
            "type": "pie",
            "params": {
                "addTooltip": True,
                "addLegend": True,
                "legendPosition": "right",
                "isDonut": True
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "log_source.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {"match_all": {}},
            "filter": []
        }
        
        return self.create_visualization(
            "sorgente-log",
            "🔍 Sorgente Log (Suricata vs ModSecurity)",
            vis_state,
            search_source
        )
    
    def create_top_ips_viz(self) -> bool:
        """Top IP Sorgenti"""
        vis_state = {
            "title": "Top IP Sorgenti",
            "type": "horizontal_bar",
            "params": {
                "addTooltip": True,
                "addLegend": False,
                "categoryAxes": [{
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "left",
                    "show": True
                }],
                "valueAxes": [{
                    "id": "ValueAxis-1",
                    "type": "value",
                    "position": "bottom",
                    "show": True
                }]
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "client_ip.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {
                "exists": {"field": "client_ip.keyword"}
            },
            "filter": []
        }
        
        return self.create_visualization(
            "top-ip-sorgenti",
            "🌐 Top IP Sorgenti",
            vis_state,
            search_source
        )
    
    def create_response_codes_viz(self) -> bool:
        """Codici Risposta HTTP"""
        vis_state = {
            "title": "Codici Risposta HTTP",
            "type": "histogram",
            "params": {
                "addTooltip": True,
                "addLegend": False,
                "categoryAxes": [{
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "bottom",
                    "show": True
                }],
                "valueAxes": [{
                    "id": "ValueAxis-1",
                    "type": "value",
                    "position": "left",
                    "show": True
                }]
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "response_code.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {
                "exists": {"field": "response_code.keyword"}
            },
            "filter": []
        }
        
        return self.create_visualization(
            "codici-risposta-http",
            "📊 Codici Risposta HTTP",
            vis_state,
            search_source
        )
    
    def create_top_uris_viz(self) -> bool:
        """Top URI Attaccate"""
        vis_state = {
            "title": "Top URI Attaccate",
            "type": "horizontal_bar",
            "params": {
                "addTooltip": True,
                "addLegend": False,
                "categoryAxes": [{
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "left",
                    "show": True
                }],
                "valueAxes": [{
                    "id": "ValueAxis-1",
                    "type": "value",
                    "position": "bottom",
                    "show": True
                }]
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "request_uri.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "request_uri.keyword"}},
                        {"exists": {"field": "attack_type.keyword"}}
                    ],
                    "must_not": [
                        {"term": {"attack_type.keyword": "No Attack Detected"}}
                    ]
                }
            },
            "filter": []
        }
        
        return self.create_visualization(
            "top-uri-attaccate",
            "🔗 Top URI Attaccate",
            vis_state,
            search_source
        )
    
    def create_events_table_viz(self) -> bool:
        """Tabella Eventi Dettagliata"""
        vis_state = {
            "title": "Tabella Eventi Dettagliata",
            "type": "table",
            "params": {
                "perPage": 10,
                "showPartialRows": False,
                "showMeticsAtAllLevels": False,
                "sort": {"columnIndex": None, "direction": None},
                "showTotal": False,
                "showToolbar": True
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "@timestamp",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1",
                        "customLabel": "Timestamp"
                    }
                },
                {
                    "id": "3",
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "log_source.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1",
                        "customLabel": "Sorgente"
                    }
                },
                {
                    "id": "4",
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "attack_type.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1",
                        "customLabel": "Tipo Attacco"
                    }
                },
                {
                    "id": "5",
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "client_ip.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1",
                        "customLabel": "IP Sorgente"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "security-soc",
            "query": {
                "bool": {
                    "must_not": [
                        {"term": {"attack_type.keyword": "No Attack Detected"}}
                    ]
                }
            },
            "filter": []
        }
        
        return self.create_visualization(
            "tabella-eventi-dettagliata",
            "📋 Tabella Eventi Dettagliata",
            vis_state,
            search_source
        )
    
    def create_suricata_alerts_viz(self) -> bool:
        """Alert Suricata per Categoria"""
        vis_state = {
            "title": "Alert Suricata per Categoria",
            "type": "histogram",
            "params": {
                "addTooltip": True,
                "addLegend": False,
                "categoryAxes": [{
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "bottom",
                    "show": True
                }],
                "valueAxes": [{
                    "id": "ValueAxis-1",
                    "type": "value",
                    "position": "left",
                    "show": True
                }]
            },
            "aggs": [
                {"id": "1", "type": "count", "schema": "metric"},
                {
                    "id": "2",
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "alert.category.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        }
        
        search_source = {
            "index": "suricata-logs-*",
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "alert"}},
                        {"exists": {"field": "alert.category.keyword"}}
                    ]
                }
            },
            "filter": []
        }
        
        return self.create_visualization(
            "alert-suricata-categoria",
            "🚨 Alert Suricata per Categoria",
            vis_state,
            search_source
        )
    
    def create_dashboard(self) -> bool:
        """Crea la dashboard con tutti i pannelli"""
        if not self.created_vizs:
            print("❌ Nessuna visualizzazione creata. Crea prima le visualizzazioni.")
            return False
        
        # Crea riferimenti per le visualizzazioni
        references = []
        for i, viz_id in enumerate(self.created_vizs):
            references.append({
                "name": f"panel-{i}",
                "type": "visualization",
                "id": viz_id
            })
        
        # Layout dei pannelli
        panels = []
        panel_layouts = [
            {"x": 0, "y": 0, "w": 24, "h": 3, "i": "filters"},
            {"x": 0, "y": 3, "w": 12, "h": 8, "i": "0"},
            {"x": 12, "y": 3, "w": 12, "h": 8, "i": "1"},
            {"x": 0, "y": 11, "w": 8, "h": 6, "i": "2"},
            {"x": 8, "y": 11, "w": 8, "h": 6, "i": "3"},
            {"x": 16, "y": 11, "w": 8, "h": 6, "i": "4"},
            {"x": 0, "y": 17, "w": 12, "h": 8, "i": "5"},
            {"x": 12, "y": 17, "w": 12, "h": 8, "i": "6"},
            {"x": 0, "y": 25, "w": 24, "h": 8, "i": "7"}
        ]
        
        for i, layout in enumerate(panel_layouts):
            if i == 0:
                # Filtri
                panels.append({
                    "version": "8.13.0",
                    "gridData": layout,
                    "panelIndex": "filters",
                    "embeddableConfig": {},
                    "panelType": "controls",
                    "id": "filters-control"
                })
            elif i - 1 < len(self.created_vizs):
                panels.append({
                    "version": "8.13.0",
                    "gridData": layout,
                    "panelIndex": str(i - 1),
                    "embeddableConfig": {},
                    "panelType": "visualization",
                    "id": self.created_vizs[i - 1]
                })
        
        attributes = {
            "title": "🛡️ Security Operations Center - Dashboard Didattica",
            "description": "Dashboard completa per analisi sicurezza: Suricata IDS + ModSecurity WAF",
            "panelsJSON": json.dumps(panels),
            "optionsJSON": json.dumps({
                "useMargins": True,
                "syncColors": False,
                "hidePanelTitles": False
            }),
            "timeRestore": True,
            "timeTo": "now",
            "timeFrom": "now-24h",
            "refreshInterval": {
                "pause": False,
                "value": 30000
            },
            "controlGroupInput": {
                "controlStyle": "oneLine",
                "chainingSystem": "HIERARCHICAL",
                "panelsJSON": json.dumps([
                    {
                        "order": 0,
                        "width": "medium",
                        "grow": True,
                        "type": "optionsListControl",
                        "explicitInput": {
                            "fieldName": "attack_type.keyword",
                            "title": "Tipo di Minaccia",
                            "id": "attack-type-filter"
                        }
                    },
                    {
                        "order": 1,
                        "width": "medium",
                        "grow": True,
                        "type": "optionsListControl",
                        "explicitInput": {
                            "fieldName": "log_source.keyword",
                            "title": "Sorgente Log",
                            "id": "log-source-filter"
                        }
                    },
                    {
                        "order": 2,
                        "width": "medium",
                        "grow": True,
                        "type": "optionsListControl",
                        "explicitInput": {
                            "fieldName": "client_ip.keyword",
                            "title": "IP Sorgente",
                            "id": "client-ip-filter"
                        }
                    }
                ])
            },
            # Rimuovo version - Kibana 8.x lo gestisce automaticamente
        }
        
        if self.create_or_update_saved_object("dashboard", "security-soc-dashboard", attributes, references):
            print(f"\n✅ Dashboard 'Security SOC Dashboard' creata con successo!")
            return True
        else:
            print(f"\n❌ Errore creando la dashboard")
            return False
    
    def run(self):
        """Esegue il processo completo"""
        print("=" * 60)
        print("🚀 Creazione Automatica Dashboard Security SOC")
        print("=" * 60)
        
        # Verifica connessione
        if not self.check_connection():
            sys.exit(1)
        
        # Verifica/Crea Data Views
        print("\n📋 Verifica/Creazione Data Views...")
        data_view_created = False
        
        # Prova a creare la Data View unificata
        if not self.check_data_view("security-soc"):
            print("⚠️  Data View 'Security SOC' non trovata, tentativo creazione automatica...")
            if self.create_data_view("Security SOC", "suricata-logs-*,modsec-logs-*"):
                data_view_created = True
            else:
                print("\n⚠️  Creazione automatica fallita. Crea manualmente:")
                print("   1. Vai su Stack Management → Data Views → Create data view")
                print("   2. Name: 'Security SOC'")
                print("   3. Index pattern: suricata-logs-*,modsec-logs-*")
                print("   4. Timestamp field: @timestamp")
                print("\n   Continuo comunque con le visualizzazioni...")
        else:
            print("✅ Data View 'Security SOC' trovata")
        
        # Verifica anche le altre Data Views (opzionali)
        if not self.check_data_view("suricata-logs"):
            print("ℹ️  Data View 'Suricata Logs' non trovata (opzionale)")
        
        if not self.check_data_view("modsec-logs"):
            print("ℹ️  Data View 'ModSecurity Logs' non trovata (opzionale)")
        
        # Crea visualizzazioni
        print("\n📊 Creazione visualizzazioni...")
        print("-" * 60)
        
        success_count = 0
        total_count = 8
        
        if self.create_timeline_viz():
            success_count += 1
        if self.create_attack_types_viz():
            success_count += 1
        if self.create_log_source_viz():
            success_count += 1
        if self.create_top_ips_viz():
            success_count += 1
        if self.create_response_codes_viz():
            success_count += 1
        if self.create_top_uris_viz():
            success_count += 1
        if self.create_events_table_viz():
            success_count += 1
        if self.create_suricata_alerts_viz():
            success_count += 1
        
        print(f"\n✅ {success_count}/{total_count} visualizzazioni create")
        
        # Crea dashboard
        if success_count > 0:
            print("\n🎨 Creazione dashboard...")
            if self.create_dashboard():
                print("\n" + "=" * 60)
                print("✅ COMPLETATO!")
                print("=" * 60)
                print(f"\n🌐 Apri la dashboard su:")
                print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
                print("\n💡 La dashboard include:")
                print("   - 8 visualizzazioni")
                print("   - 3 filtri interattivi")
                print("   - Auto-refresh ogni 30 secondi")
                print("   - Time range: Last 24 hours")
            else:
                print("\n⚠️  Dashboard non creata, ma le visualizzazioni sono disponibili")
        else:
            print("\n❌ Nessuna visualizzazione creata. Verifica i log sopra.")

if __name__ == "__main__":
    creator = KibanaDashboardCreator()
    creator.run()

