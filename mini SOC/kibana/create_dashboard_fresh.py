#!/usr/bin/env python3
"""
Crea dashboard completamente nuova con Kibana 8.12.2
Struttura compatibile e corretta
"""

import json
import requests
import sys

KIBANA_URL = "http://localhost:5601"

def get_data_view_id():
    """Ottieni l'ID della Data View"""
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=index-pattern&search_fields=title&search=suricata-logs", headers={"kbn-xsrf": "true"})
        if response.status_code == 200:
            saved_objects = response.json().get("saved_objects", [])
            for obj in saved_objects:
                title = obj.get("attributes", {}).get("title", "")
                if "suricata-logs" in title and "modsec-logs" in title:
                    return obj.get("id")
    except:
        pass
    return None

def get_all_visualizations():
    """Ottieni tutte le visualizzazioni"""
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&per_page=20", headers={"kbn-xsrf": "true"})
        if response.status_code == 200:
            return response.json().get("saved_objects", [])
    except:
        pass
    return []

def create_dashboard_fresh():
    """Crea dashboard completamente nuova"""
    print("=" * 60)
    print("🔧 Creazione Dashboard Completamente Nuova (Kibana 8.12.2)")
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
    data_view_id = get_data_view_id()
    if not data_view_id:
        print("❌ Data View non trovata")
        sys.exit(1)
    
    print(f"✅ Data View ID: {data_view_id}")
    
    # Ottieni visualizzazioni
    visualizations = get_all_visualizations()
    if not visualizations:
        print("❌ Nessuna visualizzazione trovata")
        sys.exit(1)
    
    print(f"✅ Trovate {len(visualizations)} visualizzazioni")
    
    # Crea panels con versione 8.12.2
    panels = []
    
    # Panel 0: Controls
    panels.append({
        "version": "8.12.2",
        "gridData": {"x": 0, "y": 0, "w": 24, "h": 3, "i": "filters"},
        "panelIndex": "filters",
        "embeddableConfig": {},
        "panelType": "controls",
        "id": "filters-control"
    })
    
    # Panels visualizzazioni
    panel_layouts = [
        {"x": 0, "y": 3, "w": 12, "h": 8},
        {"x": 12, "y": 3, "w": 12, "h": 8},
        {"x": 0, "y": 11, "w": 8, "h": 6},
        {"x": 8, "y": 11, "w": 8, "h": 6},
        {"x": 16, "y": 11, "w": 8, "h": 6},
        {"x": 0, "y": 17, "w": 12, "h": 8},
        {"x": 12, "y": 17, "w": 12, "h": 8},
        {"x": 0, "y": 25, "w": 24, "h": 8}
    ]
    
    for i, layout in enumerate(panel_layouts):
        if i < len(visualizations):
            panels.append({
                "version": "8.12.2",
                "gridData": {**layout, "i": str(i)},
                "panelIndex": str(i),
                "embeddableConfig": {},
                "panelType": "visualization",
                "id": visualizations[i].get("id")
            })
    
    # Crea controls con dataViewId
    control_panels = [
        {
            "order": 0,
            "width": "medium",
            "grow": True,
            "type": "optionsListControl",
            "explicitInput": {
                "fieldName": "attack_type.keyword",
                "title": "Tipo di Minaccia",
                "id": "attack-type-filter",
                "dataViewId": data_view_id
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
                "id": "log-source-filter",
                "dataViewId": data_view_id
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
                "id": "client-ip-filter",
                "dataViewId": data_view_id
            }
        }
    ]
    
    # Crea references
    references = []
    for i, viz in enumerate(visualizations):
        references.append({
            "name": f"panel-{i}",
            "type": "visualization",
            "id": viz.get("id")
        })
    
    # Aggiungi reference alla Data View
    references.append({
        "name": "controlGroupInput.panelsJSON[].explicitInput.dataViewId",
        "type": "index-pattern",
        "id": data_view_id
    })
    
    # Crea dashboard
    dashboard_attrs = {
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
            "panelsJSON": json.dumps(control_panels)
        }
    }
    
    try:
        create_response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/dashboard/security-soc-dashboard",
            json={
                "attributes": dashboard_attrs,
                "references": references
            },
            headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
        )
        
        if create_response.status_code in [200, 201]:
            print(f"\n✅ Dashboard creata con successo!")
            print(f"   - Versione pannelli: 8.12.2")
            print(f"   - Controls con dataViewId: ✅")
            print(f"   - References corrette: ✅")
            return True
        else:
            print(f"\n❌ Errore creando dashboard: {create_response.status_code}")
            print(f"   {create_response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if create_dashboard_fresh():
        print("\n" + "=" * 60)
        print("✅ DASHBOARD CREATA!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Se ancora non funziona:")
        print("   Potrebbe essere necessario creare la dashboard manualmente")
        print("   tramite l'interfaccia Kibana per evitare problemi di compatibilità")
    else:
        print("\n⚠️  Creazione fallita.")

if __name__ == "__main__":
    main()

