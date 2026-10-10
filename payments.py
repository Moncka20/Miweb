"""Safe, observable simulation of the Pagos Express release."""

from decimal import Decimal, InvalidOperation
from threading import Lock
from typing import Any, Dict
from uuid import uuid4

from configcat_service import ConfigCatToggleService


class PaymentMetrics:
    """Process-local counters for the workshop and smoke tests."""

    def __init__(self):
        self._lock = Lock()
        self._counters = {
            "attempts": 0,
            "successful_payments": 0,
            "failed_payments": 0,
            "disabled_requests": 0,
        }

    def increment(self, name: str) -> None:
        with self._lock:
            self._counters[name] += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            data = dict(self._counters)
        attempts = data["attempts"]
        data["conversion_rate"] = (
            round(data["successful_payments"] / attempts, 4)
            if attempts
            else 0.0
        )
        data["failure_rate"] = (
            round(data["failed_payments"] / attempts, 4) if attempts else 0.0
        )
        return data


class PaymentsExpressService:
    """Feature-gated payment simulation; it never charges a real provider."""

    FLAG_KEY = "pagos-express-v1"

    def __init__(
        self,
        toggle_service: ConfigCatToggleService,
        metrics: PaymentMetrics,
    ):
        self.toggle_service = toggle_service
        self.metrics = metrics

    def is_enabled(self, user_id: str) -> bool:
        return self.toggle_service.is_enabled_for_user(
            self.FLAG_KEY, user_id, default_value=0
        )

    def checkout(self, user_id: str, amount: Any) -> Dict[str, Any]:
        self.metrics.increment("attempts")
        try:
            parsed_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError) as exc:
            self.metrics.increment("failed_payments")
            raise ValueError("amount debe ser un número válido") from exc

        if not parsed_amount.is_finite() or parsed_amount <= 0:
            self.metrics.increment("failed_payments")
            raise ValueError("amount debe ser mayor que cero")

        self.metrics.increment("successful_payments")
        return {
            "payment_id": f"pex_{uuid4().hex}",
            "status": "succeeded",
            "user_id": user_id,
            "amount": str(parsed_amount),
            "currency": "COP",
            "simulation": True,
        }
