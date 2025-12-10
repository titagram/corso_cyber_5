#!/usr/bin/env python3
"""
Workaround: Aggiunge kibanaSavedObjectMeta con valore vuoto come fallback
Per risolvere bug Kibana 8.13.0 che cerca di accedere a searchSourceJSON anche quando undefined
"""

import json
import requests
import sys

KIBANA_URL = "http://localhost:5601"

def add_empty_fallback():
    """Aggiunge valore vuoto come fallback"""
    print("=" * 60)
    print("🔧 Workaround: Aggiunta Valore Vuoto come Fallback")
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
    
    # Ottieni tutte le visualizzazioni
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/_find?type=visualization&fields=title", headers={"kbn-xsrf": "true"})
        if response.status_code != 200:
            print(f"❌ Errore ottenendo visualizzazioni")
            return False
        
        visualizations = response.json().get("saved_objects", [])
        print(f"\n📊 Trovate {len(visualizations)} visualizzazioni")
        
        fixed_count = 0
        for viz in visualizations:
            viz_id = viz.get("id")
            title = viz.get("attributes", {}).get("title", viz_id)
            
            try:
                viz_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                if viz_response.status_code != 200:
                    continue
                
                viz_full = viz_response.json()
                attrs = dict(viz_full.get("attributes", {}))
                
                # Assicurati che kibanaSavedObjectMeta esista SEMPRE, anche se vuoto
                if "kibanaSavedObjectMeta" not in attrs:
                    attrs["kibanaSavedObjectMeta"] = {}
                
                # Assicurati che searchSourceJSON esista SEMPRE
                if "searchSourceJSON" not in attrs["kibanaSavedObjectMeta"]:
                    attrs["kibanaSavedObjectMeta"]["searchSourceJSON"] = "{}"
                
                # Se esiste già, verifica che sia valido JSON
                try:
                    ss_json = attrs["kibanaSavedObjectMeta"]["searchSourceJSON"]
                    if isinstance(ss_json, str):
                        json.loads(ss_json)  # Verifica che sia JSON valido
                    else:
                        attrs["kibanaSavedObjectMeta"]["searchSourceJSON"] = json.dumps(ss_json)
                except:
                    # Se non è valido, usa valore vuoto sicuro
                    attrs["kibanaSavedObjectMeta"]["searchSourceJSON"] = "{}"
                
                # Aggiorna
                update_url = f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                update_body = {
                    "attributes": attrs
                }
                
                # Mantieni references esistenti
                if viz_full.get("references"):
                    update_body["references"] = viz_full.get("references")
                
                update_response = requests.put(
                    update_url,
                    json=update_body,
                    headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
                )
                
                if update_response.status_code in [200, 201]:
                    print(f"   ✅ '{title}' - Fallback aggiunto")
                    fixed_count += 1
                else:
                    print(f"   ⚠️  '{title}': {update_response.status_code}")
                    print(f"      {update_response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Errore '{title}': {e}")
                continue
        
        print(f"\n✅ {fixed_count}/{len(visualizations)} visualizzazioni aggiornate con fallback")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if add_empty_fallback():
        print("\n" + "=" * 60)
        print("✅ WORKAROUND APPLICATO!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Se l'errore persiste ancora:")
        print("   1. Potrebbe essere un bug di Kibana 8.13.0")
        print("   2. Considera di downgrade a Kibana 8.12.x o 8.11.x")
        print("   3. Oppure aggiorna a Kibana 8.14+ se disponibile")
        print("   4. Verifica i log: docker logs kibana --tail 50")
    else:
        print("\n⚠️  Workaround parziale.")

if __name__ == "__main__":
    main()

