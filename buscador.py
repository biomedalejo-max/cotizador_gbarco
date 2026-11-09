import os
import requests
import io
from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def buscar_con_serper(termino: str, api_key: str, max_resultados: int = 4) -> list:
    """Busca en Google y extrae la foto original y la miniatura de respaldo."""
    if not api_key:
        return []
    
    url = "https://google.serper.dev/images"
    payload = {
        "q": termino.strip(),
        "gl": "co",
        "hl": "es",
        "num": max_resultados
    }
    headers = {
        "X-API-KEY": api_key.strip(),
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=6)
        if resp.status_code == 200:
            datos = resp.json()
            lista_fotos = []
            for img in datos.get("images", []):
                # Guardamos tanto la URL original como la de respaldo de Google CDN
                url_ppal = img.get("imageUrl")
                url_respaldo = img.get("thumbnailUrl")
                if url_ppal or url_respaldo:
                    lista_fotos.append({
                        "original": url_ppal or url_respaldo,
                        "backup": url_respaldo or url_ppal
                    })
            return lista_fotos[:max_resultados]
    except Exception as e:
        print(f"Error Serper: {e}")
        
    return []

def descargar_foto_garantizada(foto_obj, indice_item: int) -> str:
    """Descarga la foto; si el sitio web original bloquea, usa el respaldo de Google."""
    if isinstance(foto_obj, str):
        urls_a_probar = [foto_obj]
    else:
        urls_a_probar = [foto_obj.get("original"), foto_obj.get("backup")]

    ruta_destino = f"foto_equipo_{indice_item}.jpg"

    for url in urls_a_probar:
        if not url:
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200 and len(r.content) > 500:
                # Convertir a JPG puro
                img = Image.open(io.BytesIO(r.content))
                img = img.convert("RGB")
                img.thumbnail((500, 500))  # Tamaño óptimo
                img.save(ruta_destino, "JPEG", quality=88)
                return os.path.abspath(ruta_destino)
        except Exception:
            continue

    return None
