# Plan de Testing para la Aplicación "Gestión del Mercado Laboral"

## Introducción

La aplicación "Gestión del Mercado Laboral" es un sistema diseñado para gestionar ofertas de empleo, tareas y usuarios. Tiene dos componentes principales:
1. Un backend desarrollado en Django que gestiona los datos (modelos como `JobOffer`, `Task`, y `CustomUser`) y una base de datos (PostgreSQL).
2. Una aplicación de escritorio desarrollada con Tkinter que permite a los usuarios interactuar con los datos a través de una interfaz gráfica con pestañas para "Ofertas de Empleo", "Tareas" y "Usuarios".

Además, incluye un módulo de scraping (`market_analysis/tasks.py`) que extrae ofertas de empleo de LinkedIn y Tecnoempleo utilizando Selenium y las guarda en la base de datos.

El objetivo principal de la aplicación es permitir a los usuarios visualizar, añadir, actualizar y eliminar registros de ofertas de empleo, tareas y usuarios de manera eficiente y sin errores, así como automatizar la recolección de datos de ofertas de empleo desde fuentes externas.

Este plan de testing se centra en probar la funcionalidad de la aplicación de escritorio, los modelos del backend, y los scrapers de LinkedIn y Tecnoempleo.

## Objetivo del Testing

El objetivo de este plan de testing es verificar que las funcionalidades principales de la aplicación de escritorio, los modelos del backend, y los scrapers operen correctamente sin errores críticos. Esto incluye:
- Asegurar que los usuarios puedan interactuar con las pestañas "Ofertas de Empleo", "Tareas" y "Usuarios".
- Validar que las operaciones de añadir, actualizar y eliminar registros funcionen como se espera.
- Verificar que los modelos del backend (`JobOffer`, `Project`, `Task`, `Skill`, `CustomUser`) se comporten correctamente.
- Asegurar que los scrapers de LinkedIn y Tecnoempleo extraigan y guarden datos correctamente.
- Identificar posibles errores de usabilidad, validación de datos y estabilidad de la aplicación.

## Alcance del Testing

**Partes que serán probadas**:
- La pestaña "Ofertas de Empleo" en la aplicación de escritorio:
  - Visualización de ofertas de empleo existentes.
  - Añadir, actualizar y eliminar ofertas de empleo.
- Funcionalidades básicas de la interfaz gráfica (interacción con el `Treeview`, campos de entrada y botones).
- Validaciones de datos (por ejemplo, campos obligatorios como título y empresa).
- Flujo de usuario (por ejemplo, selección de una oferta para actualizar o eliminar).
- Modelos del backend mediante pruebas unitarias automatizadas:
  - Modelos en `market_analysis`: `JobOffer`, `Skill`, `MarketData`.
  - Modelos en `projects`: `Project`, `Task`, `Skill`.
  - Modelos en `users`: `CustomUser`.
- Scrapers en `market_analysis/tasks.py`:
  - `run_linkedin_scraper`: Extracción de ofertas de LinkedIn.
  - `scrape_tecnoempleo`: Extracción de ofertas de Tecnoempleo.

**Partes que NO serán probadas**:
- Las pestañas "Tareas" y "Usuarios" en la aplicación de escritorio (se probarán en una fase posterior).
- La interfaz de administración de Django (`/admin/`).
- Funcionalidades del módulo `ai_module` (actualmente vacío).
- Rendimiento de la aplicación (como tiempos de carga o manejo de grandes volúmenes de datos).
- Pruebas de seguridad (como inyección SQL o accesos no autorizados).

## Estrategia de Testing

### **Pruebas Manuales**

**Método**:
- Se realizaron pruebas manuales para la aplicación de escritorio, simulando el rol de un QA Junior sin herramientas de automatización para la interfaz gráfica.

**Tipos de Testing**:
- **Testing Funcional**: Verificar que las funcionalidades principales (visualizar, añadir, actualizar, eliminar) funcionen correctamente.
- **Testing de Validaciones**: Comprobar que las validaciones de datos (campos obligatorios, formatos correctos) se apliquen correctamente.
- **Testing de Flujo de Usuario**: Asegurar que el flujo de interacción del usuario sea intuitivo (por ejemplo, seleccionar una oferta, modificarla y actualizarla).
- **Testing Negativo**: Probar escenarios donde el usuario comete errores (como dejar campos obligatorios vacíos o intentar eliminar sin seleccionar una oferta).

**Herramientas**:
- Aplicación de escritorio (`desktop_app/main.py`).
- Base de datos (PostgreSQL).
- Interfaz de administración de Django para crear datos de prueba (`python manage.py runserver` y acceder a `http://127.0.0.1:8000/admin/`).

**Preparación**:
- Se crearon datos de prueba (5 ofertas de empleo) usando la interfaz de administración de Django.
- Se aseguraron que las migraciones estuvieran aplicadas (`python manage.py makemigrations` y `python manage.py migrate`).

### **Pruebas Unitarias Automatizadas**

**Método**:
- Se realizaron pruebas unitarias automatizadas para los modelos del backend y los scrapers usando el framework de testing de Django (`django.test.TestCase`).

**Archivos de prueba**:
- `market_analysis/tests.py`:
  - Pruebas para los modelos `JobOffer`, `Skill`, y `MarketData`.
  - Pruebas para los scrapers `run_linkedin_scraper` y `scrape_tecnoempleo`.
- `projects/tests.py`: Pruebas para los modelos `Project`, `Task`, y `Skill`.
- `users/tests.py`: Pruebas para el modelo `CustomUser`.
- `ai_module/tests.py`: Actualmente vacío, ya que el módulo `ai_module` no tiene funcionalidad implementada.

**Comando para ejecutar las pruebas**:
```bash
python manage.py test