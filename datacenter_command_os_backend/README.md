# DataCenter Command OS — API y base de datos inicial

Esta carpeta es el primer backend de desarrollo para convertir la demo HTML en una plataforma con datos centralizados.

## Incluye

- PostgreSQL como base de datos central.
- API REST con FastAPI.
- Entidades: salas, racks, equipos, interfaces, servicios, recursos eléctricos, reservas y eventos.
- Validación básica de altura de rack y solapamiento de equipos en unidades U.
- Documentación interactiva de la API.
- La demo HTML existente en `frontend/`.

## Requisitos

Instala Docker Desktop y Docker Compose. No se necesita instalar Python o PostgreSQL por separado para ejecutar la configuración Docker.

## Inicio local

1. Descomprime el proyecto.
2. Abre una terminal en la carpeta raíz.
3. Copia `.env.example` a `.env` y cambia la contraseña.
4. Ejecuta:

   ```bash
   docker compose up --build
   ```

5. Comprueba la API en `http://localhost:8000/health`.
6. Abre la documentación interactiva en `http://localhost:8000/docs`.

La API queda disponible en `http://localhost:8000/api`.

## Ejemplo de crear un rack

En `/docs`, selecciona `POST /api/racks` y envía:

```json
{
  "data": {
    "name": "RACK-A01",
    "height_u": 42,
    "max_power_w": 5000,
    "notes": "Fila A"
  }
}
```

Luego registra un equipo con `POST /api/equipment`:

```json
{
  "data": {
    "name": "SRV-01",
    "kind": "server",
    "rack_id": 1,
    "start_u": 10,
    "height_u": 2,
    "power_w": 450,
    "status": "planned"
  }
}
```

El identificador `rack_id` debe corresponder a un rack existente. El backend rechaza equipos fuera del alto del rack y solapamientos de U.

## Recursos disponibles

- `/api/rooms`
- `/api/racks`
- `/api/equipment`
- `/api/interfaces`
- `/api/services`
- `/api/power-resources`
- `/api/reservations`
- `/api/events`

Todos admiten `GET` para listar, `GET /{id}` para consultar, `POST` para crear, `PATCH /{id}` para modificar y `DELETE /{id}` para borrar. Los campos se envían dentro de `{"data": {...}}`.

## Importante: límites de esta entrega

- **Es un esqueleto de desarrollo**, no una plataforma lista para producción.
- La demo HTML aún no está conectada a esta API; esta entrega crea la base técnica separada para la integración siguiente.
- No incluye autenticación, roles, auditoría robusta, migraciones Alembic ni copias de seguridad programadas. No la publiques en Internet ni la uses para datos críticos sin añadir esos controles.
- Los estados eléctricos son datos declarados; no representan mediciones reales.
- No se conecta ni controla hardware. La integración SNMP/API/Modbus debe diseñarse según los equipos reales.
- Para producción: añadir autenticación (por ejemplo OIDC), permisos por rol, HTTPS, secretos seguros, copias verificadas, logs de auditoría, migraciones, pruebas y revisión de seguridad.
- La comprobación de solapamiento de rack es una validación inicial; en producción debe hacerse transaccionalmente para evitar conflictos simultáneos entre usuarios.

## Próximas etapas

1. Conectar los formularios y tablas del frontend a esta API.
2. Incorporar autenticación, usuarios, permisos e historial de cambios.
3. Implementar diagrama de conexiones y validación de reservas por intervalo de fechas.
4. Agregar telemetría real y alarmas mediante integraciones compatibles con los fabricantes.
5. Incorporar propuestas de IA con revisión y aprobación explícitas.
