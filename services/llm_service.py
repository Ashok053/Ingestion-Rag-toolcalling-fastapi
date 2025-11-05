from core.configuration import settings

class LLMService:
    """
    LLM service supporting currently Groq.
    """

    def __init__(self):
        self.client = None
        self.provider = None

        if settings.GROQ_API_KEY:
            self._init_groq()
        else:
            print("No Groq API key found in settings. LLM will not work.")

    def _init_groq(self):
        """Initialize Groq client with API key."""
        try:
            from groq import Groq
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.provider = "groq"
            print("Using Groq LLM.")
        except Exception as e:
            print(f"Groq initialization failed: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.5) -> str:
        """
        Generate a response from the LLM.
        Args:
            prompt: User input or context.
            max_tokens: Max tokens for output.
            temperature: Creativity level.
        Returns:
            Generated text from LLM.
        """
        if not self.client:
            raise RuntimeError("LLM client is not initialized.")

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system",
                 "content": "You are a helpful AI assistant answering questions based on provided context. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content


llm_service = LLMService()
