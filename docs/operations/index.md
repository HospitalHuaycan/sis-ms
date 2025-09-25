# Operación y mantenimiento

Esta sección reúne lineamientos para operar SIS-MS en entornos de prueba y
producción. Incluye comandos cotidianos, recomendaciones de monitoreo y tareas
periódicas relacionadas con la base de datos y las credenciales del servicio
SOAP.

## Comandos habituales

```bash
# Ejecutar pruebas y análisis antes de liberar cambios
uv run pytest
uv run ruff check .
uv run pyright

# Formatear el código fuente
uv run ruff format .

# Generar una nueva migración (requiere base de datos configurada)
uv run alembic revision --autogenerate -m "descripcion"
```

> Ejecuta `uv run alembic upgrade head` en cada despliegue para asegurar que el
> esquema coincida con la versión del código.

## Monitoreo y *health checks*

- `GET /health` invoca `DatabaseConfig.test_connection()` y confirma la conexión
  con PostgreSQL. Úsalo como *readiness probe* o chequeo automatizado.
- `Logger` emite trazas coloreadas en consola por defecto. Para integraciones con
  Google Cloud Logging utiliza `LogType.GOOGLE_CLOUD` al construir la instancia.
- `api_exception` registra cualquier error controlado; revisa los campos
  `error_code` y `description` en la respuesta cuando se produzca un fallo.

Considera añadir métricas externas (Prometheus, Stackdriver, etc.) para medir el
número de consultas exitosas/fallidas y los tiempos de respuesta.

## Gestión de credenciales y secretos

- `SOAP_USER` y `SOAP_PASSWORD` son credenciales sensibles. Almacénalas en un
  gestor de secretos y rota los valores siguiendo las políticas de tu
  organización.
- Si las credenciales cambian, actualiza el servicio sin reiniciar clientes: el
  token de sesión se solicita en cada invocación de `/consultar_afiliado`.
- Configura certificados TLS en el *reverse proxy* que expone FastAPI.

## Base de datos y caché

- `AfiliadoService` marca cada consulta con `es_local` cuando responde desde la
  caché del día (consulta previa registrada en `consulta`).
- Para revisar el historial ejecuta consultas sobre la tabla `consulta`. Por
  ejemplo, para detectar errores recientes:

  ```sql
  SELECT created_at, numero_documento, error_code, error_description
  FROM consulta
  WHERE created_at > NOW() - INTERVAL '1 day'
  ORDER BY created_at DESC;
  ```

- Si necesitas eliminar datos antiguos, crea migraciones o scripts específicos;
  evita truncar tablas manualmente para mantener auditoría.

## Migraciones y despliegues

1. Ejecuta las pruebas automatizadas y el análisis estático.
2. Genera la migración con Alembic (si aplica) y revísala antes de aplicarla.
3. Despliega el código y aplica `alembic upgrade head` en la misma transacción
   de despliegue.
4. Monitorea los logs en busca de fallos del SIS o errores de conexión a la base
   de datos.

## Documentación y soporte

- La documentación vive en `docs/` y se publica con `uv run mkdocs build`.
- Agrega notas operativas (p.ej. incidencias, cambios de contrato) en este mismo
  apartado para mantener un histórico accesible a todo el equipo.
- Si el servicio SOAP presenta inestabilidad, habilita el nivel `DEBUG` en el
  logger para capturar los mensajes completos devueltos por `zeep`.
