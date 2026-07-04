import os
from dotenv import load_dotenv
from openai import OpenAI

from config.settings import OPENAI_MODEL
from utils.openai_completion import chat_token_kwargs

load_dotenv()

_FACTUAL_SUFFIX = (
    "\n\nIMPORTANT: Utilise tes connaissances les plus récentes (entraînement jusqu'en 2024). "
    "Quand tu mentionnes des statistiques, études ou faits, précise toujours la source approximative "
    "(ex: 'selon des études récentes', 'données 2024', etc). Sois factuel et cite des ordres de grandeur réalistes."
)


class BaseAgent:
    """Base class for AI agents using OpenAI API with native web search"""
    
    def __init__(self, model=OPENAI_MODEL, temperature=0.7, max_tokens=500):
        
        # Startup sanity check
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Error: OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @staticmethod
    def _with_factual_suffix(system_prompt: str) -> str:
        return system_prompt + _FACTUAL_SUFFIX

    def _chat_completion_kwargs(self, **extra):
        """Kwargs communs pour ``chat.completions.create`` (GPT-5 → max_completion_tokens)."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            **chat_token_kwargs(self.model, self.max_tokens),
            **extra,
        }
        
    def generate_response(self, user_input, system_prompt="You are a helpful AI assistant."):
        """Generate a response using OpenAI's Chat Completions API"""
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                **self._chat_completion_kwargs(),
            )
            
            # Extract the response content from the Chat Completion response
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                if hasattr(message, 'content') and message.content:
                    return message.content.strip()
            
            return "Error: No content found in response"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_response_with_search(self, user_input, system_prompt="You are a helpful AI assistant.", search_callback=None):
        """
        Generate a response with native OpenAI web search capability
        GPT-4o can now search the web directly when needed
        """
        try:
            enhanced_prompt = self._with_factual_suffix(system_prompt)
            if search_callback:
                search_callback("🔍 AI peut rechercher sur le web si nécessaire...")
            
            messages = [
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Création des paramètres de base
            params = self._chat_completion_kwargs(
                messages=messages,
            )
            
            # Utiliser Responses API avec web search si activé
            if hasattr(self, 'enable_web_search') and self.enable_web_search:
                # Responses API avec web_search_preview (syntax correcte!)
                full_input = f"{enhanced_prompt}\n\nUser: {user_input}"
                
                response = self.client.responses.create(
                    model=self.model,
                    tools=[{"type": "web_search_preview"}],
                    input=full_input
                )
                
                # Récupérer le texte de sortie
                if hasattr(response, 'output_text'):
                    return response.output_text.strip()
                else:
                    return str(response)
            else:
                # Fallback Chat Completions sans web search
                response = self.client.chat.completions.create(**params)
                
                response_message = response.choices[0].message
                
                if hasattr(response_message, 'content') and response_message.content:
                    return response_message.content.strip()
                
                return "Error: No content found in response"
            
        except Exception as e:
            return f"Error: {str(e)}"

    def get_persona_vector(self):
        """Vecteur personnage ONPC ; surchargé par les sous-classes."""
        from config.debate_graph import get_persona_vector

        return get_persona_vector("optimiste")

    def generate_react_debate_turn(
        self,
        user_input,
        system_prompt="You are a helpful AI assistant.",
        stream_callback=None,
        search_callback=None,
        step_callback=None,
        topic="",
    ):
        """
        Tour de débat : graphe LangGraph débatteur ONPC (voir `agents.react.graph`).
        """
        from agents.react.executor import run_react_turn

        return run_react_turn(
            client=self.client,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system_prompt=self._with_factual_suffix(system_prompt),
            user_input=user_input,
            enable_web_search=getattr(self, "enable_web_search", False),
            stream_callback=stream_callback,
            search_callback=search_callback,
            step_callback=step_callback,
            persona_vector=self.get_persona_vector(),
            topic=topic,
        )

    def generate_streaming_response(self, user_input, system_prompt="You are a helpful AI assistant.", callback=None):
        """Generate a streaming response using OpenAI's Chat Completions API"""
        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                stream=True,
                **self._chat_completion_kwargs(),
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    if callback:
                        callback(content)
            
            return full_response.strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_streaming_response_with_search(self, user_input, system_prompt="You are a helpful AI assistant.", 
                                               stream_callback=None, search_callback=None):
        """
        Generate a streaming response with native OpenAI web search capability
        """
        try:
            enhanced_prompt = self._with_factual_suffix(system_prompt)
            if search_callback:
                search_callback("🔍 Recherche web activée...")
            
            messages = [
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": user_input}
            ]

            stream = self.client.chat.completions.create(
                stream=True,
                **self._chat_completion_kwargs(messages=messages),
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    if stream_callback:
                        stream_callback(content)
            
            return full_response.strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def set_model(self, model_name):
        """Set the OpenAI model to use"""
        self.model = model_name
    
    def set_temperature(self, temperature):
        """Set temperature for response generation (0.0 to 2.0)"""
        if 0.0 <= temperature <= 2.0:
            self.temperature = temperature
    
    def set_max_tokens(self, max_tokens):
        """Set the maximum tokens for response"""
        self.max_tokens = max_tokens