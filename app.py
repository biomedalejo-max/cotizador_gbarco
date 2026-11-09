import streamlit as st
import datetime
import os
from buscador import buscar_con_serper, descargar_foto_garantizada
from generador_oferta import generar_documento_oferta, formato_cop
from generador_pdf import generar_documento_pdf

st.set_page_config(page_title="Cotizador G. Barco S.A.", page_icon="📋", layout="centered")

with st.sidebar:
    st.header("⚙️ Configuración")
    serper_api_key = st.text_input("🔑 Clave Google Serper:", type="password")

st.title("📋 Cotizador G. BARCO S.A.")
st.caption("Generador ágil de ofertas comerciales")

if "productos" not in st.session_state:
    st.session_state.productos = [{
        "referencia": "", "descripcion": "", "cantidad": 1,
        "precio_unitario": 0.0, "garantia": "12 meses",
        "visitas": "2 visitas/año", "imagen_path": None, "candidatas": []
    }]

with st.expander("📌 1. Datos Generales de la Oferta", expanded=True):
    col_num, col_fecha = st.columns(2)
    with col_num:
        numero_oferta = st.text_input("N° de Oferta (Manual):", value="BMZL201449")
    with col_fecha:
        fecha_hoy = datetime.date.today().strftime("%d de %B de %Y")
        ciudad_fecha = st.text_input("Ciudad y Fecha:", value=f"Manizales, {fecha_hoy}")

    cliente = st.text_input("Cliente / Razón Social:", placeholder="Ej. SERVICIOS ESPECIALES DE SALUD")
    nit = st.text_input("NIT:", placeholder="Ej. 8908075915")
    contacto = st.text_input("Contacto / Atención a:", placeholder="Ej. Dra. Vanessa Villamil")
    ciudad_cliente = st.text_input("Ciudad destino:", value="La Ciudad")

st.markdown("### 📦 2. Equipos a Cotizar")

for i, prod in enumerate(st.session_state.productos):
    st.markdown(f"--- \n#### Ítem #{i+1}")
    prod["referencia"] = st.text_input(f"Referencia:", value=prod["referencia"], key=f"ref_{i}")
    prod["descripcion"] = st.text_area(f"Descripción / Características:", value=prod["descripcion"], key=f"desc_{i}", height=70)
    
    col_c, col_p = st.columns(2)
    with col_c:
        prod["cantidad"] = st.number_input(f"Cantidad:", min_value=1, value=prod["cantidad"], step=1, key=f"cant_{i}")
    with col_p:
        prod["precio_unitario"] = st.number_input(f"Precio Unitario (COP sin IVA):", min_value=0.0, value=float(prod["precio_unitario"]), step=500000.0, key=f"prec_{i}")

    # Búsqueda
    col_btn_buscar, col_img_actual = st.columns([1, 1])
    with col_btn_buscar:
        if st.button(f"🔍 Buscar Fotos Web", key=f"btn_search_{i}"):
            termino = f"{prod['referencia']} {prod['descripcion']}".strip()
            if not termino:
                st.warning("⚠️ Escribe primero la Referencia o Descripción.")
            else:
                with st.spinner("Buscando en Google Imágenes..."):
                    fotos = buscar_con_serper(termino, serper_api_key, max_resultados=4)
                    prod["candidatas"] = fotos
                    if not fotos:
                        st.warning("No se encontraron fotos. Verifica la clave Serper o sube una foto manual.")

    with col_img_actual:
        if prod["imagen_path"] and os.path.exists(prod["imagen_path"]):
            st.image(prod["imagen_path"], caption="✅ Foto asignada con éxito", width=120)
        else:
            st.info("Sin foto asignada")

    # Galería interactiva
    if prod["candidatas"]:
        st.write("👉 **Toca 'Usar' en la foto correcta:**")
        cols_fotos = st.columns(len(prod["candidatas"]))
        for idx_foto, foto_item in enumerate(prod["candidatas"]):
            url_vista = foto_item.get("backup") or foto_item.get("original")
            with cols_fotos[idx_foto]:
                st.image(url_vista, use_container_width=True)
                if st.button("Usar", key=f"sel_{i}_{idx_foto}"):
                    with st.spinner("Guardando foto en el documento..."):
                        ruta_guardada = descargar_foto_garantizada(foto_item, indice_item=i)
                        if ruta_guardada:
                            prod["imagen_path"] = ruta_guardada
                            st.success("¡Foto guardada!")
                            st.rerun()

    with st.expander("📁 Subir foto manualmente desde la galería"):
        subida = st.file_uploader(f"Seleccionar archivo:", type=["png", "jpg", "jpeg"], key=f"upload_{i}")
        if subida is not None:
            r_manual = f"foto_manual_{i}.jpg"
            with open(r_manual, "wb") as f:
                f.write(subida.read())
            prod["imagen_path"] = os.path.abspath(r_manual)
            st.rerun()

col_add, col_del = st.columns(2)
with col_add:
    if st.button("➕ Agregar otro equipo"):
        st.session_state.productos.append({
            "referencia": "", "descripcion": "", "cantidad": 1,
            "precio_unitario": 0.0, "garantia": "12 meses",
            "visitas": "2 visitas/año", "imagen_path": None, "candidatas": []
        })
        st.rerun()

with col_del:
    if len(st.session_state.productos) > 1:
        if st.button("🗑️ Quitar último equipo"):
            st.session_state.productos.pop()
            st.rerun()

st.markdown("---")
st.markdown("### 💰 Resumen Financiero")
subtotal = sum(p["cantidad"] * p["precio_unitario"] for p in st.session_state.productos)
iva = subtotal * 0.19
total = subtotal + iva

c1, c2, c3 = st.columns(3)
c1.metric("Subtotal", formato_cop(subtotal))
c2.metric("IVA 19%", formato_cop(iva))
c3.metric("Total Oferta", formato_cop(total))

with st.expander("⚙️ Condiciones comerciales"):
    validez = st.text_input("Validez:", value="Pesos colombianos / Hasta 30 días.")
    entrega = st.text_input("Plazo de Entrega:", value="Cinco (5) días salvo previa venta.")
    forma_pago = st.text_input("Forma de Pago:", value="90 días.")

st.markdown("<br>", unsafe_allow_html=True)

# GENERACIÓN DE DOCUMENTOS
if st.button("📄 GENERAR COTIZACIÓN FINAL", type="primary", use_container_width=True):
    if not cliente.strip():
        st.error("Por favor ingresa al menos el Nombre del Cliente.")
    else:
        with st.spinner("Creando PDF y Word oficiales..."):
            datos = {
                "numero_oferta": numero_oferta,
                "ciudad_fecha": ciudad_fecha,
                "cliente": cliente,
                "nit": nit,
                "contacto": contacto,
                "ciudad_cliente": ciudad_cliente,
                "validez": validez,
                "entrega": entrega,
                "forma_pago": forma_pago
            }
            nombre_base = f"Oferta_{numero_oferta}_{cliente.replace(' ', '_')}"
            nom_docx = f"{nombre_base}.docx"
            nom_pdf = f"{nombre_base}.pdf"
            
            # Generar ambos documentos
            generar_documento_oferta(datos, st.session_state.productos, nom_docx)
            generar_documento_pdf(datos, st.session_state.productos, nom_pdf)
            
            st.success("✅ ¡Cotización generada exitosamente!")
            
            col_d1, col_d2 = st.columns(2)
            
            # Botón directo a PDF (Rojo destacado)
            with col_d1:
                with open(nom_pdf, "rb") as f_pdf:
                    st.download_button(
                        label="📕 Descargar PDF Oficial",
                        data=f_pdf,
                        file_name=nom_pdf,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
            
            # Botón Word
            with col_d2:
                with open(nom_docx, "rb") as f_word:
                    st.download_button(
                        label="📄 Descargar Word (.docx)",
                        data=f_word,
                        file_name=nom_docx,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
