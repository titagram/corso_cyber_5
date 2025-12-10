#!/usr/bin/env python3
"""
Script per rimuovere kibanaSavedObjectMeta dalle visualizzazioni Kibana 8.x
In Kibana 8.x, le visualizzazioni usano 'references' invece di kibanaSavedObjectMeta
"""

import json
import requests
import sys

KIBANA_URL = "http://localhost:5601"

def get_data_view_id(pattern: str):
    """Ottieni l'ID della Data View dal pattern"""
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

def remove_kibanaSavedObjectMeta():
    """Rimuove kibanaSavedObjectMeta dalle visualizzazioni e aggiunge references"""
    print("=" * 60)
    print("🔧 Rimozione kibanaSavedObjectMeta dalle visualizzazioni")
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
    
    # Trova la Data View
    data_view_id = get_data_view_id("suricata-logs-*,modsec-logs-*")
    if not data_view_id:
        print("⚠️  Data View non trovata, provo a cercare altre...")
        data_view_id = get_data_view_id("suricata")
        if not data_view_id:
            print("❌ Impossibile trovare Data View")
            return False
    
    print(f"✅ Data View trovata: {data_view_id}")
    
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
            
            # Ottieni la visualizzazione completa per avere tutti i campi
            try:
                viz_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                if viz_response.status_code != 200:
                    print(f"   ⚠️  Impossibile ottenere dettagli di '{viz_id}'")
                    continue
                
                viz_full = viz_response.json()
                attrs = dict(viz_full.get("attributes", {}))
                references = list(viz_full.get("references", []))
                
                # Verifica se ha kibanaSavedObjectMeta
                if "kibanaSavedObjectMeta" in attrs:
                    print(f"   🔧 '{title}' ({viz_id}) - Rimuovo kibanaSavedObjectMeta...")
                    
                    # Crea una copia profonda degli attributi e rimuovi kibanaSavedObjectMeta
                    new_attrs = {}
                    for key, value in attrs.items():
                        if key != "kibanaSavedObjectMeta":
                            new_attrs[key] = value
                    
                    # Aggiungi reference alla Data View se non presente
                    has_data_view_ref = False
                    for ref in references:
                        if ref.get("type") == "index-pattern" and ref.get("id") == data_view_id:
                            has_data_view_ref = True
                            break
                    
                    if not has_data_view_ref:
                        references.append({
                            "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
                            "type": "index-pattern",
                            "id": data_view_id
                        })
                        print(f"      ✅ Aggiunta reference alla Data View")
                    
                    # Aggiorna la visualizzazione SENZA kibanaSavedObjectMeta
                    update_url = f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                    update_body = {
                        "attributes": new_attrs
                    }
                    if references:
                        update_body["references"] = references
                    
                    update_response = requests.put(
                        update_url, 
                        json=update_body, 
                        headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
                    )
                    
                    if update_response.status_code in [200, 201]:
                        # Verifica che sia stato rimosso
                        verify_response = requests.get(f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}", headers={"kbn-xsrf": "true"})
                        if verify_response.status_code == 200:
                            verify_attrs = verify_response.json().get("attributes", {})
                            if "kibanaSavedObjectMeta" not in verify_attrs:
                                print(f"      ✅ '{title}' aggiornata (kibanaSavedObjectMeta rimosso)")
                            else:
                                print(f"      ⚠️  '{title}' aggiornata ma kibanaSavedObjectMeta ancora presente")
                        fixed_count += 1
                    else:
                        print(f"      ❌ Errore aggiornando '{title}': {update_response.status_code}")
                        print(f"         {update_response.text[:300]}")
                else:
                    print(f"   ℹ️  '{title}' non ha kibanaSavedObjectMeta, salto")
                    
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
    if remove_kibanaSavedObjectMeta():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova ad aprire la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Ricarica la pagina con Ctrl+F5")
    else:
        print("\n⚠️  Fix parziale. Verifica manualmente.")

if __name__ == "__main__":
    main()

