import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from bson.objectid import ObjectId

from db import collection


st.set_page_config(
    page_title="Inventario Creativo",
    page_icon="📦",
    layout="wide"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

if not os.getenv("MONGO_URL"):
    st.error("No se encontró la variable MONGO_URL en Railway.")
    st.stop()


st.title("📦 Inventario Creativo")
st.write("Aplicación desplegada con Streamlit, Docker, Railway y MongoDB.")

menu = st.sidebar.radio(
    "Menú",
    ["Dashboard", "Registrar producto", "Gestionar productos", "Subir archivos"]
)


def obtener_productos():
    productos = list(collection.find())
    for producto in productos:
        producto["_id"] = str(producto["_id"])
    return productos


if menu == "Dashboard":
    st.subheader("📊 Dashboard")

    productos = obtener_productos()

    if not productos:
        st.info("Aún no hay productos registrados.")
    else:
        df = pd.DataFrame(productos)

        col1, col2, col3 = st.columns(3)
        col1.metric("Productos", len(df))
        col2.metric("Valor total", f"S/ {df['precio'].sum():.2f}")
        col3.metric("Stock total", int(df["stock"].sum()))

        st.divider()

        fig = px.bar(
            df,
            x="nombre",
            y="stock",
            color="categoria",
            title="Stock por producto"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)


elif menu == "Registrar producto":
    st.subheader("➕ Registrar producto")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre del producto")
        categoria = st.selectbox(
            "Categoría",
            ["Tecnología", "Ropa", "Alimentos", "Accesorios", "Otros"]
        )
        precio = st.number_input("Precio", min_value=0.0)
        stock = st.number_input("Stock", min_value=0, step=1)
        estado = st.selectbox(
            "Estado",
            ["Disponible", "Bajo stock", "Agotado"]
        )
        descripcion = st.text_area("Descripción")

        guardar = st.form_submit_button("Guardar")

        if guardar:
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


elif menu == "Gestionar productos":
    st.subheader("🛠️ Gestionar productos")

    productos = obtener_productos()

    if not productos:
        st.info("No hay productos registrados.")
    else:
        df = pd.DataFrame(productos)
        st.dataframe(df, use_container_width=True)

        st.divider()

        st.subheader("✏️ Actualizar producto")

        producto_id = st.text_input("ID del producto")
        nuevo_nombre = st.text_input("Nuevo nombre")
        nuevo_precio = st.number_input("Nuevo precio", min_value=0.0)
        nuevo_stock = st.number_input("Nuevo stock", min_value=0, step=1)

        if st.button("Actualizar"):
            try:
                collection.update_one(
                    {"_id": ObjectId(producto_id)},
                    {
                        "$set": {
                            "nombre": nuevo_nombre,
                            "precio": nuevo_precio,
                            "stock": nuevo_stock
                        }
                    }
                )
                st.success("Producto actualizado.")
            except:
                st.error("ID inválido.")

        st.divider()

        st.subheader("🗑️ Eliminar producto")

        eliminar_id = st.text_input("ID a eliminar")

        if st.button("Eliminar"):
            try:
                collection.delete_one({"_id": ObjectId(eliminar_id)})
                st.warning("Producto eliminado.")
            except:
                st.error("ID inválido.")


elif menu == "Subir archivos":
    st.subheader("📂 Subir archivos")

    archivo = st.file_uploader("Selecciona un archivo")

    if archivo is not None:
        ruta = UPLOAD_DIR / archivo.name

        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())

        st.success(f"Archivo guardado: {ruta}")

    st.subheader("Archivos actuales")

    archivos = os.listdir(UPLOAD_DIR)

    if archivos:
        st.write(archivos)
    else:
        st.info("No hay archivos subidos.")
