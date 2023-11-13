import streamlit as st
from streamlit_option_menu import option_menu
import database as db
from custom_auth import customAuth
from admin_window import run_admin_window
from user_window import run_user_window
import time


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = 'Salud', page_icon = '💪', layout = 'wide')

# Company logo
#st.image('images/logo_mf.jpeg')

# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

usernames = {user['username']: 
                {'email': user['username'], 
                'name': user['name'], 
                'password': user['password']} 
            for user in users}

preauth_users = {'emails': [user['username'] for user in db.fetch_all_users_preauth()]}

authenticator = customAuth({'usernames': usernames}, 'health_dashboard', 'abcdef', cookie_expiry_days = 30, preauthorized = preauth_users)

login_state = '"Inicio de Sesión"'
# --- NAVIGATION MENU ---

### ESTO ES MEJORABLE ###

def show_option_menu(default_index = 0):
    return option_menu(
                menu_title=None,
                options=["Inicio de Sesión", "Registro"],
                icons=["box-arrow-in-left", "person-plus-fill"],  # https://icons.getbootstrap.com/
                orientation="horizontal",
                default_index=default_index
            )   

# --- Redirect to register if user not registered ---
def redirect_to_register():
    query_email = st.experimental_get_query_params().get('email')
    if query_email is not None:
        if query_email[0] not in [user['username'] for user in users] and query_email[0] in preauth_users['emails']:
            st.session_state.email_register = query_email[0]
            return 1
    return 0

init = st.session_state.get('init')
try:
    cookie = st.session_state.get('init').get('health_dashboard')
    if cookie is None:
        login_state = show_option_menu(redirect_to_register())
except:
    login_state = show_option_menu(redirect_to_register())



# --- REGISTER FORM ---
if login_state == 'Registro':
    if authenticator.register_user('Registro', preauthorization=True):
        with st.spinner("Cargando..."):
            st.success('Usuario registrado correctamente')
            time.sleep(1)
            st.rerun()

# --- LOGIN FORM ---
else:
    name, authentication_status, username = authenticator.login('Inicio de Sesión', 'main')

    if authentication_status == False:
        st.error('Email o contraseña incorrectos.')

    if authentication_status == None:
        st.warning('Inicia sesión para ver el contenido.')        

    if authentication_status:
        if username == 'admin':
            run_admin_window()
        else:
            run_user_window(username, name)

        ### MEJORAR ESTO ###
        st.sidebar.markdown("&nbsp;")
        st.sidebar.markdown("&nbsp;")
        st.sidebar.markdown("---")

        authenticator.logout('Cerrar Sesión', 'sidebar')