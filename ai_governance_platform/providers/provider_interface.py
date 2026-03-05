from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class StubProvider(AIProvider):
    def generate_response(self, prompt: str) -> str:
        # Simple stub logic for demonstration
        if "salary" in prompt:
            if "own" in prompt:
                return "Your salary is confidential."
            elif "Technology" in prompt:
                return "Technology department salaries are confidential."
            elif "all" in prompt or "employee" in prompt:
                return "All employee salaries are confidential."
        elif "deploy" in prompt or "production" in prompt:
            return "Production deploy steps are restricted."
        return "No relevant information found."
