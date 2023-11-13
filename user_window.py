import streamlit as st
from streamlit_option_menu import option_menu
import database as db
import pandas as pd

def run_user_window(username, name):

    # Page title
    st.sidebar.title(f'Bienvenido, {name.capitalize()}.')

    action = 'Inicio'

    with st.sidebar:
        action = option_menu(
            menu_title='Qué necesitas?',
            options=['Inicio', 'Nueva medición', 'Consultar mediciones', 'Nuevo cliente'],
            icons=['house', 'speedometer', 'rulers', 'person-plus-fill'],  # https://icons.getbootstrap.com/
        )

    

    if action == 'Inicio':

        ### ESTO ES MEJORABLE ###
        st.header('Resumen')
        # Fetch user health data
        data = pd.DataFrame(db.get_user_data(username))

        if data.shape[0] > 0:

            
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            _, last_date, last_weight, last_fat_perc, last_bone_mass, last_muscle_mass, _ = data.sort_values('date', ascending=False).iloc[0].values

            with col1:
                st.metric('Peso', str(last_weight) + ' Kg', delta='4')
            with col2:
                st.metric('% Grasa', str(last_fat_perc) + ' %', delta='4')
            with col3:
                st.metric('Masa Ósea', str(last_bone_mass) + ' Kg', delta='4')
            with col4:
                st.metric('Masa Muscular', str(last_muscle_mass) + ' %', delta='4')

            st.write(data)

        ### COMPLETAR PAGINA DE INICIO ###
        pass

    elif action == 'Nuevo cliente':
        pass
    
    elif action == 'Consultar mediciones':
        pass


    else:
        pass