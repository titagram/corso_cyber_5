#!/usr/bin/env python3
"""
Fix COMPLETO: Aggiunge kibanaSavedObjectMeta completo a TUTTE le visualizzazioni
con struttura completa e corretta
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

def fix_all_visualizations():
    """Aggiunge kibanaSavedObjectMeta completo a tutte le visualizzazioni"""
    print("=" * 60)
    print("🔧 Fix COMPLETO: kibanaSavedObjectMeta a TUTTE le visualizzazioni")
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
    
    # Ottieni tutte le visualizzazioni
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&per_page=20", headers={"kbn-xsrf": "true"})
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
                    print(f"   ⚠️  Impossibile ottenere '{viz_id}'")
                    continue
                
                viz_full = viz_response.json()
                attrs = dict(viz_full.get("attributes", {}))
                references = list(viz_full.get("references", []))
                
                # Crea kibanaSavedObjectMeta COMPLETO e CORRETTO
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
                    # Verifica che sia stato salvato correttamente
                    verify_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                    if verify_response.status_code == 200:
                        verify_attrs = verify_response.json().get("attributes", {})
                        if "kibanaSavedObjectMeta" in verify_attrs:
                            meta = verify_attrs.get("kibanaSavedObjectMeta", {})
                            ss = meta.get("searchSourceJSON", "")
                            if data_view_id in ss:
                                print(f"   ✅ '{title}' - kibanaSavedObjectMeta completo")
                                fixed_count += 1
                            else:
                                print(f"   ⚠️  '{title}' - aggiornata ma dataViewId non trovato")
                        else:
                            print(f"   ⚠️  '{title}' - aggiornata ma kibanaSavedObjectMeta non presente")
                    else:
                        print(f"   ⚠️  '{title}' - aggiornata ma verifica fallita")
                else:
                    print(f"   ❌ '{title}': {update_response.status_code}")
                    print(f"      {update_response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Errore '{title}': {e}")
                continue
        
        print(f"\n✅ {fixed_count}/{len(visualizations)} visualizzazioni aggiornate correttamente")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if fix_all_visualizations():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 IMPORTANTE:")
        print("   1. Pulisci completamente la cache del browser")
        print("   2. Apri in modalità incognito/privata")
        print("   3. Se ancora non funziona, prova a creare la dashboard manualmente")
    else:
        print("\n⚠️  Fix parziale.")

if __name__ == "__main__":
    main()

