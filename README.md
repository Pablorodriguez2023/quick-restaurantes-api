# API de Gestión de Restaurantes
 
Sistema de gestión de restaurantes desarrollado con Django REST Framework que permite administrar restaurantes, menús, pedidos y usuarios. Utiliza PostgreSQL, Redis y Celery para funcionalidades avanzadas como manejo de tareas asíncronas y generación de reportes.
 
---
 
## 📋 Tabla de Contenidos
1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalación Rápida](#instalación-rápida)
4. [Configuración](#configuración)
5. [Uso](#uso)
6. [API Endpoints](#api-endpoints)
7. [Autenticación](#autenticación)
8. [Pruebas](#pruebas)
9. [Solución de Problemas](#solución-de-problemas)
10. [Monitoreo de Tareas Celery](#monitoreo-de-tareas-celery)
 
---
 
## ✨ Características
 
- Gestión completa de restaurantes (CRUD)
- Sistema de menús y pedidos
- Autenticación mediante JWT
- Generación de reportes en segundo plano
- Documentación automática con Swagger/OpenAPI
 
---
 
## 📋 Requisitos
 
- **Requisitos del Sistema**:
  - Docker (versión 20.10+)
  - Docker Compose (versión 1.29+)
  - Git
  - Conexión a Internet
 
---
 
## 🚀 Instalación Rápida
 
### 1. Clonar el Repositorio
```bash
git clone https://github.com/Pablorodriguez2023/restaurant-api.git pablo-rodriguez-restaurantes-api && cd pablo-rodriguez-restaurantes-api
```
 
### 2. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
```env
# Configuración de Django
SECRET_KEY=django-insecure-your_very_secret_key_here
DEBUG=1
 
# Configuración de Base de Datos
DB_NAME=restaurantes
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=restaurantes-db
DB_PORT=5432
 
# Configuración de Celery y Redis
CELERY_BROKER_URL=redis://restaurantes-redis:6379/0
CELERY_RESULT_BACKEND=redis://restaurantes-redis:6379/0
 
# Configuraciones de seguridad
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
 
# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
```
 
### 3. Construir y Levantar Contenedores
```bash
# Construir contenedores
docker-compose up --build
 
```
 
### 4. Configurar Base de Datos y Usuario Administrador

#### Paso 1: Preparar la Base de Datos
```bash
# Generar migraciones
docker exec restaurantes-app python manage.py makemigrations

# Aplicar migraciones
docker exec restaurantes-app python manage.py migrate
```

#### Paso 2: Verificar Configuración JWT
```bash
# Verificar que JWT_SECRET_KEY está configurado en .env
echo "JWT_SECRET_KEY=your_jwt_secret_key_here" >> .env

# Reiniciar el servicio para aplicar los cambios
docker restart restaurantes-app
```

#### Paso 3: Crear Superusuario

> **⚠️ Importante**: Hay dos formas de crear el superusuario:

##### Opción 1: Usando el comando interactivo (recomendado)
```bash
# Crear superusuario de forma interactiva
docker exec -it restaurantes-app python manage.py createsuperuser
```

##### Opción 2: Usando variables de entorno (si hay problemas con TTY)
```bash
# Crear superusuario con variables de entorno
docker exec restaurantes-app python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
"
```

#### Paso 4: Verificar la Instalación

```bash
# 1. Verificar que el usuario existe
docker exec restaurantes-app python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
print('Usuarios en la base de datos:', User.objects.all())
"

# 2. Probar la obtención del token
curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "adminpass123"}'
```

> **📝 Notas importantes**: 
> 1. Si usas la Opción 2, las credenciales serán:
>    - Username: admin
>    - Email: admin@example.com
>    - Password: adminpass123
> 2. Por seguridad, cambia estas credenciales en un entorno de producción.
> 3. La contraseña debe tener al menos 8 caracteres y no puede ser demasiado común.
> 4. Después de crear el superusuario, espera unos segundos a que el servicio se reinicie completamente.
> 5. Si tienes problemas con la autenticación, verifica que JWT_SECRET_KEY está correctamente configurado en tu archivo .env.

---
 
## 📡 API Endpoints

### 🔐 Autenticación y Tokens

**POST /api/token/**
- Obtiene un par de tokens de acceso y refresco
- Requiere: username y password en el body
- Retorna: access_token y refresh_token
- URL: `http://localhost:8000/api/token/`
- Body ejemplo:
  ```json
  {
    "username": "admin",
    "password": "tu_contraseña"
  }
  ```
- Respuesta ejemplo:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
  }
  ```

> **📝 Nota**: Guarda el token de acceso (`access`) para usarlo en las siguientes peticiones en el header `Authorization: Bearer <token>`

### 📚 Documentación API

**GET /swagger/**
- Interfaz interactiva de Swagger para probar la API
- No requiere autenticación
- Permite probar todos los endpoints desde el navegador
- URL: `http://localhost:8000/swagger/`

**GET /redoc/**
- Documentación alternativa con ReDoc
- No requiere autenticación
- Formato más amigable para lectura
- URL: `http://localhost:8000/redoc/`

**GET /swagger.json**
- Especificación OpenAPI en formato JSON
- Útil para generar clientes API
- URL: `http://localhost:8000/swagger.json`

### 👥 Gestión de Usuarios

**GET /api/users/users/**
- Lista todos los usuarios registrados
- Requiere: token JWT
- Retorna: lista de usuarios con sus detalles
- URL: `http://localhost:8000/api/users/users`

**POST /api/users/**
- Crea un nuevo usuario
- Requiere: datos del usuario en el body
- Retorna: datos del usuario creado
- URL: `http://localhost:8000/api/users/`
- Body ejemplo:
  ```json
  {
    "email": "usuario@email.com",
    "password": "contraseña123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "phone": "1234567890",
    "default_address": "Dirección 123"
  }
  ```

**GET /api/users/{id}/**
- Obtiene detalles de un usuario específico
- Requiere: token JWT
- Retorna: información detallada del usuario
- URL ejemplo: `http://localhost:8000/api/users/1/`

**PUT /api/users/{id}/**
- Actualiza datos de un usuario existente
- Requiere: token JWT y datos a actualizar
- Retorna: datos actualizados del usuario
- URL ejemplo: `http://localhost:8000/api/users/1/`
- Body ejemplo:
  ```json
  {
    "first_name": "Nuevo Nombre",
    "phone": "0987654321"
  }
  ```

**DELETE /api/users/{id}/**
- Elimina un usuario del sistema
- Requiere: token JWT
- Retorna: confirmación de eliminación
- URL ejemplo: `http://localhost:8000/api/users/1/`

**POST /api/users/register/**
- Registro específico para nuevos usuarios
- No requiere autenticación
- Retorna: datos del usuario registrado y token
- URL: `http://localhost:8000/api/users/register/`
- Body ejemplo:
  ```json
  {
    "email": "nuevo@email.com",
    "password": "contraseña123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "phone": "1234567890",
    "default_address": "Dirección 123"
  }
  ```

### 🏪 Gestión de Restaurantes

**GET /api/restaurants/restaurants/**
- Lista todos los restaurantes
- Requiere: token JWT
- Retorna: lista de restaurantes con sus detalles
- URL: `http://localhost:8000/api/restaurants/restaurants/`

**POST /api/restaurants/restaurants/**
- Registra un nuevo restaurante
- Requiere: token JWT y datos del restaurante
- Retorna: datos del restaurante creado
- URL: `http://localhost:8000/api/restaurants/restaurants/`
- Body ejemplo:
  ```json
  {
    "name": "Restaurante Ejemplo",
    "address": "Dirección del Restaurante",
    "phone": "1234567890",
    "email": "restaurante@email.com",
    "description": "Descripción del restaurante",
    "category": "ITALIAN"  // Campo requerido: ITALIAN, MEXICAN, CHINESE, FAST_FOOD, etc.
  }
  ```

**GET /api/restaurants/restaurants/{id}/**
- Obtiene detalles de un restaurante específico
- Requiere: token JWT
- Retorna: información detallada del restaurante
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/1/`

**PUT /api/restaurants/restaurants/{id}/**
- Actualiza información de un restaurante
- Requiere: token JWT y datos a actualizar
- Retorna: datos actualizados del restaurante
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/1/`
- Body ejemplo:
  ```json
  {
    "name": "Nuevo Nombre",
    "phone": "0987654321"
  }
  ```

**DELETE /api/restaurants/restaurants/{id}/**
- Elimina un restaurante del sistema
- Requiere: token JWT
- Retorna: confirmación de eliminación
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/1/`

**POST /api/restaurants/restaurants/bulk_upload/**
- Carga masiva de restaurantes mediante archivo CSV
- Formato de archivo: CSV (.csv)
- Requiere: token JWT y archivo CSV
- Retorna: ID de la tarea asíncrona
- URL: `http://localhost:8000/api/restaurants/restaurants/bulk_upload/`
- Body ejemplo (form-data):
  ```
  file: [archivo.csv]
  ```
- Estructura del CSV requerida:
  ```
  name,address,phone,email,category
  Restaurante A,Calle 123,1234567890,rest@email.com,ITALIAN
  ```

**GET /api/restaurants/restaurants/check_task_status/{task_id}/**
- Verifica estado de una tarea de carga masiva
- Requiere: token JWT
- Retorna: estado actual de la tarea
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/check_task_status/abc123/`

### 📊 Gestión de Archivos CSV y Reportes

> **Nota**: Todos estos endpoints están diseñados específicamente para trabajar con archivos en formato CSV (.csv). No se admiten otros formatos de archivo.

#### Estructura de Archivos CSV

##### Archivo CSV de Restaurantes
- **Campos Requeridos**:
  - `name`: Nombre del restaurante (texto)
  - `address`: Dirección completa (texto)
  - `category`: Categoría (ITALIAN, MEXICAN, CHINESE, FAST_FOOD, etc.)
- **Campos Opcionales**:
  - `phone`: Número telefónico (texto)
  - `email`: Correo electrónico (texto)
  - `rating`: Calificación (decimal, 0.00-5.00)
  - `status`: Estado (OPEN, CLOSED, TEMPORARILY_CLOSED)
  - `latitude`: Latitud (decimal)
  - `longitude`: Longitud (decimal)
- **Ejemplo**:
  ```csv
  name,address,category,phone,email,rating,status
  Restaurante A,Calle 123,ITALIAN,1234567890,rest@email.com,4.5,OPEN
  Restaurante B,Av Principal,MEXICAN,0987654321,restb@email.com,4.8,OPEN
  ```

##### Archivo CSV de Menú
- **Campos Requeridos**:
  - `name`: Nombre del ítem (texto)
  - `price`: Precio (decimal)
  - `restaurant_id`: ID del restaurante (número entero)
  - `category`: Categoría (APPETIZER, MAIN_COURSE, DESSERT, DRINK)
- **Campos Opcionales**:
  - `description`: Descripción del ítem (texto)
  - `available`: Disponibilidad (true/false)
  - `preparation_time`: Tiempo de preparación en minutos (número)
  - `calories`: Calorías (número)
- **Ejemplo**:
  ```csv
  name,price,restaurant_id,category,description,available,preparation_time
  Pizza,Pizza italiana,15.99,1,MAIN_COURSE,Pizza italiana tradicional,true,20
  Pasta Alfredo,12.99,1,MAIN_COURSE,Pasta con salsa cremosa,true,15
  ```

##### Archivo CSV de Usuarios
- **Campos Requeridos**:
  - `email`: Correo electrónico (texto)
  - `password`: Contraseña (texto)
  - `first_name`: Nombre (texto)
  - `last_name`: Apellido (texto)
- **Campos Opcionales**:
  - `phone`: Número telefónico (texto)
  - `default_address`: Dirección predeterminada (texto)
  - `typology`: Tipo de usuario (ADMIN, CUSTOMER, RESTAURANT_OWNER)
- **Ejemplo**:
  ```csv
  email,password,first_name,last_name,phone,default_address,typology
  user@email.com,pass123,John,Doe,1234567890,Calle 123,CUSTOMER
  admin@email.com,admin123,Admin,User,0987654321,Av Principal,ADMIN
  ```

#### Validaciones y Restricciones
- Los archivos CSV deben usar coma (,) como separador
- La primera fila debe contener los nombres de las columnas
- Los campos requeridos no pueden estar vacíos
- Los valores numéricos deben usar punto (.) como separador decimal
- Las fechas deben estar en formato YYYY-MM-DD
- Los campos booleanos deben ser true/false
- Los IDs deben ser números enteros positivos
- Los correos electrónicos deben tener un formato válido
- Las contraseñas deben tener al menos 8 caracteres

#### Manejo de Errores
- Si el archivo no es CSV, se retornará un error 400
- Si faltan campos requeridos, se retornará un error detallando los campos faltantes
- Si hay errores de formato, se proporcionará un informe de errores
- Los registros con errores serán omitidos, pero los válidos se procesarán

#### Carga Masiva de Datos (Solo archivos CSV)

**POST /api/menu/menu-items/bulk_upload/**
- Carga masiva de items de menú mediante archivo CSV
- Formato de archivo: CSV (.csv)
- Requiere: token JWT y archivo CSV
- Retorna: ID de la tarea asíncrona
- URL: `http://localhost:8000/api/menu/menu-items/bulk_upload/`
- Body ejemplo (form-data):
  ```
  file: [archivo.csv]
  ```
- Estructura del CSV requerida:
  ```
  name,description,price,restaurant_id,category,available
  Pizza,Pizza italiana,15.99,1,MAIN_COURSE,true
  ```

**POST /api/users/users/bulk_upload/**
- Carga masiva de usuarios mediante archivo CSV
- Formato de archivo: CSV (.csv)
- Requiere: token JWT y archivo CSV
- Retorna: ID de la tarea asíncrona
- URL: `http://localhost:8000/api/users/users/bulk_upload/`
- Body ejemplo (form-data):
  ```
  file: [archivo.csv]
  ```
- Estructura del CSV requerida:
  ```
  email,password,first_name,last_name,phone,default_address
  user@email.com,pass123,John,Doe,1234567890,Calle 123
  ```

#### Descarga de Reportes y Plantillas (Formato CSV)

**GET /api/restaurants/restaurants/download_template/**
- Descarga plantilla CSV para carga masiva de restaurantes
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: archivo CSV con estructura requerida
- URL: `http://localhost:8000/api/restaurants/restaurants/download_template/`

**GET /api/menu/menu-items/download_template/**
- Descarga plantilla CSV para carga masiva de items de menú
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: archivo CSV con estructura requerida
- URL: `http://localhost:8000/api/menu/menu-items/download_template/`

**GET /api/users/users/download_template/**
- Descarga plantilla CSV para carga masiva de usuarios
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: archivo CSV con estructura requerida
- URL: `http://localhost:8000/api/users/users/download_template/`

**GET /api/restaurants/restaurants/generate_report/**
- Genera reporte de restaurantes en formato CSV
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: ID de la tarea asíncrona
- URL: `http://localhost:8000/api/restaurants/restaurants/generate_report/`
- Parámetros opcionales:
  - `start_date`: Fecha inicial (YYYY-MM-DD)
  - `end_date`: Fecha final (YYYY-MM-DD)
  - `status`: Estado del restaurante

**GET /api/restaurants/restaurants/download_report/{task_id}/**
- Descarga el reporte generado en formato CSV
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: archivo CSV con el reporte
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/download_report/abc123/`

**GET /api/restaurants/restaurants/generate_sales_report/**
- Genera reporte de ventas en formato CSV
- Formato de descarga: CSV (.csv)
- Requiere: token JWT
- Retorna: ID de la tarea asíncrona
- URL: `http://localhost:8000/api/restaurants/restaurants/generate_sales_report/`
- Parámetros opcionales:
  - `start_date`: Fecha inicial (YYYY-MM-DD)
  - `end_date`: Fecha final (YYYY-MM-DD)
  - `restaurant_id`: ID del restaurante

#### Verificación de Estado de Tareas

**GET /api/restaurants/restaurants/check_task_status/{task_id}/**
- Verifica el estado de una tarea de generación de reporte o carga masiva
- Requiere: token JWT
- Retorna: estado actual de la tarea
- URL ejemplo: `http://localhost:8000/api/restaurants/restaurants/check_task_status/abc123/`
- Estados posibles:
  - `PENDING`: Tarea en espera
  - `STARTED`: Tarea iniciada
  - `SUCCESS`: Tarea completada exitosamente
  - `FAILURE`: Tarea fallida

### 🍽️ Gestión del Menú

**GET /api/menu/menu-items/**
- Lista todos los items del menú
- Requiere: token JWT
- Retorna: lista de items con sus detalles
- Soporta filtros:
  - `available`: Filtrar por disponibilidad (true/false)
  - `restaurant`: Filtrar por ID de restaurante
  - `category`: Filtrar por categoría
  - `price_min`: Precio mínimo
  - `price_max`: Precio máximo
- URL: `http://localhost:8000/api/menu/menu-items/`
- Ejemplo con filtros: `http://localhost:8000/api/menu/menu-items/?available=true&restaurant=1`

**POST /api/menu/menu-items/**
- Crea un nuevo item en el menú
- Requiere: token JWT y datos del item
- Retorna: datos del item creado
- URL: `http://localhost:8000/api/menu/menu-items/`
- Body ejemplo:
  ```json
  {
    "name": "Plato Ejemplo",
    "description": "Descripción del plato",
    "price": 15.99,
    "restaurant": 1,
    "category": "MAIN_COURSE",
    "available": true,           // Campo requerido: true/false
    "preparation_time": 20       // Campo requerido: tiempo en minutos
  }
  ```

**GET /api/menu/menu-items/{id}/**
- Obtiene detalles de un item específico
- Requiere: token JWT
- Retorna: información detallada del item
- URL ejemplo: `http://localhost:8000/api/menu/menu-items/1/`

**PUT /api/menu/menu-items/{id}/**
- Actualiza información de un item
- Requiere: token JWT y datos a actualizar
- Retorna: datos actualizados del item
- URL ejemplo: `http://localhost:8000/api/menu/menu-items/1/`
- Body ejemplo:
  ```json
  {
    "price": 18.99,
    "description": "Nueva descripción"
  }
  ```

**DELETE /api/menu/menu-items/{id}/**
- Elimina un item del menú
- Requiere: token JWT
- Retorna: confirmación de eliminación
- URL ejemplo: `http://localhost:8000/api/menu/menu-items/1/`

### 📝 Gestión de Órdenes

**GET /api/orders/orders/**
- Lista todas las órdenes
- Requiere: token JWT
- Retorna: lista de órdenes con sus detalles
- URL: `http://localhost:8000/api/orders/orders/`

**POST /api/orders/orders/**
- Crea una nueva orden
- Requiere: token JWT y datos de la orden
- Retorna: datos de la orden creada
- URL: `http://localhost:8000/api/orders/orders/`
- Body ejemplo:
  ```json
  {
    "restaurant": 1,
    "delivery_address": "Dirección de entrega",
    "items": [
      {
        "menu_item": 1,
        "quantity": 2
      }
    ],
    "special_instructions": "Sin instrucciones especiales",     // Campo requerido
    "estimated_delivery_time": "2024-12-16T22:00:00Z"          // Campo requerido: fecha y hora en formato ISO
  }
  ```

**GET /api/orders/orders/{id}/**
- Obtiene detalles de una orden específica
- Requiere: token JWT
- Retorna: información detallada de la orden
- URL ejemplo: `http://localhost:8000/api/orders/orders/1/`

**PUT /api/orders/orders/{id}/**
- Actualiza estado o información de una orden
- Requiere: token JWT y datos a actualizar
- Retorna: datos actualizados de la orden
- URL ejemplo: `http://localhost:8000/api/orders/orders/1/`
- Body ejemplo:
  ```json
  {
    "status": "DELIVERED"
  }
  ```

**DELETE /api/orders/orders/{id}/**
- Elimina una orden del sistema
- Requiere: token JWT
- Retorna: confirmación de eliminación
- URL ejemplo: `http://localhost:8000/api/orders/orders/1/`

### 📦 Gestión de Ítems de Orden

**POST /api/orders/order-items/**
- Agrega un nuevo ítem a una orden.
- **Body**:
  ```json
  {
    "menu_item_id": 1,
    "quantity": 2
  }
  ```

**GET /api/orders/order-items/**
- Lista todos los ítems de las órdenes.
- **Requiere**: token JWT.

**GET /api/orders/order-items/{id}/**
- Obtiene los detalles de un ítem específico de la orden.
- **Requiere**: token JWT.

**PUT /api/orders/order-items/{id}/**
- Actualiza un ítem existente en la orden.
- **Body**:
  ```json
  {
    "quantity": 3
  }
  ```

**DELETE /api/orders/order-items/{id}/**
- Elimina un ítem de la orden.
- **Requiere**: token JWT.

### 🔒 Seguridad de la API

- Todos los endpoints (excepto registro y autenticación) requieren un token JWT válido en el header:
  ```
  Authorization: Bearer <token>
  ```
- Los datos sensibles (teléfono, dirección) se almacenan hasheados en la base de datos
- Las contraseñas se hashean usando bcrypt antes de almacenarse
- Los datos sensibles se enmascaran al mostrarse (ej: ****1234)

---
 
## 🧪 Pruebas
 
### Ejecutar Pruebas Unitarias
```bash
# Ejecutar todas las pruebas
docker exec restaurantes-app python manage.py test
 
# Ejecutar pruebas de una app específica
docker exec restaurantes-app python manage.py test users
docker exec restaurantes-app python manage.py test restaurants
docker exec restaurantes-app python manage.py test menu
docker exec restaurantes-app python manage.py test orders
```
 
---
 
## 🌐 Acceso a la API
 
- **Servidor**: [http://localhost:8000](http://localhost:8000)
- **Swagger/OpenAPI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Documentación de la API**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
 
---
 
 
---
 
## 🔧 Solución de Problemas

### Problemas con la Autenticación

1. **Error: "No active account found with the given credentials"**
   ```bash
   # 1. Verifica que el usuario existe
   docker exec restaurantes-app python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.all())"
   
   # 2. Recrea el usuario si es necesario
   docker exec restaurantes-app python manage.py shell -c "
   from django.contrib.auth import get_user_model;
   User = get_user_model();
   User.objects.all().delete();
   User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
   "
   
   # 3. Reinicia los servicios
   docker restart restaurantes-app restaurantes-celery
   ```

2. **Error: "Token is invalid or expired"**
   - Los tokens JWT expiran después de un tiempo
   - Obtén un nuevo token usando el endpoint `/api/token/`
   - O usa el endpoint `/api/token/refresh/` con tu refresh token

### Problemas con la Base de Datos

1. **Error: "relation does not exist"**
   ```bash
   # Recrea las migraciones
   docker exec restaurantes-app python manage.py makemigrations
   docker exec restaurantes-app python manage.py migrate
   ```

2. **Error de conexión a PostgreSQL**
   ```bash
   # Verifica que PostgreSQL está corriendo
   docker ps | grep restaurantes-db
   
   # Reinicia PostgreSQL si es necesario
   docker restart restaurantes-db
   ```

### Problemas con Redis/Celery

1. **Las tareas asíncronas no funcionan**
   ```bash
   # Verifica que Celery está corriendo
   docker logs restaurantes-celery
   
   # Reinicia Celery si es necesario
   docker restart restaurantes-celery
   ```

2. **Error de conexión a Redis**
   ```bash
   # Verifica que Redis está corriendo
   docker logs restaurantes-redis
   
   # Reinicia Redis si es necesario
   docker restart restaurantes-redis
   ```

### Reinicio Completo del Sistema

Si los problemas persisten, puedes intentar un reinicio completo:

```bash
# Detener todos los contenedores
docker-compose down

# Eliminar volúmenes (¡CUIDADO! Esto eliminará todos los datos)
docker-compose down -v

# Reconstruir y reiniciar
docker-compose up --build -d

# Recrear la base de datos
docker exec restaurantes-app python manage.py migrate

# Crear nuevo superusuario
docker exec restaurantes-app python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
"
```

---
 
## 🛠️ Comandos Útiles de Docker
 
```bash
# Ver logs de un servicio
docker-compose logs restaurantes-app
 
# Entrar a un contenedor
docker-compose exec restaurantes-app bash
 
# Detener contenedores
docker-compose down
 
# Eliminar volúmenes (cuidado!)
docker-compose down -v
```
 
---
 
## 🤝 Contribución
 
1. Haz un fork del repositorio
2. Crea tu rama de características
3. Commit de tus cambios
4. Push a la rama
5. Abre un Pull Request
 
---
 
## 📄 Licencia
 
[Especificar la licencia del proyecto]
 

---
 
## 📊 Monitoreo de Tareas Celery

### Verificar Estado del Worker
```bash
# Ver estado del worker de Celery
docker-compose logs restaurantes-celery

# Ver estado en tiempo real
docker-compose logs -f restaurantes-celery
```

### Gestión de Tareas
```bash
# Listar tareas registradas
docker-compose exec restaurantes-celery celery -A gestion_pedidos inspect registered

# Ver tareas activas
docker-compose exec restaurantes-celery celery -A gestion_pedidos inspect active

# Ver estadísticas de tareas
docker-compose exec restaurantes-celery celery -A gestion_pedidos inspect stats
```

### Monitoreo de Tareas Específicas
```bash
# Verificar estado de una tarea por ID
docker-compose exec restaurantes-app python manage.py shell -c "from celery.result import AsyncResult; AsyncResult('task-id').status"

# Ver resultado de una tarea
docker-compose exec restaurantes-app python manage.py shell -c "from celery.result import AsyncResult; print(AsyncResult('task-id').get())"
```

### Comandos de Control
```bash
# Detener worker de Celery
docker-compose stop restaurantes-celery

# Iniciar worker de Celery
docker-compose start restaurantes-celery

# Reiniciar worker de Celery
docker-compose restart restaurantes-celery
```

### Ejemplos de Uso
```python
# En el shell de Django
from restaurants.tasks import generate_restaurant_report
from celery.result import AsyncResult

# Crear una tarea
task = generate_restaurant_report.delay()
print(f"ID de la tarea: {task.id}")

# Verificar estado
result = AsyncResult(task.id)
print(f"Estado: {result.status}")

# Obtener resultado
if result.ready():
    print(f"Resultado: {result.get()}")
```

Notas:
- Los workers de Celery procesan tareas de forma asíncrona
- Cada tarea tiene un ID único para seguimiento
- Los estados posibles de una tarea son: PENDING, STARTED, SUCCESS, FAILURE, RETRY
- Los resultados de las tareas se almacenan en Redis por un tiempo limitado
