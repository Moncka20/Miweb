# 📘 Playbook de Trunk-Based Development (TBD) y Definition of Done (DoD)

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

---

## 📋 Definition of Done (DoD) Definitivo

Una historia de usuario o cambio técnico se considera **DONE** solo cuando cumple la totalidad de los siguientes criterios:

### 1. ⚙️ Calidad Técnica y Código
- [ ] El código sigue las pautas de estilo y pasa el linter estático (`ruff check .` sin advertencias).
- [ ] Todos los tests unitarios y de integración pasan en verde (`pytest`).
- [ ] No se agregan dependencias sin justificación en `requirements.txt`.
- [ ] No existen ramas de larga duración (vida máxima de rama: < 24 horas).

### 2. 🚩 Desacople con Feature Toggles (ConfigCat)
- [ ] Si la funcionalidad está en desarrollo o incompleta, **debe estar protegida detrás de un Feature Toggle** (`dark_mode_enabled`, `nueva-funcionalidad-x`).
- [ ] El comportamiento predeterminado del flag en producción debe ser `OFF` hasta su validación.
- [ ] Se incluye plan de retiro técnico del toggle una vez alcanzado el 100% GA.

### 3. 🚀 Despliegue y Operación (Render)
- [ ] El commit está integrado en `main` mediante Pull Request validado por CI.
- [ ] La imagen Docker se compila y publica en GHCR.
- [ ] El servicio se auto-despliega en Render y el endpoint `/healthz` responde `200 OK`.
- [ ] La versión anterior cuenta con capacidad de Rollback inmediato.

---

## 🚦 Regla de Oro del Equipo

> **"Si el CI está en rojo, se detiene la adición de nuevas features hasta que vuelva a estar en verde."**
