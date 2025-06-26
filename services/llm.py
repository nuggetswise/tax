"""
LLM service wrapper with multi-provider support and fallback functionality.
Supports OpenAI, Cohere, Groq, and Gemini with automatic fallback.
"""

import os
import json
from typing import Optional, Dict, Any, List
import openai
from openai import OpenAI

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass


class LLMService:
    """Multi-provider LLM service with fallback functionality."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM service with API key and model."""
        self.api_key = api_key
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Initialize providers in order of preference
        self.providers = self._initialize_providers()
        
        if not self.providers:
            raise ValueError(
                "No LLM API keys found. Set at least one of: OPENAI_API_KEY, "
                "COHERE_API_KEY, GROQ_API_KEY, or GEMINI_API_KEY in your .env file. "
                "See env.example for template."
            )
    
    def _initialize_providers(self) -> List[Dict[str, Any]]:
        """Initialize available LLM providers."""
        providers = []
        
        # OpenAI
        openai_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                openai_client = OpenAI(api_key=openai_key)
                providers.append({
                    "name": "OpenAI",
                    "client": openai_client,
                    "model": self.model,
                    "api_key": openai_key,
                    "priority": 1
                })
            except Exception as e:
                print(f"Warning: OpenAI initialization failed: {e}")
        
        # Cohere
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            try:
                import cohere
                cohere_client = cohere.Client(api_key=cohere_key)
                providers.append({
                    "name": "Cohere",
                    "client": cohere_client,
                    "model": "command-r-plus",
                    "api_key": cohere_key,
                    "priority": 2
                })
            except ImportError:
                print("Warning: Cohere package not installed. Install with: poetry install --with optional")
            except Exception as e:
                print(f"Warning: Cohere initialization failed: {e}")
        
        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                groq_client = Groq(api_key=groq_key)
                providers.append({
                    "name": "Groq",
                    "client": groq_client,
                    "model": "llama3-70b-8192",
                    "api_key": groq_key,
                    "priority": 3
                })
            except ImportError:
                print("Warning: Groq package not installed. Install with: poetry install --with optional")
            except Exception as e:
                print(f"Warning: Groq initialization failed: {e}")
        
        # Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                providers.append({
                    "name": "Gemini",
                    "client": genai,
                    "model": "gemini-1.5-pro",
                    "api_key": gemini_key,
                    "priority": 4
                })
            except ImportError:
                print("Warning: Google GenerativeAI package not installed. Install with: poetry install --with optional")
            except Exception as e:
                print(f"Warning: Gemini initialization failed: {e}")
        
        # Sort by priority
        providers.sort(key=lambda x: x["priority"])
        return providers
    
    def chat(
        self, 
        prompt: str, 
        system: Optional[str] = None, 
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a chat completion request with fallback between providers.
        
        Args:
            prompt: User message content
            system: System message (optional)
            temperature: Randomness (0.0 = deterministic)
            max_tokens: Maximum response length
            
        Returns:
            Response content as string
        """
        last_error = None
        
        for provider in self.providers:
            try:
                if provider["name"] == "OpenAI":
                    return self._chat_openai(provider, prompt, system, temperature, max_tokens)
                elif provider["name"] == "Cohere":
                    return self._chat_cohere(provider, prompt, system, temperature, max_tokens)
                elif provider["name"] == "Groq":
                    return self._chat_groq(provider, prompt, system, temperature, max_tokens)
                elif provider["name"] == "Gemini":
                    return self._chat_gemini(provider, prompt, system, temperature, max_tokens)
            except Exception as e:
                last_error = e
                print(f"Warning: {provider['name']} failed: {e}")
                continue
        
        # If all providers failed
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
    
    def _chat_openai(self, provider: Dict[str, Any], prompt: str, system: Optional[str], temperature: float, max_tokens: Optional[int]) -> str:
        """Chat with OpenAI."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = provider["client"].chat.completions.create(
            model=provider["model"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _chat_cohere(self, provider: Dict[str, Any], prompt: str, system: Optional[str], temperature: float, max_tokens: Optional[int]) -> str:
        """Chat with Cohere."""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        response = provider["client"].chat(
            message=full_prompt,
            model=provider["model"],
            temperature=temperature,
            max_tokens=max_tokens or 1000
        )
        return response.text
    
    def _chat_groq(self, provider: Dict[str, Any], prompt: str, system: Optional[str], temperature: float, max_tokens: Optional[int]) -> str:
        """Chat with Groq."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = provider["client"].chat.completions.create(
            model=provider["model"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _chat_gemini(self, provider: Dict[str, Any], prompt: str, system: Optional[str], temperature: float, max_tokens: Optional[int]) -> str:
        """Chat with Gemini."""
        model = provider["client"].GenerativeModel(provider["model"])
        
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
    
    def chat_json(
        self, 
        prompt: str, 
        system: Optional[str] = None, 
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Send a chat completion request and parse JSON response with fallback.
        
        Args:
            prompt: User message content
            system: System message (optional)
            temperature: Randomness (0.0 = deterministic)
            
        Returns:
            Parsed JSON response as dictionary
        """
        response = self.chat(prompt, system, temperature)
        
        # Clean up the response to extract JSON
        cleaned_response = response.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]  # Remove ```
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove trailing ```
        
        cleaned_response = cleaned_response.strip()
        
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [provider["name"] for provider in self.providers]
    
    def get_active_provider(self) -> Optional[str]:
        """Get the name of the currently active provider."""
        if self.providers:
            return self.providers[0]["name"]
        return None


# Global instance for easy access
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

