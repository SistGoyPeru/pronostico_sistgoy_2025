import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import hashlib
import datetime
import os

# Definir alcance de los permisos
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class AuthManager:
    def __init__(self, credentials_file="credentials.json", sheet_name="SistGoy_Usuarios"):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = None
        self.sheet = None
        self.users_cache = None
        
    def connect(self):
        """Conecta con Google Sheets usando las credenciales."""
        if not os.path.exists(self.credentials_file):
            return False, "Archivo 'credentials.json' no encontrado."
            
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open(self.sheet_name).sheet1
            return True, "Conexión exitosa"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def _hash_password(self, password):
        """Hashea la contraseña para no guardarla en texto plano."""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_all_users(self):
        """Obtiene todos los usuarios (cacheado para eficiencia)."""
        if not self.client:
            success, msg = self.connect()
            if not success:
                return []
        
        try:
            # Obtener todos los registros
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            st.error(f"Error al leer usuarios: {e}")
            return []

    def check_user_exists(self, username):
        """Verifica si un usuario ya existe."""
        users = self.get_all_users()
        for user in users:
            if str(user.get('username')) == username:
                return True
        return False

    def validate_login(self, username, password):
        """Valida credenciales de usuario."""
        users = self.get_all_users()
        hashed_pw = self._hash_password(password)
        
        for user in users:
            if str(user.get('username')) == username and user.get('password') == hashed_pw:
                return True, user.get('name', username)
        
        return False, None

    def register_user(self, username, password, email, name):
        """Registra un nuevo usuario."""
        if not self.client:
            self.connect()
            
        if self.check_user_exists(username):
            return False, "El usuario ya existe."
            
        try:
            hashed_pw = self._hash_password(password)
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Agregar fila: username, password, email, name, created_at
            new_row = [username, hashed_pw, email, name, created_at]
            self.sheet.append_row(new_row)
            return True, "Usuario registrado exitosamente."
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"
