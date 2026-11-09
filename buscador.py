import os
import re
import urllib.parse
import requests
import tempfile

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

def consultar_motor_imagenes(termino: str, max_resultados: int = 4) -> list:
    """Busca en el motor web sin bloqueos de servidor."""
    if not termino or not termino.strip():
        return []
    
    urls = []
    try:
        q_enc = urllib.parse.quote_plus(termino.strip())
        url = f"https://images.search.yahoo.com/search/images?p={q_enc}"
        resp = requests.get(url, headers=HEADERS, timeout=7)
        
        if resp.status_code == 200:
            # 1. Extraer enlaces originales de imágenes
            enlaces_directos = re.findall(r'imgurl=([a-zA-Z0-9%_\-\.\/\:]+)', resp.text)
            for raw in enlaces_directos:
                limpio = urllib.parse.unquote(raw)
                if limpio.startswith("http") and not limpio.lower().endswith('.svg'):
                    if limpio not in urls:
                        urls.append(limpio)
                if len(urls) >= max_resultados:
                    break
            
            # 2. Si las fotos originales fallan, extraer miniaturas CDN de alta disponibilidad
            if len(urls) < max_resultados:
                miniaturas = re.findall(r'(https://tse\d\.mm\.bing\.net/th\?id=[a-zA-Z0-9_\-\.]+)', resp.text)
                for m in miniaturas:
                    if m not in urls:
                        urls.append(m)
                    if len(urls) >= max_resultados:
                        break
    except Exception as e:
        print(f"Error consultando motor: {e}")
        
    return urls

def buscar_inteligente(referencia: str, descripcion: str, max_resultados: int = 4) -> tuple:
    """
    REGLA EN CASCADA:
    1. Si hay Referencia, busca primero por Referencia.
    2. Si no encuentra nada, busca por Descripción.
    3. Si ambas están presentes, prueba combinación.
    Retorna: (lista_de_urls, motivo_exito)
    """
    ref = (referencia or "").strip()
    desc = (descripcion or "").strip()

    # 1. Buscar primero por Referencia
    if ref:
        fotos = consultar_motor_imagenes(f"{ref} equipo medico", max_resultados)
        if not fotos:
            fotos = consultar_motor_imagenes(ref, max_resultados)
        if fotos:
            return fotos, f"Referencia ('{ref}')"

    # 2. Si no encontró por Referencia, buscar por Descripción
    if desc:
        # Tomar las primeras palabras clave principales de la descripción
        palabras_clave = " ".join(desc.split()[:7])
        fotos = consultar_motor_imagenes(palabras_clave, max_resultados)
        if fotos:
            return fotos, f"Descripción ('{palabras_clave}')"

    # 3. Intento combinado si ambos tienen datos
    if ref and desc:
        combo = f"{ref} {desc.split()[0]}"
        fotos = consultar_motor_imagenes(combo, max_resultados)
        if fotos:
            return fotos, f"Combinación ('{combo}')"

    return [], "Sin resultados"

def descargar_imagen_temporal(url_imagen: str) -> str:
    """Descarga la imagen para meterla al documento Word."""
    try:
        resp = requests.get(url_imagen, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(resp.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
    return None
