"""
Token Manager - Gestion dynamique de la longueur des réponses
Le modérateur peut ajuster la longueur des réponses des agents
"""

class TokenManager:
    """Gestionnaire de tokens pour contrôler la longueur des débats"""
    
    def __init__(self):
        self.current_max_tokens = 250  # Par défaut
        self.min_tokens = 100  # Minimum pour éviter réponses trop courtes
        self.max_tokens = 400  # Maximum pour éviter réponses trop longues
        
        # Presets pour différents styles de débat
        self.presets = {
            "rapide": 150,      # Débat rapide, réponses courtes
            "normal": 250,      # Débat standard  
            "détaillé": 350,    # Débat approfondi
            "express": 100      # Débat ultra-rapide
        }
    
    def set_tokens(self, token_count):
        """Définit le nombre de tokens (avec limites)"""
        if token_count < self.min_tokens:
            self.current_max_tokens = self.min_tokens
        elif token_count > self.max_tokens:
            self.current_max_tokens = self.max_tokens
        else:
            self.current_max_tokens = token_count
        
        return self.current_max_tokens
    
    def set_preset(self, preset_name):
        """Utilise un preset défini"""
        if preset_name in self.presets:
            self.current_max_tokens = self.presets[preset_name]
            return True
        return False
    
    def get_current_tokens(self):
        """Récupère le nombre de tokens actuel"""
        return self.current_max_tokens
    
    def get_token_instruction(self):
        """Génère l'instruction de longueur pour les agents"""
        return f"IMPORTANT: Limite ta réponse à maximum {self.current_max_tokens} tokens (environ {self.current_max_tokens // 4} mots). Sois concis et percutant!"
    
    def adjust_for_round(self, round_number):
        """Ajuste les tokens selon le round (optionnel)"""
        if round_number <= 2:
            # Premiers rounds plus longs pour poser le débat
            return self.current_max_tokens + 50
        else:
            # Rounds suivants plus courts pour le dynamisme
            return max(self.current_max_tokens - 20, self.min_tokens)
    
    def get_available_presets(self):
        """Liste des presets disponibles"""
        return list(self.presets.keys())


# Instance globale pour tout le système
token_manager = TokenManager()