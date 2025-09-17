# Operación y mantenimiento

## Comandos habituales

```bash
# Ejecutar pruebas unitarias
uv run pytest

# Ejecutar análisis estático (Pyright) y formateo (Ruff)
uv run pyright
uv run ruff check .
uv run ruff format .

# Generar nueva migración (revisa que la BD esté configurada)
uv run alembic revision --autogenerate -m "descripcion"
```

## Migraciones y persistencia

- `DatabaseConfig` centraliza la configuración de PostgreSQL; Alembic utiliza la misma clase en `app/migrations/env.py`, por lo que
  es imprescindible exportar las variables de entorno antes de correr migraciones.
- La tabla `consulta` guarda el historial de peticiones, permitiendo auditoría y métricas de uso.
- Si necesitas tablas adicionales, define los modelos en `app/models/` y ejecútalas mediante Alembic.

## Logging y observabilidad

- El servicio utiliza `logging` de la librería estándar con nivel `INFO`. Amplía la configuración según tu plataforma (Stackdriver,
  ELK, etc.).
- `api_exception` registra las excepciones y responde con un payload homogéneo; revisa `error_code` y `description` para depurar
  fallos provenientes del SIS.
- El endpoint `/health` consulta la base de datos. Úsalo en probes de Kubernetes o chequeos automáticos.

## Seguridad y configuración

- Restringe CORS (`allow_origins`) antes de pasar a producción.
- Protege las variables `SOAP_USER`/`SOAP_PASSWORD` mediante un gestor de secretos.
- Considera cachear el token de sesión si el patrón de uso lo permite; el servicio ya lo mantiene en memoria mientras el proceso
  esté activo.

## Documentación

- La documentación de MkDocs vive en la carpeta `docs/`.
- Para previsualizarla localmente ejecuta:

```bash
uv run mkdocs serve -a 0.0.0.0:8001
```

- Publica el sitio con `uv run mkdocs build` y despliega el contenido de `site/` en tu servicio estático favorito.
