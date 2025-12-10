#!/usr/bin/env python3
"""
Script per fixare la dashboard Kibana - Risolve errore kibanaSavedObjectMeta
"""

import json
import requests
import sys

KIBANA_URL = "http://localhost:5601"

def get_all_data_views():
    """Ottieni tutte le data views"""
    data_views = []
    
    # Prova metodo 1: API data_views
    try:
        response = requests.get(f"{KIBANA_URL}/api/data_views/data_view", headers={"kbn-xsrf": "true"})
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and "data_view" in result:
                data_views.extend(result["data_view"] if isinstance(result["data_view"], list) else [result["data_view"]])
            elif isinstance(result, list):
                data_views.extend(result)
    except:
        pass
    
    # Prova metodo 2: Saved objects find
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=index-pattern&fields=title", headers={"kbn-xsrf": "true"})
        if response.status_code == 200:
            saved_objects = response.json().get("saved_objects", [])
            for obj in saved_objects:
                attrs = obj.get("attributes", {})
                data_views.append({
                    "id": obj.get("id"),
                    "name": obj.get("id"),
                    "title": attrs.get("title", obj.get("id"))
                })
    except:
        pass
    
    return data_views

def create_data_view(name: str, pattern: str):
    """Crea una data view"""
    url = f"{KIBANA_URL}/api/data_views/data_view"
    body = {
        "data_view": {
            "title": name,
            "name": name,
            "timeFieldName": "@timestamp"
        }
    }
    
    try:
        response = requests.post(url, json=body, headers={"kbn-xsrf": "true", "Content-Type": "application/json"})
        if response.status_code in [200, 201]:
            print(f"✅ Data View '{name}' creata")
            return True
        elif response.status_code == 409:
            print(f"⚠️  Data View '{name}' già esistente")
            return True
        else:
            print(f"⚠️  Errore creando Data View: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def fix_visualizations():
    """Aggiorna le visualizzazioni per usare una data view esistente"""
    # Ottieni tutte le data views
    data_views = get_all_data_views()
    print(f"\n📋 Data Views disponibili: {len(data_views)}")
    for dv in data_views:
        print(f"   - {dv.get('name', dv.get('title', 'Unknown'))}: {dv.get('title', 'N/A')}")
    
    # Cerca una data view valida che include sia suricata che modsec
    valid_data_view_id = None
    valid_data_view_name = None
    
    for dv in data_views:
        title = dv.get('title', '')
        dv_id = dv.get('id', '')
        # Cerca quella che include entrambi i pattern
        if 'suricata' in title.lower() and 'modsec' in title.lower():
            valid_data_view_id = dv_id
            valid_data_view_name = title
            break
    
    # Se non trovata, usa la prima disponibile
    if not valid_data_view_id and data_views:
        valid_data_view_id = data_views[0].get('id', '')
        valid_data_view_name = data_views[0].get('title', data_views[0].get('id', ''))
    
    if not valid_data_view_id:
        print("\n⚠️  Nessuna Data View trovata. Creo 'Security SOC'...")
        if create_data_view("Security SOC", "suricata-logs-*,modsec-logs-*"):
            # Ottieni l'ID della Data View appena creata
            data_views_new = get_all_data_views()
            for dv in data_views_new:
                if dv.get('title', '') == "suricata-logs-*,modsec-logs-*":
                    valid_data_view_id = dv.get('id', '')
                    valid_data_view_name = "suricata-logs-*,modsec-logs-*"
                    break
        else:
            print("❌ Impossibile creare Data View. Crea manualmente:")
            print("   1. Vai su Stack Management → Data Views")
            print("   2. Crea 'Security SOC' con pattern: suricata-logs-*,modsec-logs-*")
            return False
    
    print(f"\n✅ Userò Data View ID: {valid_data_view_id}")
    print(f"   Nome: {valid_data_view_name}")
    
    # Ottieni tutte le visualizzazioni usando _find
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&fields=title", headers={"kbn-xsrf": "true"})
        if response.status_code != 200:
            print(f"❌ Errore ottenendo visualizzazioni: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
        
        visualizations = response.json().get("saved_objects", [])
        print(f"\n📊 Trovate {len(visualizations)} visualizzazioni")
        
        fixed_count = 0
        for viz in visualizations:
            viz_id = viz.get("id")
            attrs = viz.get("attributes", {})
            
            # Verifica se ha kibanaSavedObjectMeta
            if "kibanaSavedObjectMeta" not in attrs:
                print(f"   ⚠️  '{viz_id}' manca kibanaSavedObjectMeta, aggiungo...")
                attrs["kibanaSavedObjectMeta"] = {
                    "searchSourceJSON": json.dumps({
                        "index": valid_data_view_id,
                        "query": {"match_all": {}},
                        "filter": []
                    })
                }
                
                # Aggiorna
                update_url = f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                update_body = {"attributes": attrs}
                update_response = requests.put(update_url, json=update_body, headers={"kbn-xsrf": "true", "Content-Type": "application/json"})
                
                if update_response.status_code in [200, 201]:
                    print(f"   ✅ '{viz_id}' aggiornata (aggiunto kibanaSavedObjectMeta)")
                    fixed_count += 1
                else:
                    print(f"   ❌ Errore aggiornando '{viz_id}': {update_response.status_code}")
                    print(f"      {update_response.text[:200]}")
            
            # Aggiorna anche il searchSourceJSON se usa un indice che non esiste
            elif "kibanaSavedObjectMeta" in attrs:
                try:
                    search_source_str = attrs["kibanaSavedObjectMeta"].get("searchSourceJSON", "{}")
                    search_source = json.loads(search_source_str) if isinstance(search_source_str, str) else search_source_str
                    current_index = search_source.get("index", "")
                    
                    # Se usa "security-soc" o un nome invece di un ID, aggiorna
                    if current_index == "security-soc" or (current_index and not current_index.startswith("2b") and not current_index.startswith("3")):
                        # Aggiorna con ID della data view valida
                        attrs["kibanaSavedObjectMeta"]["searchSourceJSON"] = json.dumps({
                            "index": valid_data_view_id,
                            "query": search_source.get("query", {"match_all": {}}),
                            "filter": search_source.get("filter", [])
                        })
                        
                        update_url = f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                        update_body = {"attributes": attrs}
                        update_response = requests.put(update_url, json=update_body, headers={"kbn-xsrf": "true", "Content-Type": "application/json"})
                        
                        if update_response.status_code in [200, 201]:
                            print(f"   ✅ '{viz_id}' aggiornata con Data View ID '{valid_data_view_id[:20]}...'")
                            fixed_count += 1
                        else:
                            print(f"   ⚠️  Errore aggiornando '{viz_id}': {update_response.status_code}")
                            print(f"      {update_response.text[:200]}")
                except:
                    pass
        
        print(f"\n✅ {fixed_count} visualizzazioni aggiornate")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Fix Dashboard Kibana - Risoluzione errore kibanaSavedObjectMeta")
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
    
    # Fix visualizzazioni
    if fix_visualizations():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova ad aprire la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Se l'errore persiste:")
        print("   1. Ricarica la pagina (Ctrl+F5)")
        print("   2. Verifica che la Data View esista")
        print("   3. Elimina e ricrea la dashboard se necessario")
    else:
        print("\n⚠️  Fix parziale. Verifica manualmente.")

if __name__ == "__main__":
    main()

