import os
from pathlib import Path
from datetime import datetime


import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId


# ==============================
# CONFIGURACIÓN GENERAL
# ==============================

st.set_page_config(
    page_title="Inventario",
    page_icon="📦",
    layout="wide"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ==============================
# CONEXIÓN A MONGODB
# ==============================

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# ==============================
# ESTILOS
# ==============================

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.card {
    padding: 20px;
    border-radius: 18px;
    background-color: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.title-box {
    background: linear-gradient(90deg, #63e9f2, #fff3b0);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 25px;
}

.title-box h1 {
    color: #1f2937;
    margin: 0;
}

.title-box p {
    color: #374151;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# ENCABEZADO
# ==============================

st.markdown("""
<div class="title-box">
    <h1>📦 Inventario</h1>
    <p>Gestiona productos con MongoDB, Streamlit y Docker</p>
</div>
""", unsafe_allow_html=True)


# ==============================
# SIDEBAR
# ==============================

st.sidebar.title("⚙️ Panel de control")
menu = st.sidebar.radio(
    "Selecciona una sección",
    ["Dashboard", "Registrar producto", "Gestionar productos", "Subir archivos"]
)


# ==============================
# FUNCIONES
# ==============================

def obtener_productos():
    productos = list(collection.find())

    for producto in productos:
        producto["_id"] = str(producto["_id"])

    return productos


def convertir_dataframe(productos):
    if productos:
        return pd.DataFrame(productos)
    return pd.DataFrame()


# ==============================
# DASHBOARD
# ==============================

if menu == "Dashboard":

    productos = obtener_productos()
    df = convertir_dataframe(productos)

    st.subheader("📊 Resumen general")

    if df.empty:
        st.info("Aún no hay productos registrados.")
    else:
        total_productos = len(df)
        valor_total = df["precio"].sum()
        promedio_precio = df["precio"].mean()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de productos", total_productos)
        col2.metric("Valor total", f"S/ {valor_total:.2f}")
        col3.metric("Precio promedio", f"S/ {promedio_precio:.2f}")

        st.divider()

        col4, col5 = st.columns(2)

        with col4:
            st.subheader("Productos por categoría")
            fig = px.pie(
                df,
                names="categoria",
                title="Distribución por categoría"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col5:
            st.subheader("Productos por estado")
            fig2 = px.bar(
                df,
                x="estado",
                title="Cantidad por estado"
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Últimos productos registrados")
        st.dataframe(df.tail(5), use_container_width=True)


# ==============================
# REGISTRAR PRODUCTO
# ==============================

elif menu == "Registrar producto":

    st.subheader("➕ Registrar nuevo producto")

    with st.form("form_producto"):

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre del producto")
            categoria = st.selectbox(
                "Categoría",
                ["Tecnología", "Ropa", "Alimentos", "Accesorios", "Otros"]
            )
            precio = st.number_input("Precio", min_value=0.0)

        with col2:
            stock = st.number_input("Stock", min_value=0, step=1)
            estado = st.selectbox(
                "Estado",
                ["Disponible", "Bajo stock", "Agotado"]
            )
            descripcion = st.text_area("Descripción")

        guardar = st.form_submit_button("Guardar producto")

        if guardar:
            if nombre.strip() == "":
                st.error("El nombre del producto es obligatorio.")
            else:
                producto = {
                    "nombre": nombre,
                    "categoria": categoria,
                    "precio": precio,
                    "stock": stock,
                    "estado": estado,
                    "descripcion": descripcion,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                collection.insert_one(producto)
                st.success("Producto registrado correctamente.")


# ==============================
# GESTIONAR PRODUCTOS
# ==============================

elif menu == "Gestionar productos":

    st.subheader("🛠️ Gestionar productos")

    productos = obtener_productos()
    df = convertir_dataframe(productos)

    if df.empty:
        st.info("No hay productos registrados.")
    else:
        busqueda = st.text_input("🔎 Buscar producto por nombre")

        if busqueda:
            df_filtrado = df[df["nombre"].str.contains(busqueda, case=False, na=False)]
        else:
            df_filtrado = df

        st.dataframe(df_filtrado, use_container_width=True)

        st.divider()

        st.subheader("✏️ Actualizar producto")

        producto_id = st.text_input("ID del producto a actualizar")

        nuevo_nombre = st.text_input("Nuevo nombre")
        nuevo_precio = st.number_input("Nuevo precio", min_value=0.0)
        nuevo_stock = st.number_input("Nuevo stock", min_value=0, step=1)
        nuevo_estado = st.selectbox(
            "Nuevo estado",
            ["Disponible", "Bajo stock", "Agotado"]
        )

        if st.button("Actualizar producto"):
            try:
                collection.update_one(
                    {"_id": ObjectId(producto_id)},
                    {
                        "$set": {
                            "nombre": nuevo_nombre,
                            "precio": nuevo_precio,
                            "stock": nuevo_stock,
                            "estado": nuevo_estado
                        }
                    }
                )

                st.success("Producto actualizado correctamente.")
            except:
                st.error("ID inválido. Copia el ID exactamente como aparece en la tabla.")

        st.divider()

        st.subheader("🗑️ Eliminar producto")

        eliminar_id = st.text_input("ID del producto a eliminar")

        if st.button("Eliminar producto"):
            try:
                collection.delete_one({"_id": ObjectId(eliminar_id)})
                st.warning("Producto eliminado correctamente.")
            except:
                st.error("ID inválido. Copia el ID exactamente como aparece en la tabla.")


# ==============================
# SUBIR ARCHIVOS
# ==============================

elif menu == "Subir archivos":

    st.subheader("📂 Subir archivos del inventario")

    archivo = st.file_uploader(
        "Sube una imagen, Excel, PDF o archivo relacionado al producto"
    )

    if archivo is not None:
        ruta_archivo = UPLOAD_DIR / archivo.name

        with open(ruta_archivo, "wb") as f:
            f.write(archivo.getbuffer())

        st.success(f"Archivo guardado correctamente: {ruta_archivo}")

    st.divider()

    st.subheader("📁 Archivos guardados")

    archivos = os.listdir(UPLOAD_DIR)

    if archivos:
        for archivo in archivos:
            st.write(f"📌 {archivo}")
    else:
        st.info("Todavía no hay archivos subidos.")
