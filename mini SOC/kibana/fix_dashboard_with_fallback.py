#!/usr/bin/env python3
"""
Script per fixare la dashboard con valori statici/fallback
Aggiunge kibanaSavedObjectMeta con valori statici sicuri
"""

import json
import requests
import sys

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

def fix_dashboard_with_fallback():
    """Fix della dashboard con valori statici"""
    print("=" * 60)
    print("🔧 Fix Dashboard con Valori Statici/Fallback")
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
    
    # Fix 1: Assicurati che tutte le visualizzazioni abbiano kibanaSavedObjectMeta con valori statici
    print(f"\n📊 Fix 1: Aggiornamento visualizzazioni con valori statici...")
    
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&fields=title", headers={"kbn-xsrf": "true"})
        if response.status_code != 200:
            print(f"❌ Errore ottenendo visualizzazioni")
            return False
        
        visualizations = response.json().get("saved_objects", [])
        print(f"   Trovate {len(visualizations)} visualizzazioni")
        
        for viz in visualizations:
            viz_id = viz.get("id")
            title = viz.get("attributes", {}).get("title", viz_id)
            
            try:
                viz_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                if viz_response.status_code != 200:
                    continue
                
                viz_full = viz_response.json()
                attrs = dict(viz_full.get("attributes", {}))
                references = list(viz_full.get("references", []))
                
                # Aggiungi/aggiorna kibanaSavedObjectMeta con valori statici sicuri
                attrs["kibanaSavedObjectMeta"] = {
                    "searchSourceJSON": json.dumps({
                        "index": data_view_id,
                        "query": {
                            "match_all": {}
                        },
                        "filter": []
                    })
                }
                
                # Assicurati che ci sia la reference
                has_ref = False
                for ref in references:
                    if ref.get("type") == "index-pattern" and ref.get("id") == data_view_id:
                        has_ref = True
                        break
                
                if not has_ref:
                    references.append({
                        "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
                        "type": "index-pattern",
                        "id": data_view_id
                    })
                
                # Aggiorna
                update_url = f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                update_body = {
                    "attributes": attrs
                }
                if references:
                    update_body["references"] = references
                
                update_response = requests.put(
                    update_url,
                    json=update_body,
                    headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
                )
                
                if update_response.status_code in [200, 201]:
                    print(f"   ✅ '{title}' aggiornata")
                else:
                    print(f"   ⚠️  '{title}': {update_response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Errore '{title}': {e}")
                continue
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
    
    # Fix 2: Ricrea la dashboard completamente
    print(f"\n📊 Fix 2: Ricreazione dashboard...")
    
    try:
        # Elimina dashboard esistente
        delete_response = requests.delete(f"{KIBANA_URL}/api/saved_objects/dashboard/security-soc-dashboard", headers={"kbn-xsrf": "true"})
        if delete_response.status_code in [200, 404]:
            print("   ✅ Dashboard esistente eliminata")
        
        # Ottieni tutte le visualizzazioni per i references
        viz_ids = [viz.get("id") for viz in visualizations]
        
        # Crea panels
        panels = [
            {
                "version": "8.13.0",
                "gridData": {"x": 0, "y": 0, "w": 24, "h": 3, "i": "filters"},
                "panelIndex": "filters",
                "embeddableConfig": {},
                "panelType": "controls",
                "id": "filters-control"
            }
        ]
        
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
            if i < len(viz_ids):
                panels.append({
                    "version": "8.13.0",
                    "gridData": {**layout, "i": str(i)},
                    "panelIndex": str(i),
                    "embeddableConfig": {},
                    "panelType": "visualization",
                    "id": viz_ids[i]
                })
        
        # Crea references
        references = []
        for i, viz_id in enumerate(viz_ids):
            references.append({
                "name": f"panel-{i}",
                "type": "visualization",
                "id": viz_id
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
            }
        }
        
        create_response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/dashboard/security-soc-dashboard",
            json={
                "attributes": dashboard_attrs,
                "references": references
            },
            headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
        )
        
        if create_response.status_code in [200, 201]:
            print("   ✅ Dashboard ricreata")
            return True
        else:
            print(f"   ❌ Errore creando dashboard: {create_response.status_code}")
            print(f"      {create_response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if fix_dashboard_with_fallback():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 IMPORTANTE:")
        print("   1. Pulisci completamente la cache del browser")
        print("   2. Apri in modalità incognito/privata")
        print("   3. Se l'errore persiste, potrebbe essere un bug di Kibana 8.13.0")
        print("   4. Considera di aggiornare o downgrade Kibana")
    else:
        print("\n⚠️  Fix parziale. Verifica manualmente.")

if __name__ == "__main__":
    main()

