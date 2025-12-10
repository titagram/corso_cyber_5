#!/usr/bin/env python3
"""
Fix della dashboard: aggiunge Data View ai controls e aggiorna versione pannelli
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

def fix_dashboard():
    """Fix della dashboard con Data View nei controls"""
    print("=" * 60)
    print("🔧 Fix Dashboard: Aggiunta Data View ai Controls")
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
    
    # Ottieni la dashboard
    try:
        response = requests.get(f"{KIBANA_URL}/api/saved_objects/dashboard/security-soc-dashboard", headers={"kbn-xsrf": "true"})
        if response.status_code != 200:
            print(f"❌ Errore ottenendo dashboard: {response.status_code}")
            return False
        
        dashboard = response.json()
        attrs = dict(dashboard.get("attributes", {}))
        references = list(dashboard.get("references", []))
        
        print(f"\n📊 Dashboard trovata")
        
        # Parse panelsJSON
        panels = json.loads(attrs.get("panelsJSON", "[]"))
        print(f"   Pannelli trovati: {len(panels)}")
        
        # Aggiorna versione pannelli da 8.13.0 a 8.12.2
        updated_panels = []
        for panel in panels:
            panel_copy = dict(panel)
            if panel_copy.get("version") == "8.13.0":
                panel_copy["version"] = "8.12.2"
            updated_panels.append(panel_copy)
        
        # Parse controlGroupInput
        control_group = attrs.get("controlGroupInput", {})
        control_panels = json.loads(control_group.get("panelsJSON", "[]"))
        
        print(f"   Controls trovati: {len(control_panels)}")
        
        # Aggiungi dataViewId a ogni control
        updated_control_panels = []
        for control in control_panels:
            control_copy = dict(control)
            explicit_input = control_copy.get("explicitInput", {})
            explicit_input["dataViewId"] = data_view_id
            control_copy["explicitInput"] = explicit_input
            updated_control_panels.append(control_copy)
        
        # Aggiorna controlGroupInput
        control_group["panelsJSON"] = json.dumps(updated_control_panels)
        attrs["controlGroupInput"] = control_group
        
        # Aggiorna panelsJSON
        attrs["panelsJSON"] = json.dumps(updated_panels)
        
        # Assicurati che ci sia la reference alla Data View
        has_data_view_ref = False
        for ref in references:
            if ref.get("type") == "index-pattern" and ref.get("id") == data_view_id:
                has_data_view_ref = True
                break
        
        if not has_data_view_ref:
            references.append({
                "name": "controlGroupInput.panelsJSON[].explicitInput.dataViewId",
                "type": "index-pattern",
                "id": data_view_id
            })
            print(f"   ✅ Aggiunta reference alla Data View")
        
        # Aggiorna dashboard
        update_url = f"{KIBANA_URL}/api/saved_objects/dashboard/security-soc-dashboard"
        update_body = {
            "attributes": attrs,
            "references": references
        }
        
        update_response = requests.put(
            update_url,
            json=update_body,
            headers={"kbn-xsrf": "true", "Content-Type": "application/json"}
        )
        
        if update_response.status_code in [200, 201]:
            print(f"\n✅ Dashboard aggiornata con successo!")
            print(f"   - Versione pannelli aggiornata: 8.13.0 → 8.12.2")
            print(f"   - Data View aggiunta ai controls")
            return True
        else:
            print(f"\n❌ Errore aggiornando dashboard: {update_response.status_code}")
            print(f"   {update_response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if fix_dashboard():
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETATO!")
        print("=" * 60)
        print(f"\n🌐 Prova la dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/security-soc-dashboard")
        print("\n💡 Pulisci la cache del browser e ricarica con Ctrl+F5")
    else:
        print("\n⚠️  Fix fallito. Verifica manualmente.")

if __name__ == "__main__":
    main()

