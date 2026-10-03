import unittest

from configcat_service import ConfigCatToggleService
from feature_flags import FeatureFlagService
from Prueba import multiplicar, resta, sumar
from server import app


class PruebaOperaciones(unittest.TestCase):
    def test_sumar(self):
        self.assertEqual(sumar(2, 3), 5)

    def test_resta(self):
        self.assertEqual(resta(5, 3), 2)

    def test_multiplicar(self):
        self.assertEqual(multiplicar(4, 3), 12)


class PruebaDarkModeRolloutTickets(unittest.TestCase):
    def setUp(self):
        self.service = FeatureFlagService()
        self.user_id = "user_test_123"

    def test_ticket_1_flag_apagado(self):
        """Ticket 1: Flag dark_mode_enabled apagado (0% rollout)."""
        is_enabled = self.service.is_dark_mode_enabled(self.user_id, rollout_percentage=0)
        self.assertFalse(is_enabled)

    def test_ticket_2_canary_rollout_sin_persistencia(self):
        """Ticket 2: Flag al 10% canary, sin persistencia."""
        percentile = self.service.get_user_percentile(self.user_id)
        expected_flag = percentile < 10
        self.assertEqual(
            self.service.is_dark_mode_enabled(self.user_id, rollout_percentage=10),
            expected_flag,
        )

        persisted = self.service.save_preference(
            self.user_id, "dark", persistence_allowed=False
        )
        self.assertFalse(persisted)
        self.assertIsNone(self.service.get_preference(self.user_id))

    def test_ticket_3_ga_100_con_persistencia(self):
        """Ticket 3: Flag al 100% y persistencia habilitada."""
        self.assertTrue(
            self.service.is_dark_mode_enabled(self.user_id, rollout_percentage=100)
        )
        persisted = self.service.save_preference(
            self.user_id, "dark", persistence_allowed=True
        )
        self.assertTrue(persisted)
        self.assertEqual(self.service.get_preference(self.user_id), "dark")


class PruebaConfigCatIntegration(unittest.TestCase):
    def setUp(self):
        self.toggle_service = ConfigCatToggleService()

    def test_fallback_local_default_value(self):
        """Verifica que el servicio responda valores por defecto de forma segura."""
        val = self.toggle_service.get_value("feature_inexistente", default_value=False)
        self.assertFalse(val)

    def test_override_local_toggle(self):
        """Verifica la capacidad de sobrescribir flags para pruebas."""
        self.toggle_service.set_local_override("nueva-funcionalidad-x", True)
        val = self.toggle_service.get_value("nueva-funcionalidad-x")
        self.assertTrue(val)


class PruebaServerEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_healthz_endpoint(self):
        """Endpoint de Health Check requerido por Render."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_api_flags_endpoint(self):
        """Endpoint de consulta de Feature Flags."""
        response = self.client.get("/api/flags/dark_mode_enabled?userId=usr_10")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("enabled", data)
        self.assertEqual(data["flag"], "dark_mode_enabled")


if __name__ == "__main__":
    unittest.main()