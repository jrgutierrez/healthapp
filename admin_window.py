import os
import streamlit as st
from streamlit_authenticator import validator
from streamlit_option_menu import option_menu
import database as db
import pandas as pd
from datetime import datetime
import plotly.express as px

def run_admin_window():
    # Page title
    st.sidebar.title(f"Bienvenido, {os.getenv('CLIENT')}.")

    action = 'Inicio'

    with st.sidebar:
        action = option_menu(
            menu_title='Qué necesitas?',
            options=['Inicio', 'Nueva medición', 'Consultar mediciones', 'Nuevo cliente'],
            icons=['house', 'speedometer', 'rulers', 'person-plus-fill'],  # https://icons.getbootstrap.com/
        )

    if action == 'Inicio':

        ### ESTO ES MEJORABLE ###
        all_users = pd.DataFrame(db.fetch_all_users())
        st.metric('Clientes Totales', all_users.shape[0], delta='4')

        all_users['gender'] = all_users['gender'].str.replace('F', 'Mujer').replace('M', 'Hombre')

        # Contar la frecuencia de cada valor en la columna 'gender'
        counts = all_users['gender'].value_counts()

        # Crear el diagrama de tarta con Plotly Express
        fig = px.pie(counts, values=counts.values, names=counts.index, title='Distribución por género')

        # Mostrar el diagrama de tarta en Streamlit
        st.plotly_chart(fig)

        ### COMPLETAR PAGINA DE INICIO ###
        pass

    elif action == 'Nuevo cliente':
        st.header('Introduce los datos del nuevo cliente:')
        preauth_username = st.text_input('Email')
        if st.button('Registrar cliente'):
            if validator.Validator().validate_email(preauth_username):
                preauth_res = db.create_preauth_user(preauth_username)
                if preauth_res == 1:
                    st.success('Usuario preautorizado correctamente')
                elif preauth_res == 0:
                    st.error('Usuario ya registrado')
                elif preauth_res == 2:
                    st.error('Usuario ya preautorizado')
                elif preauth_res == 3:
                    st.error('Error en la preautorización')
            else:
                st.error('Email introducido no válido')
    
    elif action == 'Consultar mediciones':
        st.header('Selecciona el cliente:')
        customers = [f"{user['name']} | {user['username']}" for user in db.fetch_all_users() if user['name']!='admin']
        username = st.selectbox('Cliente', customers)
        if st.button('Consultar mediciones'):
            data = pd.DataFrame(db.get_user_data(username.split(' | ')[1])).sort_values('date', ascending = False).reset_index()
            data = data[['date', 'weight', 'fat_perc', 'bone_mass', 'muscle_mass']]
            data = data.rename(columns = {'date': 'Fecha', 'weight': 'Peso', 'fat_perc': 'Porcentaje Grasa', 'bone_mass': 'Masa Osea', 'muscle_mass': 'Masa muscular'})
            st.write(data)


    else:
        st.header('Introduce los datos de la medición:')
        customers = [''] + [f"{user['name']} | {user['username']}" for user in db.fetch_all_users() if user['name']!='admin']
        username = st.selectbox('Cliente', customers, )
        date = st.date_input('Fecha de la medición', format = "DD/MM/YYYY")
        hour = st.time_input('Hora de la medición')
        date = datetime.combine(date, hour)
        weight = st.number_input('Peso (Kg)', 0.0, 250.0, 0.0, step = 0.01)
        fat_perc = st.number_input('Porcentaje de grasa corporal (%)', 0.0, 100.0, 0.0, step = 0.01)
        bone_mass = st.number_input('Masa ósea (Kg)', 0.0, 250.0, 0.0, step = 0.01)
        muscle_mass = st.number_input('Porcentaje de masa muscular (%)', 0.0, 100.0, 0.0, step = 0.01)

        if st.button('Registrar medición'):
            if ' | ' in username:
                try:
                    insert_res = db.insert_data(username.split(' | ')[1], weight, fat_perc, bone_mass, muscle_mass, date)
                    if insert_res == 1:
                        st.success('Medición registrada con éxito')
                except:
                    st.error('Error con el registro de la medición')
            else:
                st.warning('Por favor, selecciona el cliente')