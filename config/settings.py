class Settings:
    def __init__(self):
        # Hardcoded Vertex AI Configuration - SDK uses GOOGLE_APPLICATION_CREDENTIALS env var automatically
        self.vertex_ai_project_id = "n8n-local-463912"
        self.model_name = "gemini-2.5-pro"
        
        # Hardcoded Storage Settings
        self.gcs_bucket_name = "calmira-backend"
        
        # Hardcoded Image Generation Settings  
        self.imagen_seed = 42  # Default seed (will be overridden per story)
        
        # Hardcoded Audio Generation Settings
        self.lyria_model = "lyria-002"  # Uses service account credentials automatically
        self.chirp_model = "chirp-3hd"
        self.chirp_voice_id = "en-US-Chirp3-HD-Charon" # Replace with actual Chirp API key
        
        # Hardcoded API Settings
        self.api_host = "0.0.0.0"
        self.api_port = 8000
        self.debug = False
        
        # Hardcoded CORS Settings
        self.cors_origins = "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8080,http://127.0.0.1:8080"
        
        # Workflow Settings
        self.max_retries = 3
        self.timeout_seconds = 300
    
    @property
    def cors_origins_list(self) -> list:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
