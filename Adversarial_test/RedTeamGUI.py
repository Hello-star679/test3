#!/usr/bin/env python3
"""
ADVERSARIAL RED-TEAM FRAMEWORK
For authorized security testing and research ONLY

This framework implements:
1. GAN-style adversarial loop for security testing
2. Agentic content generation (LLM-powered mutation)
3. Realistic attack pattern simulation
4. Classifier evasion testing
5. Security boundary discovery

WARNING: This is for AUTHORIZED red-team operations ONLY.
Use in controlled, sandboxed environments with proper legal authorization.
"""
import sys
import threading
import queue
from datetime import datetime
import hashlib
import json
import time
import random
import argparse
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional, Union
from collections import defaultdict
from pathlib import Path
import os
import os
import sys
import json
import time
import random
import hashlib
import argparse
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional, Union
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import threading
import queue

# ============================================================
# CONFIGURATION
# ============================================================

class RedTeamConfig:
    """Configuration for red-team adversarial testing."""
    
    # Loop configuration
    max_iterations: int = 100
    population_size: int = 50
    mutation_rate: float = 0.35
    elite_ratio: float = 0.4
    crossover_rate: float = 0.3
    
    # Attack pattern configuration
    attack_difficulty: str = "adaptive"  # easy, medium, hard, adaptive
    attack_vectors: list = field(default_factory=lambda: [
        "phishing", "social_engineering", "credential_harvesting",
        "business_email_compromise", "fake_invoice", "account_takeover"
    ])
    
    # LLM Configuration (for agentic blabbering)
    llm_provider: str = "mock"  # mock, openai, anthropic, local
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.9
    llm_max_tokens: int = 150
    
    # Detector configuration
    detector_type: str = "mock"
    classifier_endpoint: str = "http://localhost:8080/classify"
    detector_threshold: float = 0.6
    
    # Output settings
    log_dir: str = "logs"
    save_generations: bool = True
    verbose: bool = True
    sandbox_mode: bool = True
    
    def __post_init__(self):
        os.makedirs(self.log_dir, exist_ok=True)


# ============================================================
# AGENTIC CONTENT GENERATOR (The "Blabbering" Engine)
# ============================================================

class AgenticGenerator:
    """
    Multi-agent content generator for realistic attack pattern simulation.
    Each agent has a different "persona" and generates content accordingly.
    """
    
    def __init__(self, config: RedTeamConfig):
        self.config = config
        self.agents = self._initialize_agents()
        self.generation_history = []
        
    def _initialize_agents(self) -> List[Dict]:
        """Initialize specialized agents."""
        return [
            {
                "name": "Phishing_Agent",
                "role": "phishing",
                "style": "urgent, authoritative, uses fear/scarcity",
                "patterns": self._get_phishing_patterns(),
                "persona": "Bank Security Team"
            },
            {
                "name": "Social_Engineer_Agent",
                "role": "social_engineering",
                "style": "friendly, trustworthy, rapport-building",
                "patterns": self._get_social_patterns(),
                "persona": "IT Support Professional"
            },
            {
                "name": "BEC_Agent",
                "role": "business_email_compromise",
                "style": "professional, executive-level, uses authority",
                "patterns": self._get_bec_patterns(),
                "persona": "CFO / Executive"
            },
            {
                "name": "Harvesting_Agent",
                "role": "credential_harvesting",
                "style": "warning-based, security-focused",
                "patterns": self._get_harvesting_patterns(),
                "persona": "Security Alert System"
            },
            {
                "name": "Mutator_Agent",
                "role": "mutation",
                "style": "adaptive, evolutionary",
                "patterns": self._get_mutation_patterns(),
                "persona": "Adversarial Mutator"
            }
        ]
    
    def _get_phishing_patterns(self) -> List[str]:
        """Phishing attack templates (realistic but safe)."""
        return [
            "URGENT: {company} Security Alert. Your account will be suspended in {time}. Verify your {credential} immediately.",
            "CRITICAL: Unauthorized login detected from {location}. Click here to secure your {account}.",
            "FINAL NOTICE: Your {account} has been flagged for {violation}. Immediate action required.",
            "SECURITY BREACH: {company} detected suspicious activity. Download the attached {document} to review."
        ]
    
    def _get_social_patterns(self) -> List[str]:
        """Social engineering templates."""
        return [
            "Hi {target}, this is {support} from {company}. We're helping users who experienced {issue}.",
            "I noticed your {profile} and wanted to connect about {opportunity}. Are you available?",
            "We're doing a {survey} and selected you based on your {expertise}. Would you participate?",
            "Your colleague {colleague} suggested I reach out about {project}. Let's connect."
        ]
    
    def _get_bec_patterns(self) -> List[str]:
        """Business email compromise templates."""
        return [
            "I need you to process the {payment} for {amount} immediately. This is confidential.",
            "Please wire the {funds} to {bank} at your earliest convenience. I'm in a meeting.",
            "URGENT: Client requested {action}. Send the {document} to {email}.",
            "I'm traveling and need {access} to the {system}. Can you provide {credentials}?"
        ]
    
    def _get_harvesting_patterns(self) -> List[str]:
        """Credential harvesting templates."""
        return [
            "Your {credential} is set to expire. Please update via {link}.",
            "We're updating our {system}. Please verify your {data}.",
            "Account verification required: {company} needs to confirm your {information}.",
            "Scheduled maintenance on {date}. Please keep your {credential} ready."
        ]
    
    def _get_mutation_patterns(self) -> List[str]:
        """Mutation patterns for evolution."""
        return [
            "{base} {variation}",
            "{variation}: {base}",
            "RE: {base}",
            "FWD: {base}",
            "[Action Required] {base}"
        ]
    
    def generate_with_llm(self, prompt: str, agent: Dict) -> str:
        """
        Generate content using LLM (OpenAI/Anthropic/local).
        This is the "agentic blabbering" core.
        """
        if self.config.llm_provider == "mock":
            return self._mock_llm_generation(agent)
        elif self.config.llm_provider == "openai":
            return self._openai_generation(prompt, agent)
        elif self.config.llm_provider == "local":
            return self._local_llm_generation(prompt, agent)
        else:
            return self._mock_llm_generation(agent)
    
    def _mock_llm_generation(self, agent: Dict) -> str:
        """Mock LLM for testing without API calls."""
        patterns = agent.get("patterns", [])
        template = random.choice(patterns)
        
        # Fill in realistic placeholders
        placeholders = {
            "company": ["TechCorp", "GlobalBank", "SecureSystems", "DataVault"],
            "time": ["12 hours", "24 hours", "48 hours", "immediately"],
            "credential": ["password", "MFA code", "security token", "PIN"],
            "account": ["account", "profile", "subscription", "membership"],
            "location": ["New York", "London", "Tokyo", "Dubai"],
            "violation": ["unauthorized access", "suspicious activity", "policy violation"],
            "target": ["user", "employee", "customer", "client"],
            "support": ["support", "helpdesk", "admin", "security team"],
            "issue": ["login failures", "suspicious activity", "account lockouts"],
            "profile": ["LinkedIn", "professional profile", "company directory"],
            "opportunity": ["a partnership", "a business opportunity", "a project"],
            "survey": ["security survey", "client satisfaction survey", "industry study"],
            "expertise": ["technical expertise", "industry knowledge", "professional background"],
            "colleague": ["John", "Sarah", "Mike", "David"],
            "project": ["the new initiative", "the quarterly review", "the security audit"],
            "payment": ["invoice", "payment", "wire transfer"],
            "amount": ["$500", "$1,000", "$5,000", "$50,000"],
            "funds": ["payment", "transfer", "wire", "deposit"],
            "bank": ["Bank of America", "Chase", "Wells Fargo", "HSBC"],
            "action": ["review", "approve", "verify", "confirm"],
            "document": ["contract", "invoice", "report", "agreement"],
            "email": ["client@company.com", "info@company.com", "support@company.com"],
            "access": ["access", "permission", "authorization"],
            "system": ["CRM", "financial system", "client portal", "internal database"],
            "data": ["contact information", "financial data", "personal information"],
            "link": ["the attached file", "the portal", "the shared drive"],
            "date": ["December 15", "December 30", "January 1", "Monday"],
            "variation": ["URGENT", "Important", "Confidential", "Time-Sensitive"],
            "base": ["Please respond", "Action required", "Your attention needed"]
        }
        
        # Fill placeholders
        result = template
        for key, values in placeholders.items():
            if f"{{{key}}}" in result:
                result = result.replace(f"{{{key}}}", random.choice(values))
        
        return result
    
    def _openai_generation(self, prompt: str, agent: Dict) -> str:
        """Generate using OpenAI API."""
        try:
            import openai
            openai.api_key = self.config.llm_api_key
            
            system_prompt = f"""You are a security researcher creating realistic attack patterns for testing.
            Generate a {agent['role']} attack message in the style of a {agent['persona']}.
            Use {agent['style']} tone.
            The message should be plausible and realistic, but clearly marked as a test.
            """
            
            response = openai.ChatCompletion.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.llm_temperature,
                max_tokens=self.config.llm_max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] OpenAI generation failed: {e}")
            return self._mock_llm_generation(agent)
    
    def _local_llm_generation(self, prompt: str, agent: Dict) -> str:
        """Generate using local LLM (e.g., Ollama, HuggingFace)."""
        # Placeholder for local LLM integration
        try:
            # Example for Ollama
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": self.config.llm_temperature
                }
            )
            return response.json().get("response", "LLM response failed")
        except:
            return self._mock_llm_generation(agent)
    
    def generate_attack(self, agent_name: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate an attack pattern.
        Returns: (content, agent_name)
        """
        if agent_name:
            agents = [a for a in self.agents if a["name"] == agent_name]
            agent = agents[0] if agents else random.choice(self.agents)
        else:
            agent = random.choice(self.agents)
        
        # Use LLM for more realistic generation
        prompt = f"Generate a {agent['role']} attack message."
        content = self.generate_with_llm(prompt, agent)
        
        # Record generation
        self.generation_history.append({
            "agent": agent["name"],
            "role": agent["role"],
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        return content, agent["name"]
    
    def mutate_with_agents(self, text: str) -> str:
        """
        Mutate text using agentic strategies.
        This is the "agentic blabbering" - agents actively modify content.
        """
        # Select a mutation strategy
        mutation_type = random.random()
        
        if mutation_type < 0.25:
            # Agent 1: Add urgency/scarcity
            urgency_words = ["URGENT", "IMMEDIATE", "ASAP", "CRITICAL", "ACTION REQUIRED"]
            text = f"{random.choice(urgency_words)}: {text}"
        elif mutation_type < 0.50:
            # Agent 2: Add authority
            authority_phrases = ["From the desk of", "Confirmed by", "Approved by", "In accordance with"]
            text = f"{random.choice(authority_phrases)}: {text}"
        elif mutation_type < 0.75:
            # Agent 3: Personalization
            personalization = ["your team", "our department", "your security", "our system"]
            text = text.replace("your", random.choice(personalization))
        else:
            # Agent 4: Formatting variation
            if not text.endswith('.'):
                text += random.choice(['!', '?', '.'])
            text = text.upper() if random.random() < 0.3 else text
        
        return text
    
    def generate_population(self, size: int) -> List[Dict]:
        """
        Generate a population of attack patterns.
        Returns: List of {content, agent, score, metadata}
        """
        population = []
        for _ in range(size):
            content, agent_name = self.generate_attack()
            population.append({
                "content": content,
                "agent": agent_name,
                "score": None,
                "metadata": {
                    "generation": len(self.generation_history),
                    "timestamp": datetime.now().isoformat()
                }
            })
        return population


# ============================================================
# DETECTOR / CRITIC
# ============================================================

class SecurityDetector:
    """
    Security detector that evaluates attack patterns.
    This is the "critic" in the GAN-style loop.
    """
    
    def __init__(self, config: RedTeamConfig):
        self.config = config
        self.detector_type = config.detector_type
        self.threshold = config.detector_threshold
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the appropriate detector."""
        if self.detector_type == "mock":
            self._detector = self._mock_score
        elif self.detector_type == "hf":
            self._detector = self._hf_score
        elif self.detector_type == "openai":
            self._detector = self._openai_score
        else:
            self._detector = self._mock_score
    
    def _mock_score(self, text: str) -> float:
        """
        Mock detector scoring - simulates a security filter.
        Returns a score 0-1 where higher = more suspicious.
        """
        indicators = [
            "urgent", "immediate", "critical", "suspension", "unauthorized",
            "verify", "confirm", "update", "security", "alert", "breach",
            "password", "credential", "account", "login", "payment",
            "wire", "transfer", "funds", "invoice", "client", "confidential"
        ]
        
        score = sum(1 for word in indicators if word in text.lower()) / len(indicators)
        score += min(1.0, len(text) / 200) * 0.3
        
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16) / (16**8)
        score = min(1.0, score + (hash_val - 0.5) * 0.15)
        
        return max(0.0, min(1.0, score))
    
    def _hf_score(self, text: str) -> float:
        """Score using Hugging Face model."""
        try:
            import requests
            response = requests.post(
                self.config.classifier_endpoint,
                json={"inputs": text},
                timeout=10
            )
            result = response.json()
            
            def extract_score(obj):
                if isinstance(obj, (int, float)):
                    return float(obj)
                if isinstance(obj, list):
                    for item in obj:
                        score = extract_score(item)
                        if score is not None:
                            return score
                if isinstance(obj, dict):
                    score_keys = ['score', 'prediction', 'probability']
                    for key in score_keys:
                        if key in obj:
                            return float(obj[key])
                    if 'label' in obj and 'score' in obj:
                        return float(obj['score'])
                return None
            
            score = extract_score(result)
            return max(0.0, min(1.0, score if score is not None else 0.5))
        except:
            return self._mock_score(text)
    
    def _openai_score(self, text: str) -> float:
        """Score using OpenAI Moderation API."""
        try:
            import openai
            openai.api_key = self.config.llm_api_key
            response = openai.Moderation.create(input=text)
            category_scores = response["results"][0]["category_scores"]
            return max(category_scores.values()) if category_scores else 0.0
        except:
            return self._mock_score(text)
    
    def score_batch(self, texts: List[str]) -> List[float]:
        """Score multiple texts."""
        return [self._detector(text) for text in texts]
    
    def score_population(self, population: List[Dict]) -> List[Dict]:
        """Score a population of attack patterns."""
        contents = [item["content"] for item in population]
        scores = self.score_batch(contents)
        
        for item, score in zip(population, scores):
            item["score"] = score
        
        return sorted(population, key=lambda x: x["score"])


# ============================================================
# RED-TEAM ENGINE (GAN-Style Loop)
# ============================================================

# In RedTeamGUI.py - Find RedTeamEngine class and modify

class RedTeamEngine:
    def __init__(self, config: RedTeamConfig, callback=None):
        self.config = config
        self.callback = callback  # <-- ADD THIS
        self.generator = AgenticGenerator(config)
        self.detector = SecurityDetector(config)
        self.population = []
        self.history = []
        self.best_attack = None
        self.best_score = 1.0
        self.iteration = 0

    def run(self):
        """Run the red-team adversarial loop with real-time updates."""
        self.initialize_population()
        
        for iteration in range(self.config.max_iterations):
            self.iteration = iteration + 1
            self.evolve_population()
            
            # Calculate statistics
            scores = [item["score"] for item in self.population]
            avg_score = sum(scores) / len(scores)
            best_this_gen = self.population[0]["score"]
            best_attack = self.population[0]["content"]
            
            # --- REAL-TIME UPDATE ---
            if self.callback:
                self.callback({
                    'type': 'epoch',
                    'epoch': self.iteration,
                    'total': self.config.max_iterations,
                    'best_score': best_this_gen,
                    'avg_score': avg_score,
                    'best_attack': best_attack,
                    'agent': self.population[0]["agent"],
                    'population_size': len(self.population)
                })
            
            # Track best
            if best_this_gen < self.best_score:
                self.best_score = best_this_gen
                self.best_attack = best_attack
                if self.callback:
                    self.callback({
                        'type': 'new_best',
                        'score': self.best_score,
                        'attack': self.best_attack,
                        'epoch': self.iteration,
                        'agent': self.population[0]["agent"]
                    })
            
            # Early stopping
            if best_this_gen < 0.1:
                break
        
    def initialize_population(self):
        """Initialize the population with attack patterns."""
        print(f"[*] Initializing population of {self.config.population_size} attack patterns...")
        self.population = self.generator.generate_population(self.config.population_size)
        self.population = self.detector.score_population(self.population)
        
        if self.population:
            self.best_attack = self.population[0]["content"]
            self.best_score = self.population[0]["score"]
        
        print(f"[+] Best initial score: {self.best_score:.4f}")
    
    def evolve_population(self):
        """Evolve the population using GAN-style approach."""
        self.population.sort(key=lambda x: x["score"])
        elite_count = int(len(self.population) * self.config.elite_ratio)
        elites = self.population[:elite_count]
        offspring = []
        
        crossover_count = int(len(elites) * self.config.crossover_rate)
        for _ in range(crossover_count):
            if len(elites) >= 2:
                parent1 = random.choice(elites)
                parent2 = random.choice(elites)
                child_content = self._crossover(parent1["content"], parent2["content"])
                child_agent = random.choice([parent1["agent"], parent2["agent"]])
                offspring.append({
                    "content": child_content,
                    "agent": child_agent,
                    "metadata": {"generation": self.iteration, "method": "crossover"}
                })
        
        mutation_count = self.config.population_size - len(elites) - len(offspring)
        for _ in range(mutation_count):
            parent = random.choice(elites) if elites else random.choice(self.population)
            child_content = self.generator.mutate_with_agents(parent["content"])
            offspring.append({
                "content": child_content,
                "agent": parent["agent"],
                "metadata": {"generation": self.iteration, "method": "mutation"}
            })
        
        while len(offspring) < (self.config.population_size - len(elites)):
            content, agent = self.generator.generate_attack()
            offspring.append({
                "content": content,
                "agent": agent,
                "metadata": {"generation": self.iteration, "method": "fresh"}
            })
        
        self.population = elites + offspring
        self.population = self.detector.score_population(self.population)
        
        if self.population:
            if self.population[0]["score"] < self.best_score:
                self.best_score = self.population[0]["score"]
                self.best_attack = self.population[0]["content"]
    
    def _crossover(self, text1: str, text2: str) -> str:
        """Combine two texts using crossover."""
        words1 = text1.split()
        words2 = text2.split()
        
        if len(words1) < 2 or len(words2) < 2:
            return text1
        
        point1 = random.randint(0, len(words1) - 1)
        point2 = random.randint(0, len(words2) - 1)
        
        chunk2 = words2[point2:]
        result = words1[:point1] + chunk2
        return " ".join(result)
    
    def run(self):
        """Run the red-team adversarial loop."""
        print("=" * 80)
        print("🔥 RED-TEAM ADVERSARIAL ENGINE")
        print("=" * 80)
        print(f"Generations: {self.config.max_iterations}")
        print(f"Population: {self.config.population_size}")
        print(f"Mutation Rate: {self.config.mutation_rate}")
        print(f"Attack Vectors: {', '.join(self.config.attack_vectors)}")
        print("=" * 80)
        print()
        
        self.initialize_population()
        start_time = time.time()
        
        for iteration in range(self.config.max_iterations):
            self.iteration = iteration + 1
            self.evolve_population()
            scores = [item["score"] for item in self.population]
            avg_score = sum(scores) / len(scores)
            median_score = sorted(scores)[len(scores) // 2]
            best_this_gen = self.population[0]["score"]
            
            print(f"Generation {iteration+1:03d}/{self.config.max_iterations} | "
                  f"Best: {best_this_gen:.4f} | "
                  f"Avg: {avg_score:.4f} | "
                  f"Median: {median_score:.4f} | "
                  f"Agent: {self.population[0]['agent']}")
            
            self.history.append({
                "generation": iteration + 1,
                "best_score": best_this_gen,
                "avg_score": avg_score,
                "median_score": median_score,
                "best_attack": self.population[0]["content"],
                "agent": self.population[0]["agent"],
                "population_scores": scores
            })
            
            if best_this_gen < 0.1:
                print(f"[!] Perfect evasion found at generation {iteration+1}!")
                break
        
        elapsed = time.time() - start_time
        print()
        print("=" * 80)
        print("📊 RED-TEAM SUMMARY")
        print("=" * 80)
        print(f"Generations completed: {self.iteration}")
        print(f"Total attacks generated: {self.iteration * self.config.population_size}")
        print(f"Time elapsed: {elapsed:.2f}s")
        print(f"Best evasion score: {self.best_score:.4f}")
        print(f"Best attack pattern: {self.best_attack}")
        print("=" * 80)
        
        self._save_results()
        return self.best_attack, self.best_score, self.history

# ============================================================
# GUI INTERFACE
# ============================================================

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("[!] PyQt5 not installed. GUI features disabled.")

if GUI_AVAILABLE:
    class RedTeamGUI(QMainWindow):
        update_log_signal = pyqtSignal(str)
        finish_signal = pyqtSignal(str, float, list)
        error_signal = pyqtSignal(str)

        def __init__(self):
            super().__init__()
            self.config = RedTeamConfig()
            self.engine = None
            self.is_running = False
            self.thread = None
            self.log_lines = []
            self.init_ui()
            self.setup_signals()

        def init_ui(self):
            """Initialize the GUI."""
            self.setWindowTitle("Adversarial Red-Team Engine")
            self.setGeometry(100, 100, 1200, 800)

            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            control_panel = self.create_control_panel()
            layout.addWidget(control_panel)

            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            self.results_tab = QWidget()
            self.tabs.addTab(self.results_tab, "Results")
            self.setup_results_tab()

            self.attacks_tab = QWidget()
            self.tabs.addTab(self.attacks_tab, "Attack Patterns")
            self.setup_attacks_tab()

            self.log_tab = QWidget()
            self.tabs.addTab(self.log_tab, "Log")
            self.setup_log_tab()

        def create_control_panel(self) -> QWidget:
            """Create the control panel."""
            panel = QGroupBox("Control Panel")
            layout = QHBoxLayout()

            self.start_btn = QPushButton("▶ Start")
            self.start_btn.clicked.connect(self.start_engine)
            layout.addWidget(self.start_btn)

            self.stop_btn = QPushButton("⏹ Stop")
            self.stop_btn.clicked.connect(self.stop_engine)
            self.stop_btn.setEnabled(False)
            layout.addWidget(self.stop_btn)

            config_btn = QPushButton("⚙ Config")
            config_btn.clicked.connect(self.show_config)
            layout.addWidget(config_btn)

            self.progress = QProgressBar()
            layout.addWidget(self.progress)

            self.status_label = QLabel("Ready")
            layout.addWidget(self.status_label)

            panel.setLayout(layout)
            return panel

        def setup_results_tab(self):
            """Setup the results tab."""
            layout = QVBoxLayout()
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            layout.addWidget(self.results_text)

            stats_layout = QHBoxLayout()
            self.best_label = QLabel("Best Score: -")
            stats_layout.addWidget(self.best_label)
            self.avg_label = QLabel("Avg Score: -")
            stats_layout.addWidget(self.avg_label)
            self.generation_label = QLabel("Generation: 0")
            stats_layout.addWidget(self.generation_label)
            stats_layout.addStretch()
            layout.addLayout(stats_layout)

            self.results_tab.setLayout(layout)

        def setup_attacks_tab(self):
            """Setup the attacks tab."""
            layout = QVBoxLayout()
            self.attack_list = QListWidget()
            layout.addWidget(self.attack_list)

            self.attack_details = QTextEdit()
            self.attack_details.setReadOnly(True)
            self.attack_details.setMaximumHeight(150)
            layout.addWidget(self.attack_details)

            self.attacks_tab.setLayout(layout)

        def setup_log_tab(self):
            """Setup the log tab."""
            layout = QVBoxLayout()
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setFont(QFont("Monospace", 9))
            layout.addWidget(self.log_text)
            self.log_tab.setLayout(layout)

        def start_engine(self):
            """Start the red-team engine."""
            if self.is_running:
                return
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Running...")
            self.thread = threading.Thread(target=self._run_engine)
            self.thread.daemon = True
            self.thread.start()

        def _run_engine(self):
            """Run the red-team engine in a background thread."""
            try:
                self.engine = RedTeamEngine(self.config)
                import builtins
                original_print = builtins.print
                self.log_lines = []

                def log_capture(*args, **kwargs):
                    msg = " ".join(str(arg) for arg in args)
                    self.log_lines.append(msg)
                    original_print(*args, **kwargs)
                    self.update_log_signal.emit(msg)

                builtins.print = log_capture
                best_attack, best_score, history = self.engine.run()
                builtins.print = original_print
                self.finish_signal.emit(best_attack, best_score, history)
            except Exception as e:
                self.error_signal.emit(str(e))
                import traceback
                traceback.print_exc()

        def stop_engine(self):
            """Stop the engine."""
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Stopped")

        def show_config(self):
            """Show configuration dialog."""
            QMessageBox.information(self, "Configuration", "Config dialog coming soon!")

        def update_results(self, best_attack: str, best_score: float, history: List):
            """Update the results display with engine output."""
            self.best_label.setText(f"Best Score: {best_score:.4f}")
            self.generation_label.setText(f"Generation: {len(history)}")

            if history:
                avg = sum(h.get("avg_score", 0) for h in history) / len(history)
                self.avg_label.setText(f"Avg Score: {avg:.4f}")

            self.results_text.clear()
            self.results_text.append("🏆 Best Attack Pattern:")
            self.results_text.append(f"{best_attack}\n")
            self.results_text.append(f"📊 Best Evasion Score: {best_score:.4f}")
            self.results_text.append(f"📈 Generations: {len(history)}")

            self.attack_list.clear()
            if self.engine and hasattr(self.engine, 'population'):
                for item in self.engine.population[:10]:
                    display = f"{item['score']:.4f} | {item['agent']} | {item['content'][:50]}..."
                    self.attack_list.addItem(display)

            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("✅ Complete")
            self.is_running = False

        def add_log(self, msg: str):
            """Add a log message."""
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {msg}")

        def setup_signals(self):
            """Setup Qt signals."""
            self.update_log_signal.connect(self.add_log)
            self.finish_signal.connect(self.update_results)
            self.error_signal.connect(self.show_error)

        def show_error(self, msg: str):
            """Show error message."""
            QMessageBox.critical(self, "Error", msg)
            self.stop_engine()

# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Adversarial Red-Team Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with mock detector
  python adversarial_redteam.py --mock --iterations 50
  
  # Run with Hugging Face detector
  python adversarial_redteam.py --detector hf --url http://localhost:8080
  
  # Run with OpenAI
  python adversarial_redteam.py --detector openai --openai-key sk-xxx
  
  # Launch GUI
  python adversarial_redteam.py --gui
        """
    )
    
    parser.add_argument("--mock", action="store_true", help="Use mock detector")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    parser.add_argument("--detector", choices=["mock", "hf", "openai"],
                       default="mock", help="Detector type")
    parser.add_argument("--url", default="http://localhost:8080",
                       help="Classifier URL")
    parser.add_argument("--iterations", type=int, default=50,
                       help="Number of generations")
    parser.add_argument("--population", type=int, default=30,
                       help="Population size")
    parser.add_argument("--openai-key", help="OpenAI API key")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create config
    config = RedTeamConfig()
    config.use_mock = args.mock or args.detector == "mock"
    config.detector_type = args.detector
    config.classifier_endpoint = args.url
    config.max_iterations = args.iterations
    config.population_size = args.population
    
    if args.openai_key:
        config.llm_api_key = args.openai_key
        config.llm_provider = "openai"
    
    # Launch GUI or CLI
    if args.gui and GUI_AVAILABLE:
        app = QApplication([])
        gui = RedTeamGUI()
        gui.show()
        sys.exit(app.exec_())
    elif args.gui and not GUI_AVAILABLE:
        print("[ERROR] PyQt5 not installed. Install with: pip install PyQt5")
        sys.exit(1)
    else:
        # Run CLI
        print("=" * 80)
        print("🔥 ADVERSARIAL RED-TEAM ENGINE")
        print("⚠️  For authorized security testing ONLY")
        print("=" * 80)
        print()
        
        engine = RedTeamEngine(config)
        best_attack, best_score, history = engine.run()
        
        print()
        print("=" * 80)
        print("✅ COMPLETE - RECOMMENDATIONS")
        print("=" * 80)
        print(f"Evasion Score: {best_score:.4f}")
        print(f"Attack Pattern: {best_attack}")
        print()
        print("Actions:")
        print("1. Add this pattern to your test dataset")
        print("2. Update your classifier if needed")
        print("3. Review the full results for analysis")
        print("=" * 80)


if __name__ == "__main__":
    main()
