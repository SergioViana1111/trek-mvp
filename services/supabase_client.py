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
        url = None
        key = None
        # 1. Try Streamlit Secrets
        try:
            if hasattr(st, "secrets") and "supabase" in st.secrets:
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["key"]
        except Exception:
            pass

        # 2. Fallback to local secrets.toml (for tests)
        if not url:
            import toml, os
            try:
                secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets.toml")
                if os.path.exists(secrets_path):
                    data = toml.load(secrets_path)
                    url = data["supabase"]["url"]
                    key = data["supabase"]["key"]
            except Exception:
                pass
        
        if url and key:
            try:
                self._client = create_client(url, key)
            except Exception as e:
                print(f"Supabase connection error: {e}")
                self._client = None
        else:
            self._client = None

    @property
    def client(self) -> Client:
        return self._client

def get_supabase() -> Client:
    service = SupabaseService()
    return service.client
