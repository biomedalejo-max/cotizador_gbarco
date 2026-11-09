import os
import requests
import tempfile
import urllib.parse

HEADERS = {
    "User-Agent": "CotizadorBarco/1.0"
}

def buscar_con_serper(termino: str, api_key: str, max_resultados: int = 4) -> list:
    """Busca en Google Imágenes usando la API de Serper (100% infalible en la nube)."""
    if not api_key:
        return []
    
    url = "https://google.serper.dev/images"
    payload = {
        "q": termino.strip(),
        "gl": "co",  # Región Colombia
        "hl": "es",  # Idioma español
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
            # Extraer las URLs de las fotos de Google
            return [img.get("imageUrl") for img in datos.get("images", []) if img.get("imageUrl")]
    except Exception as e:
        print(f"Error Serper: {e}")
        
    return []

def buscar_en_wikimedia(termino: str, max_resultados: int = 4) -> list:
    """Buscador público de respaldo libre de bloqueos."""
    try:
        q = urllib.parse.quote_plus(termino)
        url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={q}&gsrlimit={max_resultados}&prop=imageinfo&iiprop=url&format=json"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            paginas = data.get("query", {}).get("pages", {})
            urls = []
            for p in paginas.values():
                info = p.get("imageinfo", [{}])[0]
                u = info.get("url")
                if u and not u.endswith(".svg"):
                    urls.append(u)
            return urls
    except Exception:
        pass
    return []

def buscar_inteligente(referencia: str, descripcion: str, api_key: str = "", max_resultados: int = 4) -> tuple:
    ref = (referencia or "").strip()
    desc = (descripcion or "").strip()
    
    # Armar los términos ordenados
    terminos = []
    if ref and desc:
        terminos.append(f"{ref} {desc}")
    if ref:
        terminos.append(ref)
    if desc:
        terminos.append(desc)

    for term in terminos:
        # 1. Si pusiste la clave de Serper (Google Imágenes real)
        if api_key:
            fotos = buscar_con_serper(term, api_key, max_resultados)
            if fotos:
                return fotos, f"Google ('{term[:25]}...')"
        
        # 2. Respaldo sin clave
        fotos = buscar_en_wikimedia(term, max_resultados)
        if fotos:
            return fotos, f"Buscador libre ('{term[:25]}...')"

    return [], "Sin resultados"

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga la imagen seleccionada y la prepara para el documento Word."""
    try:
        resp = requests.get(url_imagen, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if resp.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(resp.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Error al descargar foto: {e}")
    return None
