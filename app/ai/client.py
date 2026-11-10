import httpx

from app.schemas.ai import ChatRequest


class AIClientError(Exception):
    """Базовая ошибка AI-клиента."""


class InvalidAPIKeyError(AIClientError):
    """Невалидный API-ключ."""


class AIClient:
    """
    Универсальный AI-клиент с поддержкой BYOK.

    Пример:
        client = AIClient(provider="openrouter", api_key="sk-or-v1-...")
        answer = await client.chat(request)
    """

    PROVIDER_URLS: dict[str, str] = {
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
        "gemini": "https://generativelanguage.googleapis.com/v1beta",
    }

    def __init__(self, provider: str, api_key: str) -> None:
        if provider not in self.PROVIDER_URLS:
            raise ValueError(
                f"Неизвестный провайдер '{provider}'. Доступные: {list(self.PROVIDER_URLS.keys())}"
            )
        if not api_key:
            raise InvalidAPIKeyError("API-ключ не может быть пустым")

        self.provider = provider
        self.api_key = api_key
        self.base_url = self.PROVIDER_URLS[provider]

    async def chat(self, request: ChatRequest) -> str:
        """Отправляет запрос к AI и возвращает текстовый ответ."""
        if self.provider == "openrouter":
            return await self._chat_openrouter(request)
        if self.provider == "gemini":
            return await self._chat_gemini(request)
        raise AIClientError(f"Провайдер {self.provider} не реализован")

    async def _chat_openrouter(self, request: ChatRequest) -> str:
        """OpenRouter — OpenAI-совместимый API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/evelyn",
        }
        payload = {
            "model": request.model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)

        if resp.status_code == 401:
            raise InvalidAPIKeyError("Невалидный OpenRouter API-ключ")
        if resp.status_code != 200:
            raise AIClientError(f"OpenRouter {resp.status_code}: {resp.text}")

        data = resp.json()
        return str(data["choices"][0]["message"]["content"])

    async def _chat_gemini(self, request: ChatRequest) -> str:
        """Gemini — собственный формат API."""
        url = f"{self.base_url}/models/{request.model}:generateContent"
        params = {"key": self.api_key}

        system_parts: list[str] = []
        contents: list[dict[str, object]] = []

        for msg in request.messages:
            if msg.role == "system":
                system_parts.append(msg.content)
            else:
                gemini_role = "user" if msg.role == "user" else "model"
                contents.append(
                    {
                        "role": gemini_role,
                        "parts": [{"text": msg.content}],
                    }
                )

        payload: dict[str, object] = {
            "contents": contents,
            "generationConfig": {"temperature": request.temperature},
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, params=params, json=payload)

        if resp.status_code == 400 and "API_KEY_INVALID" in resp.text:
            raise InvalidAPIKeyError("Невалидный Gemini API-ключ")
        if resp.status_code != 200:
            raise AIClientError(f"Gemini {resp.status_code}: {resp.text}")

        data = resp.json()
        return str(data["candidates"][0]["content"]["parts"][0]["text"])
