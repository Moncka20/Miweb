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

---

## 💳 Pagos Express: liberación segura

La funcionalidad `pagos-express-v1` está implementada como una simulación
observable y comienza con rollout `0%`. No realiza cargos reales a un proveedor
de pagos.

### Endpoints

```text
GET  /api/flags/pagos-express-v1?userId=<usuario>
POST /api/payments/express/checkout
GET  /api/metrics/payments-express
```

Ejemplo de checkout:

```json
{
  "user_id": "internal_reviewer",
  "amount": "10000"
}
```

El checkout responde `403` mientras el usuario no pertenezca a la audiencia
habilitada. El rollout local se controla con un porcentaje entero:

```python
toggle_service.set_local_override("pagos-express-v1", 5)
```

El mismo usuario siempre recibe la misma decisión dentro de un porcentaje.
ConfigCat puede administrar el valor del flag; en local o CI se utiliza el
fallback seguro apagado. Las métricas actuales son contadores en memoria para
la práctica y deben reemplazarse por un sistema persistente antes de operar
pagos reales.

### Configuración del rollout en ConfigCat

La variable `CONFIGCAT_SDK_KEY` ya está configurada localmente en `.env`.
No se debe copiar su valor al repositorio, a Miro, a un issue o a una captura
de pantalla. En Render debe configurarse como secret environment variable.

En ConfigCat:

1. Abrir el proyecto y seleccionar el entorno que utiliza Render.
2. Crear un setting de tipo **Number** con la clave exacta
   `pagos-express-v1`.
3. Establecer el valor por defecto en `0`.
4. Publicar la configuración.
5. Crear las reglas de targeting en este orden:

   - **Usuarios internos:** condición `Identifier is one of`
     `internal_reviewer` y los usuarios de prueba autorizados; valor `100`.
   - **Canary:** para el resto de usuarios, activar el porcentaje de
     distribución al `5%`; valor `5`.
   - **Ampliación:** después de la observación aprobada, cambiar la
     distribución al `20%`; valor `20`.
   - **General Availability:** después de dos observaciones sanas, cambiar
     la distribución al `100%`; valor `100`.

6. En cada cambio, guardar y publicar una nueva versión de la configuración.
7. Registrar en el tablero de liberación: versión publicada, hora, porcentaje,
   owner, métricas observadas y decisión.

La secuencia operativa es:

| Fase | Regla en ConfigCat | Valor |
| --- | --- | ---: |
| Inicial | Sin targeting para usuarios finales | `0` |
| Usuarios internos | Identificador incluido en la lista interna | `100` |
| Canary | Porcentaje de usuarios | `5` |
| Ampliación | Porcentaje de usuarios | `20` |
| General Availability | Porcentaje de usuarios | `100` |

No se debe activar el `20%` si todavía no están disponibles la conversión,
los errores de pago, el health check y el procedimiento de rollback. Para
volver a una situación segura, publicar nuevamente el valor `0` o el
porcentaje anterior.

### Verificación posterior a cada publicación

Consultar el endpoint para un usuario interno y otro fuera de la audiencia:

```powershell
Invoke-RestMethod "http://localhost:8080/api/flags/pagos-express-v1?userId=internal_reviewer"
Invoke-RestMethod "http://localhost:8080/api/flags/pagos-express-v1?userId=external_test_user"
```

La respuesta debe incluir `flag`, `enabled`, `user_id`, `rollout_percentage` y
`source`. En producción, `source` debe indicar `configcat`; si indica
`fallback_local`, se debe detener el rollout y corregir la configuración del
SDK antes de continuar.

### Laboratorio visual local

El dashboard incluye la sección **Pagos Express** para consultar el flag,
probar el checkout simulado y ver las métricas de la sesión. Para habilitar
los botones de `OFF`, `5%`, `20%` y `100%` únicamente en local:

```env
ENABLE_LOCAL_FLAG_CONTROLS=true
```

Después de cambiar `.env`, reiniciar el servidor y abrir
`http://localhost:8080`. En Render esta variable debe permanecer ausente o en
`false`; el rollout real se controla exclusivamente desde ConfigCat.

El botón **Probar Pagos Express** nunca realiza cargos reales. Si el usuario
no pertenece a la audiencia activa, la interfaz muestra `feature_disabled`
con HTTP `403`. El panel de métricas muestra contadores en memoria y sirve
para la simulación del taller.