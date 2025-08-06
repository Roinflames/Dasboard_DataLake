import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime
import re
import sys
import os
# Añadir la carpeta padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Importar las variables de conexión desde tu archivo .py
from credenciales import pg_user, pg_password, pg_puerto, pg_host, pg_schema, pg_database

# Configuración de la página
st.set_page_config(
    page_title="Participación Académica e I+D+i con Pertinencia Territorial",
    page_icon="🎓",
    # layout="wide"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #7B2CBF 0%, #9D4EDD 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
    }
    .section-header {
        background-color: #E0AAFF;
        color: #240046;
        padding: 10px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        font-weight: bold;
    }
    .info-box {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
    }
    .required {
        color: #DC3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def validate_email(email):
    """Validar formato de email - acepta cualquier dominio válido"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def connect_to_database():
    """Conectar a la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(
            host=pg_host,
            port=pg_puerto,
            database=pg_database,
            user=pg_user,
            password=pg_password
        )
        return connection
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {str(e)}")
        return None

def insert_data_to_db(data):
    """Insertar datos en la base de datos en el esquema dev"""
    connection = connect_to_database()
    if connection is None:
        return False
    
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Insert con el esquema "dev" especificado
        insert_query = f"""
        INSERT INTO {pg_schema}.participacion_academica (
            nombre_completo, correo_institucional, unidad_academica, grado_academico,
            participa_comite_nacional, comites_nacionales, participacion_patrocinada_nacional,
            participa_comite_internacional, comites_internacionales, participacion_patrocinada_internacional,
            desarrolla_actividades_territoriales, descripcion_actividades_territoriales
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        cursor.execute(insert_query, data)
        connection.commit()
        return True
        
    except psycopg2.IntegrityError as e:
        st.error("Este correo electrónico ya está registrado en el sistema.")
        if connection:
            connection.rollback()
        return False
    except Exception as e:
        st.error(f"Error al guardar los datos: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Encabezado principal
st.markdown("""
<div class="main-header">
    <h1>🎓 Participación Académica e I+D+i con Pertinencia Territorial</h1>
    <p>Universidad Tecnológica Metropolitana (UTEM)</p>
</div>
""", unsafe_allow_html=True)

# Información del formulario
st.success("""
**INFORMACIÓN DEL FORMULARIO**
**Objetivo:** Recopilar información sobre participación en comités, comisiones y mesas de trabajo, así como actividades de I+D+i con pertinencia territorial.
**Uso:** Fortalecer el registro institucional y alimentar el diagnóstico del Proyecto Basal FIUT.
""")

# Inicializar session state
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Formulario principal
st.markdown('<div class="section-header">Sección 1: Datos Generales</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    nombre_completo = st.text_input(
        "Nombre completo *",
        placeholder="Ingrese su nombre completo",
        help="Escriba su nombre y apellidos completos"
    )
    
    unidad_academica = st.text_input(
        "Unidad académica (Departamento y/o Facultad) *",
        placeholder="Ej: Departamento de Biotecnología, FCNMMA",
        help="Indique su departamento y facultad de pertenencia"
    )

with col2:
    correo_institucional = st.text_input(
        "Correo electrónico *",
        placeholder="nombre@ejemplo.com",
        help="Ingrese su correo electrónico válido"
    )
    
    grado_academico = st.selectbox(
        "Indique el Grado Académico (el más alto) *",
        options=["", "Doctor", "Magíster", "Licenciado/Título Profesional"],
        help="Seleccione su máximo grado académico alcanzado"
    )

# Sección 2: Participación en Comités Nacionales
st.markdown('<div class="section-header">Sección 2: Participación en Comités y Comisiones Nacionales</div>', unsafe_allow_html=True)

participa_nacional = st.radio(
    "¿Participa actualmente en algún comité o comisión nacional? *",
    options=["No", "Sí"],
    index=None,
    help="Indique si participa en comités, comisiones o mesas de trabajo a nivel nacional"
)

# Variables para comités nacionales
comites_nacionales = ""
participacion_patrocinada_nacional = "No"

if participa_nacional == "Sí":
    comites_nacionales = st.text_area(
        "Indique el/los comités o comisiones nacionales en los que participa: *",
        placeholder="Describa detalladamente los comités, comisiones o mesas de trabajo nacionales...",
        height=100,
        help="Liste todos los comités nacionales en los que participa actualmente"
    )
    
    participacion_patrocinada_nacional = st.radio(
        "¿Esa participación está patrocinada por la Universidad? *",
        options=["No", "Sí"],
        help="Indique si la UTEM patrocina o respalda oficialmente su participación"
    )

# Sección 3: Participación en Comités Internacionales
st.markdown('<div class="section-header">Sección 3: Participación en Comités y Comisiones Internacionales</div>', unsafe_allow_html=True)

participa_internacional = st.radio(
    "¿Participa actualmente en algún comité o comisión internacional? *",
    options=["No", "Sí"],
    index=None,
    help="Indique si participa en comités, comisiones o mesas de trabajo a nivel internacional"
)

# Variables para comités internacionales
comites_internacionales = ""
participacion_patrocinada_internacional = "No"

if participa_internacional == "Sí":
    comites_internacionales = st.text_area(
        "Indique el/los comités o comisiones internacionales en los que participa: *",
        placeholder="Describa detalladamente los comités, comisiones o mesas de trabajo internacionales...",
        height=100,
        help="Liste todos los comités internacionales en los que participa actualmente"
    )
    
    participacion_patrocinada_internacional = st.radio(
        "¿Esa participación está patrocinada por la Universidad? *",
        options=["No", "Sí"],
        help="Indique si la UTEM patrocina o respalda oficialmente su participación"
    )

# Sección 4: Actividades de I+D+i con Pertinencia Territorial
st.markdown('<div class="section-header">Sección 4: Actividades de I+D+i con Pertinencia Territorial</div>', unsafe_allow_html=True)

desarrolla_actividades = st.radio(
    "¿Desarrolla actualmente actividades de investigación, desarrollo o innovación (I+D+i) con pertinencia territorial? *",
    options=["No", "Sí"],
    index=None,
    help="Indique si desarrolla proyectos o actividades de I+D+i que tengan impacto o aplicación territorial específica"
)

descripcion_actividades = ""
if desarrolla_actividades == "Sí":
    descripcion_actividades = st.text_area(
        "Describa brevemente las actividades de I+D+i con pertinencia territorial que desarrolla:",
        placeholder="Describa los proyectos, iniciativas o actividades de I+D+i que tienen impacto territorial...",
        height=120,
        help="Proporcione detalles sobre sus actividades de investigación con aplicación territorial"
    )

# Botón de envío
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("📤 Enviar Formulario", use_container_width=True, type="primary"):
        # Validaciones
        errors = []
        
        if not nombre_completo.strip():
            errors.append("El nombre completo es obligatorio")
        
        if not correo_institucional.strip():
            errors.append("El correo electrónico es obligatorio")
        elif not validate_email(correo_institucional):
            errors.append("El formato del correo electrónico no es válido")
        
        if not unidad_academica.strip():
            errors.append("La unidad académica es obligatoria")
        
        if not grado_academico:
            errors.append("Debe seleccionar su grado académico")
        
        if participa_nacional is None:
            errors.append("Debe indicar si participa en comités nacionales")
        
        if participa_internacional is None:
            errors.append("Debe indicar si participa en comités internacionales")
        
        if desarrolla_actividades is None:
            errors.append("Debe indicar si desarrolla actividades de I+D+i territoriales")
        
        if participa_nacional == "Sí" and not comites_nacionales.strip():
            errors.append("Debe especificar los comités nacionales en los que participa")
        
        if participa_internacional == "Sí" and not comites_internacionales.strip():
            errors.append("Debe especificar los comités internacionales en los que participa")
        
        # Mostrar errores si existen
        if errors:
            st.error("Por favor, corrija los siguientes errores:")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Preparar datos para insertar
            data_to_insert = (
                nombre_completo.strip(),
                correo_institucional.strip().lower(),
                unidad_academica.strip(),
                grado_academico,
                participa_nacional == "Sí",
                comites_nacionales.strip() if comites_nacionales else None,
                participacion_patrocinada_nacional == "Sí" if participa_nacional == "Sí" else None,
                participa_internacional == "Sí",
                comites_internacionales.strip() if comites_internacionales else None,
                participacion_patrocinada_internacional == "Sí" if participa_internacional == "Sí" else None,
                desarrolla_actividades == "Sí",
                descripcion_actividades.strip() if descripcion_actividades else None
            )
            
            # Insertar en base de datos
            if insert_data_to_db(data_to_insert):
                st.success("✅ ¡Formulario enviado exitosamente!")
                st.balloons()
                st.session_state.form_submitted = True
                
                # Mostrar resumen de respuestas
                st.markdown("### Resumen de su participación:")
                
                with st.expander("Ver resumen de respuestas", expanded=True):
                    st.write(f"**Nombre:** {nombre_completo}")
                    st.write(f"**Correo:** {correo_institucional}")
                    st.write(f"**Unidad Académica:** {unidad_academica}")
                    st.write(f"**Grado Académico:** {grado_academico}")
                    st.write(f"**Participa en comités nacionales:** {participa_nacional}")
                    if participa_nacional == "Sí":
                        st.write(f"**Comités nacionales:** {comites_nacionales}")
                        st.write(f"**Patrocinado nacionalmente:** {participacion_patrocinada_nacional}")
                    st.write(f"**Participa en comités internacionales:** {participa_internacional}")
                    if participa_internacional == "Sí":
                        st.write(f"**Comités internacionales:** {comites_internacionales}")
                        st.write(f"**Patrocinado internacionalmente:** {participacion_patrocinada_internacional}")
                    st.write(f"**Desarrolla actividades I+D+i territoriales:** {desarrolla_actividades}")
                    if desarrolla_actividades == "Sí":
                        st.write(f"**Descripción actividades:** {descripcion_actividades}")
                
                st.info("Su información ha sido registrada correctamente. Gracias por su participación en el fortalecimiento del diagnóstico institucional.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6C757D; font-size: 12px; margin-top: 30px;'>
    <p>© 2025 Universidad Tecnológica Metropolitana (UTEM) - Proyecto FIUT</p>
    <p>Sistema desarrollado para el fortalecimiento de capacidades institucionales en I+D+i+e</p>
</div>
""", unsafe_allow_html=True)