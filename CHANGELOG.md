## 0.2.0 (2025-09-26)

### Feat

- :boom: Commitizen workflow
- :rocket: enhance docker compose for production
- :boom: Uso de AfiliadoService en ves de SISService
- :boom: Afiliado Service
- :boom: Añadimos repositorio para manejar interaccion con BD
- :boom: Modelo Consulta para almacenar historial
- :sparkles: ConsultaAfiliadoFuaE servicio implementado
- :sparkles: login endpoint
- :sparkles: Custom exceptions
- :sparkles: Sis service and Requests
- :sparkles: add database configuration
- :sparkles: Add models
- :boom: Configurar entorno de desarrollo
- :tada: SIS microservice

### Fix

- :green_heart: Remove body.md
- :rocket: Timezone docker build
- **configuration**: :green_heart: fix compose.yml path
- expose 8000
- :adhesive_bandage: Usamos error_code
- :ambulance: Respuesta de IdError SOAP es un str
- :wrench: Configuracion de base de datos.
- :adhesive_bandage: Valores por defecto para consulta
- :sparkles: Añadimos campo usuario en el request
- :ambulance: Retornamos afiliado
- :bug: Correcoin de comparacion del IdError
- :ambulance: Cambiamos modelo Afiliado a SQLModel
- :truck: Eliminamos modelo consulta
- :ambulance: Todos los campos a str.
- :ambulance: Guardamos el mensaje de error por si falla.
- :card_file_box: Migracion de tabla
- :ambulance: Return http_status_code
- :adhesive_bandage: mount ssh from wsl to devcontainer
- :adhesive_bandage: rename service app

### Refactor

- :card_file_box: Campo IdError es str
- :technologist: eliminamos healthcheck
- :wrench: Refactorizamos database.py
- :card_file_box: Cambio de estructura de afiliado
- :recycle: Refactor SIS Service.
- **configuration**: :wrench: exclude Exception error
- **configuration**: :wrench: Exclude print error
- :wrench: Configure alembic
