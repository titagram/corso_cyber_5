#!/usr/bin/env python3
"""
Script per ricreare completamente le visualizzazioni SENZA kibanaSavedObjectMeta
"""

import json
import requests
import sys
import time

KIBANA_URL = "http://localhost:5601"

def get_data_view_id(pattern: str):
    """Ottieni l'ID della Data View"""
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=index-pattern&search_fields=title&search={pattern}", headers={"kbn-xsrf": "true"})
        if response.status_code == 200:
            saved_objects = response.json().get("saved_objects", [])
            for obj in saved_objects:
                if pattern in obj.get("attributes", {}).get("title", ""):
                    return obj.get("id")
    except:
        pass
    return None

def delete_visualization(viz_id: str):
    """Elimina una visualizzazione"""
    try:
        response = requests.delete(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
        return response.status_code in [200, 404]  # 404 = già eliminata
    except:
        return False

def create_visualization_clean(viz_id: str, title: str, vis_state: dict, data_view_id: str):
    """Crea una visualizzazione SENZA kibanaSavedObjectMeta"""
    attributes = {
        "title": title,
        "visState": json.dumps(vis_state),
        "uiStateJSON": "{}"
        # NON includiamo kibanaSavedObjectMeta
    }
    
    references = [{
        "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
        "type": "index-pattern",
        "id": data_view_id
    }]
    
    body = {
        "attributes": attributes,
        "references": references
    }
    
    try:
        response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}",
            json=body,
            headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            return True
        elif response.status_code == 409:
            # Esiste già, elimina e ricrea
            delete_visualization(viz_id)
            time.sleep(1)
            response = requests.post(
                f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}",
                json=body,
                headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
            )
            return response.status_code in [200, 201]
        return False
    except Exception as e:
        print(f"      ❌ Errore: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Ricreazione Visualizzazioni SENZA kibanaSavedObjectMeta")
    print("=" * 60)
    
    # Verifica connessione
    try:
        response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
        if response.status_code != 200:
            print(f"❌ Kibana non raggiungibile")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        sys.exit(1)
    
    print("✅ Connesso a Kibana")
    
    # Trova Data View
    data_view_id = get_data_view_id("suricata-logs-*,modsec-logs-*")
    if not data_view_id:
        print("❌ Data View non trovata")
        sys.exit(1)
    
    print(f"✅ Data View ID: {data_view_id}")
    
    # Lista visualizzazioni da ricreare
    visualizations = [
        {
            "id": "timeline-eventi-sicurezza",
            "title": "📈 Timeline Eventi di Sicurezza",
            "vis_state": {
                "title": "Timeline Eventi di Sicurezza",
                "type": "histogram",
                "params": {
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{"id": "CategoryAxis-1", "type": "category", "position": "bottom", "show": True, "scale": {"type": "linear"}, "labels": {"show": True}}],
                    "valueAxes": [{"id": "ValueAxis-1", "type": "value", "position": "left", "show": True, "scale": {"type": "linear"}}],
                    "seriesParams": [{"show": True, "type": "histogram", "mode": "stacked", "data": {"label": "Count", "id": "1"}, "valueAxis": "ValueAxis-1"}],
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right"
                },
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "date_histogram", "schema": "segment", "params": {"field": "@timestamp", "interval": "auto", "min_doc_count": 1}},
                    {"id": "3", "type": "terms", "schema": "group", "params": {"field": "log_source.keyword", "size": 5, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "distribuzione-tipi-minaccia",
            "title": "🎯 Distribuzione Tipi di Minaccia",
            "vis_state": {
                "title": "Distribuzione Tipi di Minaccia",
                "type": "pie",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right", "isDonut": False},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "attack_type.keyword", "size": 15, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "sorgente-log",
            "title": "🔍 Sorgente Log (Suricata vs ModSecurity)",
            "vis_state": {
                "title": "Sorgente Log",
                "type": "pie",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right", "isDonut": False},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "log_source.keyword", "size": 10, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "top-ip-sorgenti",
            "title": "🌐 Top IP Sorgenti",
            "vis_state": {
                "title": "Top IP Sorgenti",
                "type": "bar",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right"},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "client_ip.keyword", "size": 10, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "codici-risposta-http",
            "title": "📊 Codici Risposta HTTP",
            "vis_state": {
                "title": "Codici Risposta HTTP",
                "type": "pie",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right", "isDonut": False},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "response_status.keyword", "size": 10, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "top-uri-attaccate",
            "title": "🔗 Top URI Attaccate",
            "vis_state": {
                "title": "Top URI Attaccate",
                "type": "bar",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right"},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "request_uri.keyword", "size": 10, "order": "desc", "orderBy": "1"}}
                ]
            }
        },
        {
            "id": "tabella-eventi-dettagliata",
            "title": "📋 Tabella Eventi Dettagliata",
            "vis_state": {
                "title": "Tabella Eventi Dettagliata",
                "type": "table",
                "params": {"perPage": 10, "showPartialRows": False, "showMeticsAtAllLevels": False},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "bucket", "params": {"field": "@timestamp", "size": 10, "order": "desc", "orderBy": "1"}},
                    {"id": "3", "type": "terms", "schema": "bucket", "params": {"field": "log_source.keyword", "size": 5}},
                    {"id": "4", "type": "terms", "schema": "bucket", "params": {"field": "attack_type.keyword", "size": 10}}
                ]
            }
        },
        {
            "id": "alert-suricata-categoria",
            "title": "🚨 Alert Suricata per Categoria",
            "vis_state": {
                "title": "Alert Suricata per Categoria",
                "type": "bar",
                "params": {"addTooltip": True, "addLegend": True, "legendPosition": "right"},
                "aggs": [
                    {"id": "1", "type": "count", "schema": "metric"},
                    {"id": "2", "type": "terms", "schema": "segment", "params": {"field": "alert.category.keyword", "size": 10, "order": "desc", "orderBy": "1"}}
                ]
            }
        }
    ]
    
    print(f"\n🗑️  Eliminazione visualizzazioni esistenti...")
    for viz in visualizations:
        if delete_visualization(viz["id"]):
            print(f"   ✅ '{viz['id']}' eliminata")
        time.sleep(0.5)
    
    print(f"\n📊 Creazione visualizzazioni pulite...")
    success_count = 0
    for viz in visualizations:
        print(f"   🔧 Creando '{viz['title']}'...")
        if create_visualization_clean(viz["id"], viz["title"], viz["vis_state"], data_view_id):
            print(f"      ✅ Creata")
            success_count += 1
        else:
            print(f"      ❌ Errore")
        time.sleep(0.5)
    
    print(f"\n✅ {success_count}/{len(visualizations)} visualizzazioni ricreate")
    print(f"\n🌐 Prova la dashboard: {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
    print("💡 Ricarica con Ctrl+F5 dopo aver pulito la cache del browser")

if __name__ == "__main__":
    main()

