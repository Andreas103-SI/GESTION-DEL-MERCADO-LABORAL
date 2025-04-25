# GESTIÓN DEL MERCADO LABORAL - Documentación del Proyecto

## Proyecto
**Plataforma de Gestión de Tareas y Análisis del Mercado Laboral con Inteligencia Artificial, Integración de Datos Externos y CRUD de Escritorio**

- **Objetivo**:
  - Desarrollar una aplicación web Django para gestionar tareas colaborativas, analizar el mercado laboral en Asturias, y recomendar tareas/habilidades con IA.
  - Crear una aplicación de escritorio con CRUD para gestionar datos (ofertas, tareas, usuarios).
  - Producir documentación técnica y un manual de usuario.

- **Componentes**:
  - **Gestión de Usuarios** (`users/`):
    - Registro/login con `Django Authentication`.
    - Roles: `admin` (gestiona datos/usuarios), `project_manager` (crea proyectos/tareas), `collaborator` (completa tareas).
    - Modelo: `CustomUser` con `django-role-permissions`.
  - **Proyectos y Tareas** (`projects/`):
    - Modelos: `Project` (nombre, descripción, fechas), `Task` (título, estado, prioridad, habilidades, asignados).
    - CRUD web en `projects/views.py` para proyectos/tareas.
    - Relaciones: Proyecto → Tareas → Colaboradores (muchos-a-muchos).
  - **Análisis del Mercado Laboral** (`market_analysis/`):
    - Modelos: `JobOffer` (title, company, location, publication_date, source, salary), `Skill` (name).
    - Dashboard: `http://127.0.0.1:8000/market/dashboard/` con tendencias (habilidades demandadas, comparación de fuentes).
    - Gráficos: Chart.js (en progreso).
  - **Integración de Datos Externos** (`data_integration/`):
    - **Fuentes**:
      - Tecnoempleo: https://www.tecnoempleo.com/ofertas-trabajo/?keyword=desarrollador&provincia=33
      - InfoJobs: https://www.infojobs.net/ofertas-trabajo?keywords=desarrollador&province=asturias
      - LinkedIn: https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000
    - Scrapers en `data_integration/views.py`:
      - Tecnoempleo: Completo (30 ofertas, título, empresa, ubicación, fecha, habilidades).
      - InfoJobs: Parcial (20-30 ofertas, título, empresa, ubicación, fecha; habilidades en progreso).
      - LinkedIn: En curso (0 ofertas, autenticación manual, selectores obsoletos).
    - Template: `data_integration/templates/data_integration/scrape_results.html` (título, empresa, ubicación, fecha, habilidades, "Se han extraído Z ofertas", rango de fechas).
    - Debug: `tecnoempleo_debug.html`, `infojobs_debug.html`, `linkedin_debug.html`.
  - **Inteligencia Artificial** (`ai_module/`, planificado):
    - Recomendaciones: Asignar tareas según habilidades con scikit-learn.
    - Predicciones: Estimar demandas de habilidades futuras.
    - Integración en dashboard (pendiente).
  - **CRUD de Escritorio** (planificado):
    - Aplicación en Tkinter/PyQt para gestionar `JobOffer`, `Task`, `CustomUser`.
    - Conexión a PostgreSQL.
    - Interfaz con validación de datos.

- **Base de Datos**:
  - PostgreSQL (producción) o SQLite (desarrollo).
  - Relaciones: `JobOffer` ↔ `Skill` (muchos-a-muchos), `Project` → `Task` → `CustomUser`.
  - Índices para búsquedas (título, habilidades, fecha).

- **Frontend Web**:
  - Plantillas Django con Bootstrap.
  - Dashboard con estadísticas, tendencias, y tareas asignadas.
  - URLs: `http://127.0.0.1:8000/data/scrape/`, `http://127.0.0.1:8000/market/dashboard/`, `http://127.0.0.1:8000/projects/`.

- **Documentación**:
  - Técnica: Arquitectura, diagramas ER, instalación (`docs/proyecto.md`).
  - Manual de usuario: Guía web/escritorio con capturas (en progreso).
  - Pruebas: Tests unitarios para scrapers (ver Testing).

- **Estado al 13/04/2025**:
  - Web: Autenticación, roles, y scrapers avanzados (Tecnoempleo completo, InfoJobs parcial, LinkedIn en curso).
  - Escritorio: Pendiente.
  - Dashboard: Muestra datos de Tecnoempleo, parcial para InfoJobs.
  - IA: Planificada.

## Conocimiento de Fases
El proyecto se divide en 10 fases iterativas:

- **Fase 1: Configuración del Entorno**:
  - Proyecto Django en `/Users/ANDREASIERRA/Desktop/GESTION-DEL-MERCADO-LABORAL/job_platform`.
  - Modelos: `JobOffer` (title, company, location, publication_date, source, salary), `Skill` (name), `CustomUser` (autenticación), `Project`, `Task` (proyectos/tareas).
  - Apps: `data_integration`, `market_analysis`, `users`, `projects`.

- **Fase 2: Autenticación y Roles**:
  - Registro/login con `Django Authentication` (`users/views.py`).
  - Roles con `django-role-permissions`: `admin` (scrapers, usuarios), `project_manager` (proyectos/tareas), `collaborator` (tareas).
  - Restricción de acceso (p.ej., `has_role_decorator('admin')` en scrapers).

- **Fase 3: Gestión de Proyectos y Tareas**:
  - Modelos: `Project` (nombre, descripción, fechas), `Task` (título, estado, prioridad, habilidades, asignados).
  - CRUD web para proyectos/tareas en `projects/views.py`.
  - Relaciones: Proyecto → Tareas → Colaboradores (muchos-a-muchos).

- **Fase 4: Scraper de Tecnoempleo**:
  - Extracción pública de https://www.tecnoempleo.com/ofertas-trabajo/?keyword=desarrollador&provincia=33.
  - Datos: Título, empresa, ubicación, fecha, habilidades.
  - Guardado en `JobOffer`, `Skill` con `get_or_create`.
  - Resultados: 30 ofertas, fechas 11/04/2025 a 12/04/2025, mensaje "Se han extraído 30 ofertas".

- **Fase 5: Scraper de InfoJobs**:
  - Extracción pública de https://www.infojobs.net/ofertas-trabajo?keywords=desarrollador&province=asturias.
  - Datos: Título, empresa, ubicación, fecha (habilidades en progreso).
  - Guardado en `JobOffer`, `Skill` (parcial).
  - Estado: 20-30 ofertas, pero habilidades incompletas.

- **Fase 6: Scraper de LinkedIn**:
  - Autenticación manual (90 segundos) en https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000.
  - Datos: Título, empresa, ubicación, fecha (habilidades pendientes).
  - Estado: 0 ofertas (selectores obsoletos, en corrección).

- **Fase 7: Análisis del Mercado Laboral**:
  - Dashboard (`market_analysis/views.py`): Habilidades demandadas, comparación de fuentes, últimas ofertas.
  - Template: `market_analysis/templates/market_analysis/dashboard.html`.
  - Gráficos con Chart.js (en progreso).

- **Fase 8: Inteligencia Artificial**:
  - Recomendaciones: Modelo (scikit-learn) para asignar tareas según habilidades (planificado).
  - Predicciones: Tendencias de habilidades futuras (planificado).
  - Estado: Pendiente.

- **Fase 9: Aplicación de Escritorio (CRUD)**:
  - CRUD para `JobOffer`, `Task`, `CustomUser` con Tkinter/PyQt.
  - Conexión a PostgreSQL.
  - Estado: Pendiente.

- **Fase 10: Documentación, Pruebas, Entregables**:
  - Documentación técnica: Arquitectura, diagramas, instalación (`docs/proyecto.md`).
  - Manual de usuario: Guía web/escritorio con capturas.
  - Pruebas: Tests unitarios para scrapers (ver Testing).
  - Estado: Documentación avanzada, pruebas pendientes.

## Testing
- **Tecnoempleo** (planificado, `market_analysis/tests.py`):
  - Parseo de fechas (`11/04/2025` desde `<span>Barcelona - 11/04/2025</span>`).
  - Limpieza de salario (`27.000€ - 33.000€ b/a` → fecha).
  - Guardado en `JobOffer` (título, empresa, etc.) y `Skill` (habilidades).
  - Mock de HTML con `tecnoempleo_debug.html`.
- **InfoJobs** (planificado, `market_analysis/tests.py`):
  - Parseo de fechas (`11/04/2025` desde `<div>Publicado el 11/04/2025</div>`).
  - Guardado en `JobOffer` (título, empresa, ubicación).
  - Mock de HTML con `infojobs_debug.html`.
- **LinkedIn** (planificado, `market_analysis/tests.py`):
  - Parseo de fechas (`2025-04-12` desde `<time datetime="2025-04-12">`).
  - Guardado en `JobOffer` (título, empresa, ubicación) y `Skill` (habilidades).
  - Mock de HTML con `linkedin_debug.html`.
- **Framework**: `django.test.TestCase`.
- **Ejecutar**: `python manage.py test market_analysis`.
- **Estado**: Tests escritos, pendientes de ejecución.

## Estado al 13/04/2025
- **Tecnoempleo**: Finalizado (30 ofertas, fechas 11/04/2025 a 12/04/2025).
- **InfoJobs**: Parcial (20-30 ofertas, falta habilidades).
- **LinkedIn**: En curso (0 ofertas, autenticación lista, selectores en corrección).
- **Dashboard**: Muestra datos de Tecnoempleo, parcial para InfoJobs.
- **IA/Escritorio**: Planificados.
- **Pruebas**: Tests planificados para las tres plataformas.

## Configuración de Variables de Entorno

Para mejorar la seguridad de tu proyecto Django, es recomendable utilizar un archivo `.env` para almacenar variables sensibles como las credenciales de la base de datos. A continuación se detallan los pasos para configurar esto:

### Instalación de python-dotenv

1. Asegúrate de tener `python-dotenv` instalado en tu entorno de desarrollo. Puedes instalarlo usando pip:
   ```bash
   pip install python-dotenv
   ```

### Creación del archivo .env

2. Crea un archivo llamado `.env` en la raíz de tu proyecto con el siguiente contenido:
   ```
   DB_NAME=nombre_real_de_tu_base_de_datos
   DB_USER=usuario_real
   DB_PASSWORD=contraseña_real
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Modificación de settings.py

3. Asegúrate de que tu archivo `settings.py` esté configurado para cargar las variables de entorno desde el archivo `.env`:
   ```python
   import os
   from dotenv import load_dotenv

   # Cargar las variables de entorno desde el archivo .env
   load_dotenv()

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DB_NAME'),
           'USER': os.getenv('DB_USER'),
           'PASSWORD': os.getenv('DB_PASSWORD'),
           'HOST': os.getenv('DB_HOST'),
           'PORT': os.getenv('DB_PORT'),
       }
   }
   ```

### Asegúrate de que el archivo .env no se suba al repositorio

4. Añade el archivo `.env` a tu archivo `.gitignore` para evitar que se suba a tu repositorio:
   ```
   # .gitignore
   .env
   ```

### Verificación

5. Ejecuta el servidor de desarrollo de Django para verificar que todo funcione correctamente:
   ```bash
   python manage.py runserver
   ```

Siguiendo estos pasos, podrás mantener tus variables sensibles seguras y fuera del código fuente.
Captura de pantalla 2025-04-25 144111.png
Captura de pantalla 2025-04-25 144152.png
Captura de pantalla 2025-04-25 144305.png
Captura de pantalla 2025-03-31 123955.png