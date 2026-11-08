import os
import re
import urllib.parse
import requests
import tempfile

def buscar_imagenes_producto(termino_busqueda: str, max_resultados: int = 4) -> list:
    """Busca imágenes reales en Google Imágenes sin bloqueos."""
    if not termino_busqueda or not termino_busqueda.strip():
        return []
    
    urls = []
    
    # 1. Búsqueda directa en Google Imágenes
    try:
        query = urllib.parse.quote_plus(termino_busqueda.strip())
        url_google = f"https://www.google.com/search?q={query}&tbm=isch&hl=es"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        }
        
        resp = requests.get(url_google, headers=headers, timeout=6)
        if resp.status_code == 200:
            # Extraer las miniaturas reales de Google (nunca fondos de pantalla)
            patron = r'(https://encrypted-tbn0\.gstatic\.com/images\?q=tbn:[a-zA-Z0-9_\-]+)'
            encontrados = re.findall(patron, resp.text)
            
            # Quitar duplicados conservando el orden
            for link in encontrados:
                if link not in urls:
                    urls.append(link)
                if len(urls) >= max_resultados:
                    break
    except Exception as e:
        print(f"Error Google: {e}")

    return urls

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga la imagen para incrustarla en el documento Word."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.get(url_imagen, headers=headers, timeout=8)
        if resp.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(resp.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Error al descargar: {e}")
    return None
