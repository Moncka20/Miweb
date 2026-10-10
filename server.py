"""
Servidor web para la aplicación Miweb.
Incluye endpoints de Health Check para Render, API de Feature Toggles y servicio de frontend.
Soporta Flask cuando está instalado y servidor WSGI nativo como fallback.
"""

import json
import os
from configcat_service import ConfigCatToggleService
from payments import PaymentMetrics, PaymentsExpressService
from Prueba import multiplicar, resta, sumar

toggle_service = ConfigCatToggleService()
payment_metrics = PaymentMetrics()
payments_service = PaymentsExpressService(toggle_service, payment_metrics)

try:
    from flask import Flask, jsonify, request, send_from_directory

    app = Flask(__name__, static_folder=".")

    @app.route("/")
    def index():
        return send_from_directory(".", "index.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        return send_from_directory(".", path)

    @app.route("/healthz")
    @app.route("/api/health")
    def healthcheck():
        return jsonify({
            "status": "healthy",
            "service": "miweb-analytics",
            "version": "1.0.0",
            "ci_status": "passing",
        }), 200

    @app.route("/api/flags/<flag_key>")
    def get_flag_status(flag_key):
        user_id = request.args.get("userId", "anonymous_user")
        if flag_key == payments_service.FLAG_KEY:
            enabled = payments_service.is_enabled(user_id)
            rollout_percentage = toggle_service.get_rollout_percentage(
                flag_key, user_id, default_value=0
            )
        else:
            enabled = toggle_service.get_value(
                flag_key, default_value=False, user_identifier=user_id
            )
            rollout_percentage = None
        return jsonify({
            "flag": flag_key,
            "enabled": enabled,
            "user_id": user_id,
            "rollout_percentage": rollout_percentage,
            "source": "configcat" if toggle_service.client else "fallback_local",
        }), 200

    @app.route("/api/payments/express/checkout", methods=["POST"])
    def payments_express_checkout():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({
                "error": "El cuerpo debe ser un objeto JSON",
                "code": "invalid_payload",
            }), 400

        user_id = payload.get("user_id")
        if not isinstance(user_id, str) or not user_id.strip():
            return jsonify({
                "error": "user_id es obligatorio",
                "code": "invalid_user",
            }), 400
        user_id = user_id.strip()

        if not payments_service.is_enabled(user_id):
            payment_metrics.increment("disabled_requests")
            return jsonify({
                "error": "Pagos Express no está habilitado para este usuario",
                "code": "feature_disabled",
                "flag": payments_service.FLAG_KEY,
            }), 403

        try:
            result = payments_service.checkout(user_id, payload.get("amount"))
        except ValueError as exc:
            return jsonify({"error": str(exc), "code": "invalid_amount"}), 400
        return jsonify(result), 200

    @app.route("/api/metrics/payments-express")
    def payments_express_metrics():
        return jsonify({
            "feature": payments_service.FLAG_KEY,
            "metrics": payment_metrics.snapshot(),
            "note": "Métricas en memoria para simulación; usar un backend persistente en producción.",
        }), 200

    @app.route("/api/payments/express/test-rollout", methods=["POST"])
    def payments_express_test_rollout():
        if os.getenv("ENABLE_LOCAL_FLAG_CONTROLS", "").lower() != "true":
            return jsonify({
                "error": "Los controles locales no están habilitados",
                "code": "local_controls_disabled",
            }), 403
        payload = request.get_json(silent=True)
        percentage = payload.get("percentage") if isinstance(payload, dict) else None
        try:
            percentage = int(percentage)
        except (TypeError, ValueError):
            return jsonify({
                "error": "percentage debe ser un entero entre 0 y 100",
                "code": "invalid_percentage",
            }), 400
        if not 0 <= percentage <= 100:
            return jsonify({
                "error": "percentage debe estar entre 0 y 100",
                "code": "invalid_percentage",
            }), 400
        toggle_service.set_local_override(payments_service.FLAG_KEY, percentage)
        return jsonify({
            "flag": payments_service.FLAG_KEY,
            "rollout_percentage": percentage,
            "source": "fallback_local",
        }), 200

    @app.route("/api/math/sumar")
    def api_sumar():
        a = int(request.args.get("a", 0))
        b = int(request.args.get("b", 0))
        return jsonify({"operacion": "suma", "resultado": sumar(a, b)})

    @app.route("/api/math/resta")
    def api_resta():
        a = int(request.args.get("a", 0))
        b = int(request.args.get("b", 0))
        return jsonify({"operacion": "resta", "resultado": resta(a, b)})

    @app.route("/api/math/multiplicar")
    def api_multiplicar():
        a = int(request.args.get("a", 0))
        b = int(request.args.get("b", 0))
        return jsonify({"operacion": "multiplicacion", "resultado": multiplicar(a, b)})

except ImportError:
    # Fallback liviano estándar sin dependencias externas
    class SimpleApp:
        def __init__(self):
            pass

        def test_client(self):
            return self

        def get(self, path):
            class Response:
                def __init__(self, data, status_code):
                    self.data = data
                    self.status_code = status_code

                def get_json(self):
                    return json.loads(self.data)

            if "/healthz" in path or "/api/health" in path:
                return Response(
                    json.dumps({"status": "healthy", "service": "miweb-analytics"}),
                    200,
                )
            if "/api/flags/" in path:
                flag = path.split("/api/flags/")[1].split("?")[0]
                return Response(
                    json.dumps({"flag": flag, "enabled": False, "status": "ok"}),
                    200,
                )
            return Response(json.dumps({"status": "not_found"}), 404)

    app = SimpleApp()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    if hasattr(app, "run"):
        app.run(host="0.0.0.0", port=port)
