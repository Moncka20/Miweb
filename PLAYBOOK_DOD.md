# 📘 Playbook de Trunk-Based Development (TBD), Definition of Done (DoD) y Continuous Deployment

Este documento formaliza los acuerdos técnicos, de negocio y de despliegue del equipo para garantizar entregas continuas y confiables en producción.

---

## 🎯 Objetivo de Fase 1 (Completada 100% ✅)

Cerrar los 3 pilares indispensables para el flujo de Trunk-Based Development (TBD):
1. **Auto-deploy continuo desde `main` a Render**.
2. **Feature Toggle con ConfigCat** para desacoplar el despliegue de la liberación de funcionalidades.
3. **Definition of Done (DoD)** formalizado y aplicado en el pipeline automatizado.

---

## ✅ Checklist de Fase 1

- [x] Repositorio configurado con Branch Protection en `main`.
- [x] Contenedor Docker estandarizado ([`Dockerfile`](file:///c:/TDSW/Miweb/Dockerfile)).
- [x] Pipeline de CI con linter (`ruff`) y tests automatizados ([`.github/workflows/ci.yaml`](file:///c:/TDSW/Miweb/.github/workflows/ci.yaml)).
- [x] Publicación automática de imágenes a GitHub Container Registry (GHCR).
- [x] Especificación de despliegue en Render ([`render.yaml`](file:///c:/TDSW/Miweb/render.yaml)) con endpoint de salud `/healthz`.
- [x] Feature Toggle SDK integrado ([`configcat_service.py`](file:///c:/TDSW/Miweb/configcat_service.py)) con soporte offline/mock.
- [x] Suite de pruebas automatizadas completa ([`test_prueba.py`](file:///c:/TDSW/Miweb/test_prueba.py)).
- [x] Definition of Done documentado y acordado por el equipo.
- [x] Formato de Sprint Review adaptado a despliegues continuos.
- [x] Formato de Sprint Retrospective orientado al flujo de valor y salud del pipeline.
- [x] Política de liberación progresiva con Feature Toggles, observabilidad y rollback.

---

## 📋 Definition of Done (DoD) Definitivo

Una historia de usuario o cambio técnico se considera **DONE** solo cuando cumple la totalidad de los siguientes criterios:

### 1. ⚙️ Calidad Técnica y Código
- [ ] El código sigue las pautas de estilo y pasa el linter estático (`ruff check .` sin advertencias).
- [ ] Todos los tests unitarios y de integración pasan en verde (`pytest`).
- [ ] No se agregan dependencias sin justificación en `requirements.txt`.
- [ ] No existen ramas de larga duración (vida máxima de rama: < 24 horas).

### 2. 🚩 Desacople con Feature Toggles (ConfigCat)
- [ ] Si la funcionalidad está en desarrollo o incompleta, **debe estar protegida detrás de un Feature Toggle** (`dark_mode_enabled`, `nueva-funcionalidad-x`, `pagos-express-v1`).
- [ ] El comportamiento predeterminado del flag en producción debe ser `OFF` hasta su validación.
- [ ] El toggle tiene un owner, audiencia, métrica, criterio de avance, criterio de rollback y fecha de retiro.
- [ ] Se incluye plan de retiro técnico del toggle una vez alcanzado el 100% GA.

### 3. 🚀 Despliegue y Operación (Render)
- [ ] El commit está integrado en `main` mediante Pull Request validado por CI.
- [ ] La imagen Docker se compila y publica en GHCR.
- [ ] El servicio se auto-despliega en Render y el endpoint `/healthz` responde `200 OK`.
- [ ] La versión anterior cuenta con capacidad de Rollback inmediato.

---

## 🚦 Regla de Oro del Equipo

> **"Si el CI está en rojo, se detiene la adición de nuevas features hasta que vuelva a estar en verde."**

---

## 🔎 Separación obligatoria: integrar, desplegar y liberar

El equipo debe utilizar estos términos de forma explícita:

1. **Integrado:** el cambio está en `main` y pasó la validación requerida de CI.
2. **Desplegado:** la versión está disponible en Render y `/healthz` responde `200 OK`.
3. **Liberado:** el comportamiento está habilitado para una audiencia mediante ConfigCat.

Que una funcionalidad esté integrada o desplegada **no significa** que esté liberada para todos los usuarios. En el Sprint Review siempre se debe informar el estado de las tres etapas.

---

## 👥 Sprint Review en Continuous Deployment

La Sprint Review demuestra valor observable en producción o valor activable de forma segura. No se limita a mostrar código terminado al final del sprint.

### Formato obligatorio por incremento

Cada incremento se presenta en un máximo de cinco minutos:

- Problema de usuario que resuelve y resultado esperado.
- Estado: integrado en `main`, desplegado en Render y estado del toggle.
- Audiencia actual: interna, porcentaje de usuarios o 100%.
- Demo en vivo del comportamiento `ON` y `OFF`, cuando aplique.
- Evidencia disponible: CI, `/healthz`, deploy, conversión, errores y feedback.
- Pregunta al PO o stakeholder: **“¿Esto genera el valor esperado?”**
- Decisión registrada: mantener `OFF`, iniciar canary, ampliar, pausar o hacer rollback.

La Review no debe presentar como “listo para usuarios” un incremento que solo está en `main` o desplegado con el toggle apagado.

---

## 🔁 Sprint Retrospective orientada al flujo

Cada Retrospective debe inspeccionar obligatoriamente:

### 1. Salud del pipeline

- Cantidad de ejecuciones de CI fallidas y causa principal.
- Tiempo promedio de CI y de despliegue.
- Health checks fallidos y duración de la degradación.
- Rollbacks realizados, tiempo de recuperación y si fueron repetibles.

### 2. Disciplina TBD

- Integraciones a `main` durante el sprint.
- Edad máxima de las ramas; objetivo: menos de 24 horas.
- Causas de ramas largas, incluyendo tests flaky o CI rojo.
- Uso correcto de toggles para evitar ramas de larga duración.

### 3. Flujo de valor

- Lead time desde el inicio del trabajo hasta producción.
- Tiempo desde el despliegue hasta la liberación.
- Evidencia de que el valor llegó a los usuarios.
- Feedback, conversión y errores relevantes para la funcionalidad.

La dinámica recomendada utiliza cuatro columnas:

- 🟢 Lo que funcionó bien en el flujo.
- 🟡 Lo que generó fricción.
- 🔴 Lo que rompió el flujo o generó miedo.
- 🚀 Acciones de mejora.

Se seleccionan como máximo tres acciones. Cada acción debe tener dueño, fecha límite, métrica de éxito y relación con una política o elemento del DoD.

---

## 🚀 Política de liberación segura

Toda funcionalidad protegida por toggle debe liberarse de forma progresiva, observable y reversible.

### Requisitos antes de activar una audiencia

- CI en verde y smoke test de la funcionalidad.
- `/healthz` en `200 OK` en Render.
- Toggle creado con valor predeterminado `OFF`.
- Audiencia o porcentaje claramente definido.
- Métrica de conversión o resultado de negocio.
- Métrica de errores técnicos y errores de negocio.
- Owner de observación y canal de escalamiento.
- Rollback probado o simulado y versión anterior disponible.
- Fecha de revisión y retiro del toggle.

### Secuencia estándar de rollout

| Fase | Audiencia | Observación mínima | Decisión |
|---|---|---|---|
| Preparación | 100% `OFF` | Instrumentación y baseline | No activar si faltan métricas |
| Interno | Equipo o usuarios de prueba | Smoke test `ON/OFF` y rollback | Avanzar o volver a `OFF` |
| Canary | 5% o cohorte controlada | 24 horas | Pausar ante degradación |
| Ampliación | 20% | 24-48 horas | Ampliar solo con evidencia |
| GA | 100% | Dos observaciones sanas consecutivas | Crear ticket de retiro |

### Significado de los porcentajes

El porcentaje indica la proporción aproximada de usuarios que puede utilizar la
funcionalidad; no es un porcentaje de descuento ni de dinero cobrado. La
asignación debe ser determinista usando el identificador del usuario, para que
un usuario conserve la misma cohorte mientras la configuración no cambie.

| Valor | Usuarios habilitados | Uso |
|---:|---|---|
| `0%` | Ninguno | Estado inicial, funcionalidad incompleta o rollback. |
| `5%` | Aproximadamente 5 de cada 100 | Canary para detectar errores con exposición reducida. |
| `20%` | Aproximadamente 20 de cada 100 | Ampliación controlada y validación con más tráfico. |
| `100%` | Todos | General Availability después de evidencia suficiente. |

En una muestra pequeña la cantidad observada puede no coincidir exactamente con
el porcentaje. El porcentaje representa una cohorte estadística, no un número
fijo de usuarios.

### Simulación local frente a producción

El dashboard de Pagos Express incluye controles locales para practicar `0%`,
`5%`, `20%` y `100%`. Estos controles solo pueden funcionar cuando:

```env
ENABLE_LOCAL_FLAG_CONTROLS=true
```

La variable debe permanecer ausente o en `false` en Render. La simulación no
modifica ConfigCat y no debe utilizarse para decidir un rollout productivo.

En producción, el porcentaje se configura exclusivamente en ConfigCat mediante
el setting `pagos-express-v1`. La `CONFIGCAT_SDK_KEY` solo autentica la
conexión con ConfigCat; no define por sí misma el porcentaje de usuarios.
Antes de avanzar, la respuesta del endpoint de flags debe indicar
`source: configcat`; si indica `fallback_local`, el rollout se detiene.

### Criterios de pausa o rollback

Se pausa el rollout o se vuelve al porcentaje anterior cuando ocurra cualquiera de estas condiciones:

- Health check fallido o degradación sostenida.
- Error crítico de pago, seguridad o integridad de datos.
- Error de pagos superior al baseline acordado.
- Conversión inferior al umbral acordado sin explicación.
- Métricas ausentes, incompletas o no confiables.
- Incidente operativo sin owner disponible.

Para `pagos-express-v1`, no se activa el 20% únicamente por presión comercial. Primero deben existir métricas de conversión y error de pago, un rollback verificable y un responsable de observación.

---

## 💳 Caso operativo: `pagos-express-v1`

La funcionalidad “Pagos Express con un solo clic” sigue esta política:

- Estado inicial: `OFF` para el 100% de usuarios.
- Primer paso: habilitación interna después de validar CI, Render, smoke test y rollback.
- Segundo paso: canary controlado, preferiblemente 5%.
- Tercer paso: ampliación al 20% solo con métricas comparables contra baseline.
- Estado final: 100% únicamente después de dos observaciones sanas consecutivas.
- Retiro: eliminar el toggle y su lógica condicional mediante un cambio posterior, con ticket y fecha definidos.

La existencia de una campaña de marketing o un anuncio interno no sustituye la validación técnica ni la evidencia de valor.

### Comportamiento esperado por fase

- En `0%`, el checkout responde `feature_disabled` y HTTP `403` para todos.
- En `5%`, solo los usuarios de la cohorte canary pueden ejecutar el checkout.
- En `20%`, solo la cohorte ampliada puede ejecutar el checkout; se compara
  contra el baseline de usuarios no habilitados.
- En `100%`, todos los usuarios pueden ejecutar el flujo, pero el toggle
  todavía debe conservar un plan de rollback hasta completar la estabilización.

El checkout implementado en el repositorio es una simulación y no realiza
cargos reales. Las métricas actuales sirven para el taller y se almacenan en
memoria; antes de operar pagos reales se requiere observabilidad persistente.

---

## 🧹 Gestión de deuda de Feature Toggles

- Todo toggle nuevo debe registrar owner, propósito, fecha de creación y fecha de retiro esperada.
- Un toggle con más de 30 días requiere revisión explícita en la Retrospective.
- Un toggle con más de 45 días requiere una acción prioritaria de limpieza o una justificación aprobada.
- Los tres toggles antiguos del caso de Pagos Express deben auditarse, asignarse y retirarse o renovarse con fecha.
- No se deben crear toggles permanentes para ocultar trabajo incompleto sin una decisión operativa documentada.

---

## ✅ Checklist operativo de liberación

- [ ] El incremento está integrado en `main`.
- [ ] CI está en verde y no existe un test flaky bloqueante sin plan.
- [ ] Render está saludable y `/healthz` responde `200 OK`.
- [ ] El toggle inicia en `OFF`.
- [ ] La audiencia y el porcentaje están definidos.
- [ ] Conversión y errores de negocio son observables.
- [ ] El rollback fue probado o simulado.
- [ ] Owner y ventana de observación están registrados.
- [ ] Los criterios de avance y rollback están acordados.
- [ ] El toggle tiene fecha de retiro y ticket asociado.
