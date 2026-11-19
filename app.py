import streamlit as st
import datetime
import os
from buscador import (
    buscar_con_serper,
    descargar_foto_garantizada
)
from generador_oferta import (
    generar_documento_oferta,
    formato_cop
)
from generador_pdf import (
    generar_documento_pdf
)

st.set_page_config(
    page_title="Cotizador G. Barco S.A.",
    page_icon="📋",
    layout="centered"
)

with st.sidebar:
    st.header("⚙️ Configuración")
    serper_api_key = st.text_input(
        "🔑 Clave Google Serper:",
        type="password"
    )

st.title("📋 Cotizador G. BARCO S.A.")
st.caption("Generador ágil de ofertas comerciales")

if "productos" not in st.session_state:
    st.session_state.productos = [{
        "referencia": "",
        "descripcion": "",
        "cantidad": 1,
        "precio_unitario": 0.0,
        "garantia": "12 meses",
        "visitas": "2 visitas/año",
        "imagen_path": None,
        "candidatas": []
    }]

# 1. ENCABEZADO
with st.expander("📌 1. Datos del Cliente y Oferta", expanded=True):
    col_num, col_fecha = st.columns(2)
    with col_num:
        numero_oferta = st.text_input(
            "N° de Oferta (Manual):",
            value="BMZL201449"
        )
    with col_fecha:
        meses = {
            1: "enero", 2: "febrero", 3: "marzo",
            4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre",
            10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        hoy = datetime.date.today()
        f_esp = f"{hoy.day} de {meses[hoy.month]} de {hoy.year}"
        ciudad_fecha = st.text_input(
            "Ciudad y Fecha:",
            value=f"Manizales, {f_esp}"
        )

    cliente = st.text_input(
        "Cliente / Razón Social:",
        placeholder="Ej. CLINICA DE FRACTURAS SAS"
    )
    nit = st.text_input(
        "NIT:",
        placeholder="Ej. 8914117430"
    )
    contacto = st.text_input(
        "Contacto / Atención a:",
        placeholder="Ej. Ing. Jorfan Pabon"
    )
    ciudad_cliente = st.text_input(
        "Ciudad destino:",
        value="Pereira"
    )

# 2. PRODUCTOS
st.markdown("### 📦 2. Equipos a Cotizar")

for i, prod in enumerate(st.session_state.productos):
    st.markdown(f"--- \n#### Ítem #{i+1}")
    prod["referencia"] = st.text_input(
        f"Referencia:",
        value=prod["referencia"],
        key=f"ref_{i}"
    )
    prod["descripcion"] = st.text_area(
        f"Descripción / Características:",
        value=prod["descripcion"],
        key=f"desc_{i}",
        height=70
    )
    
    col_c, col_p = st.columns(2)
    with col_c:
        prod["cantidad"] = st.number_input(
            f"Cantidad:",
            min_value=1,
            value=prod["cantidad"],
            step=1,
            key=f"cant_{i}"
        )
    with col_p:
        prod["precio_unitario"] = st.number_input(
            f"Precio Unitario (COP sin IVA):",
            min_value=0.0,
            value=float(prod["precio_unitario"]),
            step=500000.0,
            key=f"prec_{i}"
        )

    # 👇 CASILLAS DE GARANTÍA Y VISITAS POR EQUIPO
    col_g, col_v = st.columns(2)
    with col_g:
        prod["garantia"] = st.text_input(
            f"Garantía del Ítem #{i+1}:",
            value=prod.get("garantia", "12 meses"),
            key=f"gar_{i}"
        )
    with col_v:
        prod["visitas"] = st.text_input(
            f"Visitas/Año Ítem #{i+1}:",
            value=prod.get("visitas", "2 visitas/año"),
            key=f"vis_{i}"
        )

    # Búsqueda de foto
    col_btn, col_img = st.columns([1, 1])
    with col_btn:
        if st.button(f"🔍 Buscar Fotos Web", key=f"btn_search_{i}"):
            termino = f"{prod['referencia']} {prod['descripcion']}".strip()
            if not termino:
                st.warning("⚠️ Escribe la Referencia o Descripción.")
            else:
                with st.spinner("Buscando en Google..."):
                    fotos = buscar_con_serper(
                        termino,
                        serper_api_key,
                        max_resultados=4
                    )
                    prod["candidatas"] = fotos
                    if not fotos:
                        st.warning("No se encontraron fotos.")

    with col_img:
        if prod["imagen_path"] and os.path.exists(prod["imagen_path"]):
            st.image(
                prod["imagen_path"],
                caption="✅ Foto asignada",
                width=120
            )
        else:
            st.info("Sin foto asignada")

    if prod["candidatas"]:
        st.write("👉 **Toca 'Usar' en la foto correcta:**")
        cols_fotos = st.columns(len(prod["candidatas"]))
        for idx_foto, foto_item in enumerate(prod["candidatas"]):
            url_vista = foto_item.get("backup") or foto_item.get("original")
            with cols_fotos[idx_foto]:
                st.image(url_vista, use_container_width=True)
                if st.button("Usar", key=f"sel_{i}_{idx_foto}"):
                    with st.spinner("Guardando foto..."):
                        ruta_g = descargar_foto_garantizada(
                            foto_item,
                            indice_item=i
                        )
                        if ruta_g:
                            prod["imagen_path"] = ruta_g
                            st.rerun()

    with st.expander("📁 Subir foto manual"):
        subida = st.file_uploader(
            f"Subir imagen:",
            type=["png", "jpg", "jpeg"],
            key=f"upload_{i}"
        )
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
            "referencia": "",
            "descripcion": "",
            "cantidad": 1,
            "precio_unitario": 0.0,
            "garantia": "12 meses",
            "visitas": "2 visitas/año",
            "imagen_path": None,
            "candidatas": []
        })
        st.rerun()

with col_del:
    if len(st.session_state.productos) > 1:
        if st.button("🗑️ Quitar último equipo"):
            st.session_state.productos.pop()
            st.rerun()

# 3. RESUMEN FINANCIERO
st.markdown("---")
st.markdown("### 💰 Resumen Financiero")
subtotal = sum(
    p["cantidad"] * p["precio_unitario"]
    for p in st.session_state.productos
)
iva = subtotal * 0.19
total = subtotal + iva

c1, c2, c3 = st.columns(3)
c1.metric("Subtotal", formato_cop(subtotal))
c2.metric("IVA 19%", formato_cop(iva))
c3.metric("Total Oferta", formato_cop(total))

# 👇 4. CONDICIONES COMERCIALES (VISIBLES Y EDITABLES DIRECTAMENTE)
st.markdown("---")
st.markdown("### 📋 4. Condiciones Comerciales")

col_ent, col_gar_gen = st.columns(2)
with col_ent:
    entrega = st.text_input(
        "⏱️ Plazo de Entrega:",
        value="Cinco (5) días salvo previa venta."
    )
with col_gar_gen:
    garantia_texto = st.text_input(
        "🛡️ Cláusula de Garantía (General):",
        value="Doce (12) meses contra defectos de fabricación exclusivamente."
    )

col_val, col_pag = st.columns(2)
with col_val:
    validez = st.text_input(
        "📅 Validez de la Oferta:",
        value="Pesos colombianos / Hasta 30 días."
    )
with col_pag:
    forma_pago = st.text_input(
        "💳 Forma de Pago:",
        value="90 días."
    )

st.markdown("<br>", unsafe_allow_html=True)

# GENERACIÓN
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
                "forma_pago": forma_pago,
                "garantia_texto": garantia_texto
            }
            nombre_base = f"Oferta_{numero_oferta}_{cliente.replace(' ', '_')}"
            nom_docx = f"{nombre_base}.docx"
            nom_pdf = f"{nombre_base}.pdf"
            
            generar_documento_oferta(
                datos,
                st.session_state.productos,
                nom_docx
            )
            generar_documento_pdf(
                datos,
                st.session_state.productos,
                nom_pdf
            )
            
            st.success("✅ ¡Cotización generada exitosamente!")
            
            col_d1, col_d2 = st.columns(2)
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
            with col_d2:
                with open(nom_docx, "rb") as f_word:
                    st.download_button(
                        label="📄 Descargar Word (.docx)",
                        data=f_word,
                        file_name=nom_docx,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
