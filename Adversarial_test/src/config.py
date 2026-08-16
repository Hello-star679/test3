"""
Configuration management for the adversarial test framework.
Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SandboxConfig:
    """Complete configuration for the adversarial test system."""
    
    # ============================================
    # LOOP CONFIGURATION
    # ============================================
    max_iterations: int = int(os.getenv("MAX_EPOCHS", "50"))
    population_size: int = int(os.getenv("POPULATION_SIZE", "30"))
    mutation_rate: float = float(os.getenv("MUTATION_RATE", "0.25"))
    elite_ratio: float = float(os.getenv("ELITE_RATIO", "0.5"))
    
    # ============================================
    # DETECTOR CONFIGURATION
    # ============================================
    detector_type: str = os.getenv("DETECTOR_TYPE", "mock").lower()
    use_mock: bool = os.getenv("USE_MOCK", "True").lower() == "true"
    classifier_endpoint: str = os.getenv("CLASSIFIER_URL", "http://localhost:8080/classify")
    classifier_timeout: int = int(os.getenv("CLASSIFIER_TIMEOUT", "10"))
    
    # Hugging Face settings
    hf_local_url: str = os.getenv("HF_LOCAL_URL", "http://localhost:8080")
    hf_model_name: str = os.getenv("HF_MODEL_NAME", "default-model")
    hf_api_token: Optional[str] = os.getenv("HF_API_TOKEN")
    
    # OpenAI settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_threshold: float = float(os.getenv("OPENAI_THRESHOLD", "0.7"))
    
    # Local model settings
    local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "./models/classifier")
    local_model_label: str = os.getenv("LOCAL_MODEL_LABEL", "malicious")
    local_model_index: int = int(os.getenv("LOCAL_MODEL_INDEX", "1"))
    
    # ============================================
    # GENERATOR CONFIGURATION
    # ============================================
    template_file: str = os.getenv("TEMPLATE_FILE", "templates/general.txt")
    template_categories: list = field(default_factory=lambda: 
        os.getenv("TEMPLATE_CATEGORIES", "account,security,transactions,general").split(",")
    )
    use_categories: bool = os.getenv("USE_CATEGORIES", "False").lower() == "true"
    
    # ============================================
    # OUTPUT CONFIGURATION
    # ============================================
    log_dir: str = os.getenv("LOG_DIR", "logs")
    save_results: bool = os.getenv("SAVE_RESULTS", "True").lower() == "true"
    verbose: bool = os.getenv("VERBOSE", "True").lower() == "true"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # ============================================
    # SECURITY CONFIGURATION
    # ============================================
    sandbox_mode: bool = os.getenv("SANDBOX_MODE", "True").lower() == "true"
    allow_external_calls: bool = os.getenv("ALLOW_EXTERNAL_CALLS", "False").lower() == "true"
    max_text_length: int = int(os.getenv("MAX_TEXT_LENGTH", "500"))
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Validate settings
        if self.detector_type not in ["mock", "hf", "openai", "local"]:
            raise ValueError(f"Invalid detector_type: {self.detector_type}")
        
        if self.detector_type == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key required for openai detector type")
        
        if self.detector_type == "local" and not os.path.exists(self.local_model_path):
            if self.use_mock:
                print(f"[WARN] Local model not found at {self.local_model_path}, using mock")
            else:
                raise FileNotFoundError(f"Local model not found: {self.local_model_path}")

    def to_dict(self) -> dict:
        """Convert config to dictionary for logging."""
        return {
            "max_iterations": self.max_iterations,
            "population_size": self.population_size,
            "mutation_rate": self.mutation_rate,
            "detector_type": self.detector_type,
            "classifier_endpoint": self.classifier_endpoint,
            "template_file": self.template_file,
            "sandbox_mode": self.sandbox_mode
        }
