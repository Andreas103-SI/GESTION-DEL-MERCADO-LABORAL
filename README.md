# GESTIÓN DEL MERCADO LABORAL

## Descripción del Proyecto

Este proyecto es una plataforma de gestión de tareas y análisis del mercado laboral desarrollada con Django. Incluye funcionalidades para gestionar usuarios, proyectos y tareas, así como para analizar el mercado laboral utilizando inteligencia artificial y datos externos.

## Características Principales
- Gestión de usuarios con roles y permisos.
- CRUD para proyectos y tareas.
- Integración de datos externos de plataformas de empleo.
- Análisis del mercado laboral con dashboards interactivos.
- Recomendaciones de inteligencia artificial para asignación de tareas.

## Requisitos Previos
- Python 3.x
- Django
- PostgreSQL
- pip

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd GESTION-DEL-MERCADO-LABORAL
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows usa `env\Scripts\activate`
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto con las credenciales de la base de datos y otras variables sensibles.

5. Realiza las migraciones de la base de datos:
   ```bash
   python manage.py migrate
   ```

6. Ejecuta el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Endpoints Disponibles

### Páginas Principales
- Página de inicio: `http://127.0.0.1:8000/`
- Panel de administración: `http://127.0.0.1:8000/admin/`

### Análisis de Mercado
- Dashboard principal: `http://127.0.0.1:8000/market-analysis/dashboard/`
- Actualización de datos: `http://127.0.0.1:8000/market-analysis/update-scraper/`

### Integración de Datos
- Panel de scrapers: `http://127.0.0.1:8000/data-integration/`
- Dashboard de datos: `http://127.0.0.1:8000/data-integration/data-dashboard/`
- Resultados de scraping: `http://127.0.0.1:8000/data-integration/scrape-results/`

### Gestión de Usuarios
- Login: `http://127.0.0.1:8000/accounts/login/`
- Registro: `http://127.0.0.1:8000/accounts/register/`
- Perfil: `http://127.0.0.1:8000/users/profile/`

## Uso
- Accede a la aplicación en `http://127.0.0.1:8000/`.
- Registra usuarios y asigna roles.
- Crea y gestiona proyectos y tareas.
- Visualiza análisis del mercado laboral en el dashboard.
- Utiliza los scrapers para obtener datos actualizados del mercado laboral.

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para discutir cambios importantes.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Para más detalles, consulta el archivo LICENSE. 