#!/usr/bin/env python3
"""
Script per aggiungere kibanaSavedObjectMeta CORRETTO alle visualizzazioni
Kibana 8.x richiede questo campo quando carica le visualizzazioni nella dashboard
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

def fix_visualizations():
    """Aggiunge kibanaSavedObjectMeta corretto alle visualizzazioni"""
    print("=" * 60)
    print("🔧 Aggiunta kibanaSavedObjectMeta Corretto alle Visualizzazioni")
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
    
    # Ottieni tutte le visualizzazioni
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&fields=title", headers={"kbn-xsrf": "true"})
        if response.status_code != 200:
            print(f"❌ Errore ottenendo visualizzazioni: {response.status_code}")
            return False
        
        visualizations = response.json().get("saved_objects", [])
        print(f"\n📊 Trovate {len(visualizations)} visualizzazioni")
        
        fixed_count = 0
        for viz in visualizations:
            viz_id = viz.get("id")
            title = viz.get("attributes", {}).get("title", viz_id)
            
            # Ottieni la visualizzazione completa
            try:
                viz_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                if viz_response.status_code != 200:
                    continue
                
                viz_full = viz_response.json()
                attrs = dict(viz_full.get("attributes", {}))
                references = list(viz_full.get("references", []))
                
                # Verifica se ha kibanaSavedObjectMeta corretto
                needs_fix = False
                
                if "kibanaSavedObjectMeta" not in attrs:
                    needs_fix = True
                    print(f"   🔧 '{title}' - Aggiungo kibanaSavedObjectMeta...")
                else:
                    # Verifica che sia corretto
                    try:
                        meta = attrs.get("kibanaSavedObjectMeta", {})
                        search_source_str = meta.get("searchSourceJSON", "{}")
                        search_source = json.loads(search_source_str) if isinstance(search_source_str, str) else search_source_str
                        current_index = search_source.get("index", "")
                        
                        if current_index != data_view_id:
                            needs_fix = True
                            print(f"   🔧 '{title}' - Aggiorno kibanaSavedObjectMeta con Data View corretta...")
                    except:
                        needs_fix = True
                        print(f"   🔧 '{title}' - Correggo kibanaSavedObjectMeta...")
                
                if needs_fix:
                    # Aggiungi/aggiorna kibanaSavedObjectMeta con struttura corretta
                    attrs["kibanaSavedObjectMeta"] = {
                        "searchSourceJSON": json.dumps({
                            "index": data_view_id,
                            "query": {"match_all": {}},
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
                        print(f"      ✅ '{title}' aggiornata")
                        fixed_count += 1
                    else:
                        print(f"      ❌ Errore: {update_response.status_code}")
                        print(f"         {update_response.text[:200]}")
                else:
                    print(f"   ℹ️  '{title}' già corretta")
                    
            except Exception as e:
                print(f"   ❌ Errore processando '{viz_id}': {e}")
                continue
        
        print(f"\n✅ {fixed_count} visualizzazioni aggiornate")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if fix_visualizations():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Pulisci la cache del browser e ricarica con Ctrl+F5")
    else:
        print("\n⚠️  Fix parziale. Verifica manualmente.")

if __name__ == "__main__":
    main()

