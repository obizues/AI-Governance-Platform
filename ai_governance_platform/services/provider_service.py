"""
Provider Management Service Module
Centralizes provider interface logic for the AI Document Governance Platform.
"""

from typing import Any, Dict


class StubProvider:
    def get_data(self, query: str) -> Dict[str, Any]:
        return {"result": f"Stubbed response for query: {query}"}

class ProviderService:
    def __init__(self, provider=None):
        self.provider = provider or StubProvider()


    def set_provider(self, provider):
        self.provider = provider

    def get_data(self, query: str) -> Dict[str, Any]:
        return self.provider.get_data(query)

    def get_provider_info(self) -> Dict[str, Any]:
        return {"provider": self.provider.__class__.__name__}
