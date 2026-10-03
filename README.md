# Informacion Importante
- Nuevo readme modificado
- Proyecto Ordenado
- Issues a cargo de Thomas

---

## 🌓 Estrategia de Rollout: Modo Oscuro (Dark Mode) en Dashboard

Implementación progresiva dividida en 3 tickets para entrega continua y bajo riesgo:

### 📋 Ticket 1: Variables CSS / Tema Oscuro y Lógica Raíz
- **Definición de diseño:** Variables CSS (`--bg-primary`, `--bg-surface`, `--text-primary`, etc.) en `:root` y `:root[data-theme="dark"]` en [`styles.css`](file:///c:/TDSW/Miweb/styles.css).
- **Lógica raíz:** Cambio de atributo `data-theme` en [`app.js`](file:///c:/TDSW/Miweb/app.js).
- **Feature Flag:** `dark_mode_enabled: false` (0% rollout, botón oculto).

### 📋 Ticket 2: Toggle Visible para Canary Rollout (10%)
- **Rollout Canario:** Evaluación determinista basada en el percentil del usuario (`cohortPercentile < 10%`).
- **Visibilidad:** Botón toggle visible solo para el grupo experimental del 10%.
- **Persistencia:** Deshabilitada temporalmente en esta fase (en memoria).

### 📋 Ticket 3: Persistencia y Lanzamiento Global (100% GA)
- **Persistencia:** Almacenamiento en `localStorage` (`nexus_dash_theme_preference`) o backend.
- **Rollout 100%:** Flag activado a nivel global (100%).

### 🧪 Pruebas y Validación
- **Tests unitarios:** [`test_prueba.py`](file:///c:/TDSW/Miweb/test_prueba.py) valida los 3 tickets y las funciones matemáticas existentes.
- **Linter & CI:** Cumplimiento total con `ruff` y workflows de GitHub Actions intactos en [`.github/workflows/ci.yaml`](file:///c:/TDSW/Miweb/.github/workflows/ci.yaml).