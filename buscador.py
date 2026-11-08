import os
import requests
import tempfile
from duckduckgo_search import DDGS

def buscar_imagenes_producto(termino_busqueda: str, max_resultados: int = 4) -> list:
    """Busca imágenes en internet usando la referencia del equipo."""
    if not termino_busqueda.strip():
        return []
    
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.images(
                keywords=termino_busqueda,
                max_results=max_resultados,
                safesearch='moderate'
            ))
            urls = [r.get('image') for r in resultados if r.get('image')]
            return urls
    except Exception as e:
        print(f"Error al buscar imágenes: {e}")
        return []

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga la imagen seleccionada y la guarda temporalmente."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url_imagen, headers=headers, timeout=8)
        if resp.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(resp.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
    return None