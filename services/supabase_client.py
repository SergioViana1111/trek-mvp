import streamlit as st
from supabase import create_client, Client

class SupabaseService:
    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self._client = create_client(url, key)
        except Exception as e:
            st.error(f"Failed to initialize Supabase client: {e}")
            self._client = None

    @property
    def client(self) -> Client:
        return self._client

def get_supabase() -> Client:
    service = SupabaseService()
    return service.client
