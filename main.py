import os
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Definir los alcances necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1922sJ9L6eQEErviFwOKZKV0S8DYQrHEAfpb-0hVzgAY"
RANGE_MAIN_TABLE = "B3:E11"
RANGE_SIDE_TABLE = "G3:H7"

USER_CREDENTIALS = {
    'grupo1': {'password': 'contraseña1', 'hoja': 'Grupo1'},
    'grupo2': {'password': 'contraseña2', 'hoja': 'Grupo2'},
    'grupo3': {'password': 'contraseña3', 'hoja': 'Grupo3'},
    'grupo4': {'password': 'contraseña4', 'hoja': 'Grupo4'},
    'grupo5': {'password': 'contraseña5', 'hoja': 'Grupo5'},
    'grupo6': {'password': 'contraseña6', 'hoja': 'Grupo6'},
    'grupo7': {'password': 'contraseña7', 'hoja': 'Grupo7'},
    'grupo8': {'password': 'contraseña8', 'hoja': 'Grupo8'},
    'grupo9': {'password': 'contraseña9', 'hoja': 'Grupo9'},
    'grupo10': {'password': 'contraseña10', 'hoja': 'Grupo10'},
    'grupo11': {'password': 'contraseña11', 'hoja': 'Grupo11'},
    'grupo12': {'password': 'contraseña12', 'hoja': 'Grupo12'},
    'grupo13': {'password': 'contraseña13', 'hoja': 'Grupo13'},
    'grupo14': {'password': 'contraseña14', 'hoja': 'Grupo14'},
    'grupo15': {'password': 'contraseña15', 'hoja': 'Grupo15'},
}

def setup_sheets():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            try:
                credentials = flow.run_console()
            except Exception as e:
                st.error(f"Error durante la autenticación: {e}")
                return None

        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    
    try:
        service = build("sheets", "v4", credentials=credentials)
        return service
    except HttpError as error:
        st.error(f"Error al conectar con Google Sheets: {error}")
        return None

def load_data_from_sheet(sheets_service, sheet_name, range_name):
    try:
        range_ = f"{sheet_name}!{range_name}"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=range_).execute()
        values = result.get('values', [])
        return values
    except HttpError as error:
        st.error(f"Error al obtener los datos de {sheet_name}: {error}")
        return None

def display_main_table(values, sheet_name):
    if values:
        st.subheader(f"Datos de la Cartera del {sheet_name}")
        df = pd.DataFrame(values[1:], columns=values[0])

        # Eliminar filas completamente vacías
        df.dropna(how='all', inplace=True)

        if df.empty:
            st.write(f"No se encontraron datos en la Cartera de {sheet_name}.")
            return

        # Mostrar la tabla sin formato de Excel
        st.table(df)
    else:
        st.write(f"No se encontraron datos en la Cartera de {sheet_name}.")

def display_side_table(values, sheet_name):
    if values:
        df = pd.DataFrame(values, columns=["Descripción", "Valor"])  

        # Eliminar filas completamente vacías
        df.dropna(how='all', inplace=True)

        if df.empty:
            st.write(f"No se encontraron datos en la tabla del costado de {sheet_name}.")
            return

        # Mostrar la tabla sin formato de Excel
        st.table(df)
    else:
        st.write(f"No se encontraron datos en la tabla del costado de {sheet_name}.")
    
def main():
    st.title("Visualización: Datos de Carteras 📊")
    st.markdown("<h3 style='text-align: center; color: #333;'>Ingrese sus credenciales</h3>", unsafe_allow_html=True)

    username = st.text_input("Usuario", "")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]['password'] == password:
            sheet_name = USER_CREDENTIALS[username]['hoja']
            sheets_service = setup_sheets()

            if sheets_service:
                st.success(f"Bienvenido, {username}. Cargando datos de la hoja {sheet_name}...")

                if 'values_main_table' not in st.session_state:
                    st.session_state.values_main_table = load_data_from_sheet(sheets_service, sheet_name, RANGE_MAIN_TABLE)

                if 'values_side_table' not in st.session_state:
                    st.session_state.values_side_table = load_data_from_sheet(sheets_service, sheet_name, RANGE_SIDE_TABLE)

                display_main_table(st.session_state.values_main_table, sheet_name)
                display_side_table(st.session_state.values_side_table, sheet_name)

                if st.button("Actualizar Datos"):
                    # Actualizar los datos nuevamente desde Google Sheets
                    st.session_state.values_main_table = load_data_from_sheet(sheets_service, sheet_name, RANGE_MAIN_TABLE)
                    st.session_state.values_side_table = load_data_from_sheet(sheets_service, sheet_name, RANGE_SIDE_TABLE)
                    # Mostrar los datos actualizados
                    display_main_table(st.session_state.values_main_table, sheet_name)
                    display_side_table(st.session_state.values_side_table, sheet_name)

        else:
            st.error("Usuario o contraseña incorrectos. Inténtalo de nuevo.")
            st.experimental_rerun()

if __name__ == "__main__":
    main()

