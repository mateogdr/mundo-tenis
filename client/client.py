import httpx
import asyncio

URL_API = "http://127.0.0.1:5000/api/v1/pistas"

async def ejecutar_pruebas():
    async with httpx.AsyncClient() as client:
        print(" INICIANDO CLIENTE AUTÓNOMO - MUNDO TENIS\n" + "-"*40)

        print("1. Solicitando lista de todas las pistas...")
        try:
            r = await client.get(f"{URL_API}/")
            r.raise_for_status()
            pistas = r.json()
            print(f"✅ ÉXITO: Se han recuperado {len(pistas)} pistas.")
        except Exception as e:
            print(f"❌ ERROR al listar pistas: {e}")

        print("\n2. Creando una nueva pista de prueba...")
        nueva_pista = {
            "nombre": "Pista Central Script",
            "superficie": "Tierra Batida",
            "pais": "España",
            "torneo": "Prueba Automática",
            "user_id": "66e948f8-b8a6-48c8-b96a-d52a2c920c13" 
        }
        id_creado = None
        try:
            r = await client.post(f"{URL_API}/", json=nueva_pista)
            r.raise_for_status()
            dato_guardado = r.json()
            id_creado = dato_guardado['id']
            print(f"✅ ÉXITO: Pista creada con ID: {id_creado}")
        except Exception as e:
            print(f"❌ ERROR al crear pista: {e}")

        if id_creado:
            print(f"\n3. Consultando detalle de la pista {id_creado} (Enriquecimiento)...")
            try:
                r = await client.get(f"{URL_API}/{id_creado}")
                r.raise_for_status()
                detalle = r.json()
                print(f"✅ Datos locales: {detalle['nombre']} ({detalle['torneo']})")
                
                if 'clima_externo' in detalle:
                    clima = detalle['clima_externo']
                    print(f"DATOS EXTERNOS (Open-Meteo): Temp: {clima.get('temperatura')}, Viento: {clima.get('viento')}")
                else:
                    print("⚠️  Advertencia: No se recibió información climática.")
            except Exception as e:
                print(f"❌ ERROR al obtener detalle: {e}")

            print(f"\n4. Eliminando la pista de prueba {id_creado}...")
            try:
                r = await client.delete(f"{URL_API}/{id_creado}")
                if r.status_code == 204:
                    print("✅ ÉXITO: Pista eliminada correctamente. Base de datos limpia.")
                else:
                    print(f"⚠️  Estado inesperado al borrar: {r.status_code}")
            except Exception as e:
                print(f"❌ ERROR al borrar: {e}")

        print("\n" + "-"*40 + "\n🏁 PRUEBAS FINALIZADAS")

if __name__ == "__main__":
    asyncio.run(ejecutar_pruebas())
