"""
Servicio de Feature Toggle con integración a ConfigCat.
Soporta inicialización con SDK Key oficial de ConfigCat y fallback seguro
para entornos locales / CI sin conexión o sin API Key.
"""

import os
import hashlib
from typing import Any, Dict, Optional

try:
    import configcatclient
    from configcatclient.user import User as ConfigCatUser

    CONFIGCAT_AVAILABLE = True
except ImportError:
    CONFIGCAT_AVAILABLE = False
    ConfigCatUser = None


class ConfigCatToggleService:
    def __init__(self, sdk_key: Optional[str] = None):
        self.sdk_key = sdk_key or os.getenv("CONFIGCAT_SDK_KEY")
        self.client = None
        self._local_overrides: Dict[str, Any] = {
            "dark_mode_enabled": False,
            "nueva-funcionalidad-x": False,
            # Percentage rollout. Production starts completely OFF.
            "pagos-express-v1": 0,
        }

        if self.sdk_key and CONFIGCAT_AVAILABLE:
            try:
                self.client = configcatclient.get(self.sdk_key)
            except Exception:
                self.client = None

    def get_value(
        self,
        flag_key: str,
        default_value: Any = False,
        user_identifier: Optional[str] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Evalúa el valor del Feature Toggle en ConfigCat.
        Si no hay conexión o SDK Key, utiliza la configuración local de respaldo.
        """
        if self.client and CONFIGCAT_AVAILABLE:
            try:
                user = None
                if user_identifier:
                    user = ConfigCatUser(
                        identifier=user_identifier,
                        custom=custom_attributes or {},
                    )
                return self.client.get_value(flag_key, default_value, user)
            except Exception:
                pass

        return self._local_overrides.get(flag_key, default_value)

    def set_local_override(self, flag_key: str, value: Any) -> None:
        """Permite sobrescribir flags en tests o modo offline."""
        self._local_overrides[flag_key] = value

    def get_rollout_percentage(
        self, flag_key: str, user_identifier: str, default_value: int = 0
    ) -> int:
        """Returns whether a user belongs to a deterministic percentage rollout."""
        value = self.get_value(
            flag_key,
            default_value=default_value,
            user_identifier=user_identifier,
        )
        if isinstance(value, bool):
            return 100 if value else 0
        try:
            percentage = int(value)
        except (TypeError, ValueError):
            return default_value
        return max(0, min(100, percentage))

    def is_enabled_for_user(
        self, flag_key: str, user_identifier: str, default_value: int = 0
    ) -> bool:
        """Evaluates a stable user cohort for a percentage-based toggle."""
        percentage = self.get_rollout_percentage(
            flag_key, user_identifier, default_value
        )
        if percentage == 0:
            return False
        if percentage == 100:
            return True
        bucket = int(
            hashlib.md5(user_identifier.encode("utf-8")).hexdigest(), 16
        ) % 100
        return bucket < percentage

    def close(self) -> None:
        """Cierra el cliente de ConfigCat limpiando recursos."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
