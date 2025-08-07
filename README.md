# dashboard_fiut_test
dashboard_fiut_test

pipenv shell
streamlit run streamlit_dashboard.py  

ps aux | grep streamlit
<PID>299141
kill <PID>
nohup streamlit run streamlit_dashboard.py > streamlit.log 2>&1 &

ss -tlnp | grep 8501

# Construir la imagen
docker build -t mi-streamlit-app .

# Ejecutar el contenedor
docker run -p 8501:8501 mi-streamlit-app
