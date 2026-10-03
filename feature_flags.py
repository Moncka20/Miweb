"""
Módulo de Gestión de Feature Flags para Modo Oscuro.
Implementa la arquitectura de división en 3 tickets:
- Ticket 1: Flag base apagado (0%).
- Ticket 2: Rollout canary (10%) sin persistencia.
- Ticket 3: Rollout GA (100%) con persistencia de preferencia.
"""

import hashlib
from typing import Optional


class FeatureFlagService:
    def __init__(self):
        self._persistence_store = {}

    @staticmethod
    def get_user_percentile(user_id: str) -> int:
        """Determina de forma determinista el percentil del usuario (0-99)."""
        hash_val = int(hashlib.md5(user_id.encode("utf-8")).hexdigest(), 16)
        return hash_val % 100

    def is_dark_mode_enabled(self, user_id: str, rollout_percentage: int = 0) -> bool:
        """
        Evalúa si el flag dark_mode_enabled está activo para el usuario.
        - Ticket 1: rollout_percentage = 0 (Flag apagado).
        - Ticket 2: rollout_percentage = 10 (Canary 10%).
        - Ticket 3: rollout_percentage = 100 (GA 100%).
        """
        if rollout_percentage <= 0:
            return False
        if rollout_percentage >= 100:
            return True
        return self.get_user_percentile(user_id) < rollout_percentage

    def save_preference(
        self, user_id: str, theme: str, persistence_allowed: bool = False
    ) -> bool:
        """
        Guarda la preferencia del tema si la fase permite persistencia.
        - Ticket 2: persistence_allowed = False -> No persiste.
        - Ticket 3: persistence_allowed = True -> Persiste en almacenamiento.
        """
        if not persistence_allowed:
            return False
        self._persistence_store[user_id] = theme
        return True

    def get_preference(self, user_id: str) -> Optional[str]:
        """Obtiene la preferencia guardada de un usuario."""
        return self._persistence_store.get(user_id)
