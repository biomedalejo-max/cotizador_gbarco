import streamlit as st
import datetime
import os
from buscador import buscar_inteligente, descargar_imagen_temporal
from generador_oferta import generar_documento_oferta, formato_cop

st.set_page_config(page_title="Cotizador G. Barco S.A.", page_icon="📋", layout="centered")

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

    # Búsqueda inteligente en cascada
    col_btn_buscar, col_img_actual = st.columns([1, 1])
    with col_btn_buscar:
        if st.button(f"🔍 Buscar Imagen Web", key=f"btn_search_{i}"):
            if not prod["referencia"].strip() and not prod["descripcion"].strip():
                st.warning("⚠️ Escribe al menos la Referencia o la Descripción del equipo.")
            else:
                with st.spinner("Buscando en la web..."):
                    fotos, motivo = buscar_inteligente(prod["referencia"], prod["descripcion"], max_resultados=4)
                    prod["candidatas"] = fotos
                    if fotos:
                        st.success(f"Fotos encontradas por: {motivo}")
                    else:
                        st.info("No se encontraron fotos automáticas. Puedes subir una foto abajo.")

    with col_img_actual:
        if prod["imagen_path"]:
            st.image(prod["imagen_path"], caption="Imagen asignada", width=120)
        else:
            st.info("Sin imagen")

    if prod["candidatas"]:
        st.write("👉 **Toca la foto correcta para asignarla:**")
        cols_fotos = st.columns(len(prod["candidatas"]))
        for idx_foto, url_f in enumerate(prod["candidatas"]):
            with cols_fotos[idx_foto]:
                st.image(url_f, use_container_width=True)
                if st.button("Usar", key=f"sel_{i}_{idx_foto}"):
                    ruta_temp = descargar_imagen_temporal(url_f)
                    if ruta_temp:
                        prod["imagen_path"] = ruta_temp
                        st.rerun()

    subida = st.file_uploader(f"O subir foto desde tu teléfono:", type=["png", "jpg", "jpeg"], key=f"upload_{i}")
    if subida is not None:
        import tempfile
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        t_file.write(subida.read())
        prod["imagen_path"] = t_file.name

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
if st.button("📄 GENERAR COTIZACIÓN FINAL", type="primary", use_container_width=True):
    if not cliente.strip():
        st.error("Por favor ingresa al menos el Nombre del Cliente.")
    else:
        datos = {
            "numero_oferta": numero_oferta, "ciudad_fecha": ciudad_fecha,
            "cliente": cliente, "nit": nit, "contacto": contacto,
            "ciudad_cliente": ciudad_cliente, "validez": validez,
            "entrega": entrega, "forma_pago": delivery_days := forma_pago
        }
        nom = f"Oferta_{numero_oferta}_{cliente.replace(' ', '_')}.docx"
        generar_documento_oferta(datos, st.session_state.productos, nom)
        with open(nom, "rb") as f:
            st.success("✅ ¡Cotización generada!")
            st.download_button("📥 Descargar Documento Word (.docx)", f, file_name=nom, use_container_width=True)
