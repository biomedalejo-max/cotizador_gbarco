import os
import requests
import tempfile
import asyncio

# --- REPARACIÓN VITAL PARA STREAMLIT CLOUD ---
# Activa el bucle de eventos que Streamlit apaga en sus servidores
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ---------------------------------------------

from duckduckgo_search import DDGS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def buscar_inteligente(referencia: str, descripcion: str, max_resultados: int = 4) -> tuple:
    """Busca imágenes automáticamente reparando el hilo de Streamlit."""
    ref = (referencia or "").strip()
    desc = (descripcion or "").strip()
    
    # Lista de términos a probar en orden
    terminos_a_probar = []
    if ref:
        terminos_a_probar.append((ref, f"Referencia '{ref}'"))
    if desc:
        clave_desc = " ".join(desc.split()[:6])
        terminos_a_probar.append((clave_desc, f"Descripción '{clave_desc}'"))
    if ref and desc:
        terminos_a_probar.append((f"{ref} {desc.split()[0]}", "Combinación"))

    # Asegurar el bucle en cada intento
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except Exception:
        pass

    for termino, motivo in terminos_a_probar:
        try:
            with DDGS() as ddgs:
                resultados = list(ddgs.images(
                    keywords=termino,
                    max_results=max_resultados,
                    safesearch='moderate'
                ))
                urls = [r.get('image') for r in resultados if r.get('image')]
                if urls:
                    return urls, motivo, None
        except Exception as error_busqueda:
            # Si falla un término, prueba el siguiente
            continue

    return [], "Sin resultados", "Los servidores de búsqueda no respondieron."

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga cualquier imagen de internet y la prepara para el Word."""
    if not url_imagen or not url_imagen.startswith("http"):
        return None
    try:
        resp = requests.get(url_imagen, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(resp.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
    return None
