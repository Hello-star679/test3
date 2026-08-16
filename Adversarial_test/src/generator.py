"""
Text generator for benign test content.
Uses templates with placeholders to create variations.
"""

import random
import string
import os
from typing import List, Optional, Dict, Any

class ConfigurableGenerator:
    """
    Generates benign test text from pre-approved templates.
    Supports multiple categories, mutations, and placeholder substitution.
    """
    
    def __init__(
        self,
        template_file: str = "templates/general.txt",
        categories: Optional[List[str]] = None,
        use_categories: bool = False,
        templates_dir: str = "templates"
    ):
        self.template_file = template_file
        self.templates_dir = templates_dir
        self.use_categories = use_categories
        self.categories = categories or ["account", "security", "transactions", "general"]
        self.templates_by_category = {}
        self.all_templates = []
        
        # Safe placeholder words - NEVER use actual scam language
        self.placeholders = {
            "noun": ["user", "account", "system", "profile", "device", "application", "service", "team"],
            "verb": ["verify", "update", "confirm", "review", "complete", "process", "check", "validate"],
            "adjective": ["important", "secure", "pending", "active", "current", "recent", "new", "updated"],
            "object": ["password", "email", "phone", "address", "payment", "transaction", "invoice", "receipt"],
            "action": ["verification", "confirmation", "review", "update", "processing", "validation"],
            "time": ["today", "now", "soon", "immediately", "shortly", "within 24 hours"]
        }
        
        # Load templates
        self._load_templates()
        
        if not self.all_templates:
            print("[WARN] No templates loaded. Using fallback templates.")
            self.all_templates = self._get_fallback_templates()
    
    def _load_templates(self):
        """Load templates from files in the templates directory."""
        if self.use_categories:
            # Load from category-specific files
            for category in self.categories:
                filepath = os.path.join(self.templates_dir, f"{category}.txt")
                templates = self._load_template_file(filepath)
                if templates:
                    self.templates_by_category[category] = templates
                    self.all_templates.extend(templates)
                else:
                    print(f"[WARN] No templates found for category: {category}")
        else:
            # Load from single file
            templates = self._load_template_file(self.template_file)
            if templates:
                self.all_templates = templates
                self.templates_by_category["general"] = templates
    
    def _load_template_file(self, filepath: str) -> List[str]:
        """Load templates from a specific file, ignoring comments."""
        templates = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        templates.append(line)
        except FileNotFoundError:
            print(f"[WARN] Template file not found: {filepath}")
        except Exception as e:
            print(f"[ERROR] Failed to load templates from {filepath}: {e}")
        return templates
    
    def _get_fallback_templates(self) -> List[str]:
        """Fallback templates if no files are found."""
        return [
            "Your {} needs {}.",
            "Please {} your {}.",
            "The {} requires {} for {}.",
            "We have sent a {} to your {}.",
            "Complete the {} to {} your {}.",
            "Your {} has been {}.",
            "Click here to {} your {}.",
            "Verify your {} by {}.",
            "Update your {} settings.",
            "Confirm your {} address.",
            "A new {} has been added to your account.",
            "Your {} is about to expire.",
            "Please {} your {}.",
            "We detected {} on your {}.",
            "Your {} has been {} successfully."
        ]
    
    def generate(self, category: Optional[str] = None) -> str:
        """
        Generate a test string from a template.
        If category is specified, only use templates from that category.
        """
        if category and category in self.templates_by_category:
            templates = self.templates_by_category[category]
        else:
            templates = self.all_templates
        
        if not templates:
            return "Test placeholder text."
        
        template = random.choice(templates)
        
        # Count placeholders and fill them
        count = template.count('{}')
        if count == 0:
            return template
        
        # Fill with random placeholder words
        fillers = []
        for _ in range(count):
            word_type = random.choice(list(self.placeholders.keys()))
            fillers.append(random.choice(self.placeholders[word_type]))
        
        return template.format(*fillers)
    
    def mutate(self, text: str) -> str:
        """
        Apply small, random changes to the text.
        Mutation types:
        - Character substitution
        - Word substitution
        - Word insertion
        - Word deletion
        - Case change
        - Punctuation change
        """
        if not text:
            return self.generate()
        
        mutation_type = random.random()
        
        # Character substitution
        if mutation_type < 0.2:
            chars = list(text)
            if chars:
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz ')
                return ''.join(chars)
            return text
        
        # Word substitution
        elif mutation_type < 0.4:
            words = text.split()
            if len(words) > 2:
                idx = random.randint(0, len(words) - 1)
                word_type = random.choice(list(self.placeholders.keys()))
                words[idx] = random.choice(self.placeholders[word_type])
                return ' '.join(words)
            return text
        
        # Word insertion
        elif mutation_type < 0.6:
            words = text.split()
            if len(words) > 1:
                idx = random.randint(0, len(words))
                word_type = random.choice(list(self.placeholders.keys()))
                words.insert(idx, random.choice(self.placeholders[word_type]))
                return ' '.join(words)
            return text + " " + random.choice(self.placeholders["noun"])
        
        # Word deletion
        elif mutation_type < 0.75:
            words = text.split()
            if len(words) > 3:
                del words[random.randint(0, len(words) - 1)]
                return ' '.join(words)
            return text
        
        # Case change
        elif mutation_type < 0.85:
            chars = list(text)
            if chars:
                idx = random.randint(0, len(chars) - 1)
                if chars[idx].isalpha():
                    chars[idx] = chars[idx].swapcase()
                return ''.join(chars)
            return text
        
        # Punctuation change
        else:
            if text.endswith('.'):
                return text[:-1] + '!'
            elif text.endswith('!'):
                return text[:-1] + '?'
            elif text.endswith('?'):
                return text[:-1] + '.'
            else:
                return text + random.choice(['.', '!', '?'])
    
    def generate_population(self, size: int, category: Optional[str] = None) -> List[str]:
        """Generate a population of texts."""
        return [self.generate(category) for _ in range(size)]
    
    def get_categories(self) -> List[str]:
        """Return available categories."""
        return list(self.templates_by_category.keys())
