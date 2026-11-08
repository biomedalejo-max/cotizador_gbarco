import os
import re
import urllib.parse
import requests
import tempfile

def buscar_imagenes_producto(termino_busqueda: str, max_resultados: int = 4) -> list:
    """Busca imágenes en la web sin bloqueos en la nube."""
    if not termino_busqueda or not termino_busqueda.strip():
        return []
    
    urls = []
    
    # 1. Búsqueda principal directa (Bing sin bloqueos de servidor)
    try:
        query = urllib.parse.quote_plus(termino_busqueda)
        url_bing = f"https://www.bing.com/images/async?q={query}&count=15&first=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url_bing, headers=headers, timeout=6)
        if resp.status_code == 200:
            # Extraer enlaces de las fotos
            enlaces = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', resp.text)
            for link in enlaces:
                urls.append(link)
                if len(urls) >= max_resultados:
                    break
    except Exception as e:
        print(f"Error Bing: {e}")

    # Si encontramos imágenes, las devolvemos
    if urls:
        return urls

    # 2. Respaldo por si acaso
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.images(keywords=termino_busqueda, max_results=max_resultados))
            urls = [r.get('image') for r in resultados if r.get('image')]
            return urls
    except Exception:
        pass

    return urls

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga la imagen para meterla al documento Word."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
