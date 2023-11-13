import streamlit as st
import streamlit_authenticator as stauth
import database as db

class customAuth(stauth.Authenticate):

    def login(self, form_name: str, location: str='main') -> tuple:
            """
            Creates a login widget.

            Parameters
            ----------
            form_name: str
                The rendered name of the login form.
            location: str
                The location of the login form i.e. main or sidebar.
            Returns
            -------
            str
                Name of the authenticated user.
            bool
                The status of authentication, None: no credentials entered, 
                False: incorrect credentials, True: correct credentials.
            str
                Username of the authenticated user.
            """
            if location not in ['main', 'sidebar']:
                raise ValueError("Location must be one of 'main' or 'sidebar'")
            if not st.session_state['authentication_status']:
                self._check_cookie()
                if not st.session_state['authentication_status']:
                    if location == 'main':
                        login_form = st.form('Login')
                    elif location == 'sidebar':
                        login_form = st.sidebar.form('Login')

                    login_form.subheader(form_name)
                    self.username = login_form.text_input('Email').lower()
                    st.session_state['username'] = self.username
                    self.password = login_form.text_input('Contraseña', type='password')

                    if login_form.form_submit_button('Iniciar Sesión'):
                        self._check_credentials()
                        
            return st.session_state['name'], st.session_state['authentication_status'], st.session_state['username']
    

    def register_user(self, form_name: str, location: str='main', preauthorization=True) -> bool:
        """
        Creates a register new user widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the register new user form.
        location: str
            The location of the register new user form i.e. main or sidebar.
        preauthorization: bool
            The preauthorization requirement, True: user must be preauthorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if preauthorization:
            if not self.preauthorized:
                raise ValueError("preauthorization argument must not be None")
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        email_register = ''
        if st.session_state.get('email_register') is not None:
            email_register = st.session_state.get('email_register')
        new_username = register_user_form.text_input('Email', value=email_register)
        new_name = register_user_form.text_input('Nombre')
        new_lastname = register_user_form.text_input('Apellidos')
        new_gender = register_user_form.selectbox('Género', ['', 'Femenino', 'Masculino', 'Prefiero no decirlo'])
        new_password = register_user_form.text_input('Contraseña', type='password')
        new_password_repeat = register_user_form.text_input('Repetir Contraseña', type='password')

        if register_user_form.form_submit_button('Registrarse'):
            if len(new_username) and len(new_lastname) and len(new_name) and len(new_gender) and len(new_password) > 0:
                if new_username not in self.credentials['usernames']:
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_username in self.preauthorized['emails']:
                                self._register_credentials(new_username, new_name, new_lastname, new_gender, new_password, preauthorization)
                                return True
                            else:
                                st.error('Usuario no preautorizado para registro')
                        else:
                            self._register_credentials(new_username, new_name, new_lastname, new_gender, new_password, preauthorization)
                            return True
                    else:
                        st.error('Las contraseñas no coinciden')
                else:
                    st.error('Email ya registrado')
            else:
                st.error('Por favor, introduce un email, nombre, apellidos, género y contraseña')

    def _register_credentials(self, username: str, name: str, lastname: str, gender: str, password: str, preauthorization: bool):
        """
        Adds to credentials dictionary the new user's information.

        Parameters
        ----------
        username: str
            The username of the new user.
        name: str
            The name of the new user.
        password: str
            The password of the new user.
        email: str
            The email of the new user.
        preauthorization: bool
            The preauthorization requirement, True: user must be preauthorized to register, 
            False: any user can register.
        """
        if not self.validator.validate_email(username):
            st.error('El email introducido no es válido')
            return
        if not self.validator.validate_name(name):
            st.error('El nombre introducido no es válido')
            return
        if not self.validator.validate_name(lastname):
            st.error('Los apellidos introducidos no son válidos')
            return

        password = stauth.Hasher([password]).generate()[0]

        self.credentials['usernames'][username] = {'name': name, 
            'password': password, 'email': username}
        
        db.create_user(username, name, lastname, gender, password)

        if preauthorization:
            db.delete_preauth_user(username)