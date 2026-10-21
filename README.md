# Sistema de Gestión de Eventos

Este proyecto es una aplicación web desarrollada en Python utilizando el framework **Flask**. El sistema permite la creación y administración de eventos, dividiendo las funcionalidades de manera estricta mediante roles de usuario (**Organizador** y **Asistente**), cumpliendo con los lineamientos del taller integrador.

## 🚀 Características Principales
- **Autenticación Segura:** Registro e inicio de sesión de usuarios con contraseñas encriptadas mediante `werkzeug.security`.
- **Control de Acceso por Roles (RBAC):** - **Organizador:** Permisos completos para el CRUD de eventos (Crear, Leer, Editar, Eliminar) y visualización de la lista de asistentes inscritos.
  - **Asistente:** Acceso al catálogo general para inscribirse o cancelar inscripciones a eventos (con control automático de cupo máximo).
- **Perfil de Usuario:** Vista editable de datos básicos e historial dinámico según el rol (eventos creados o eventos inscritos).
- **Manejo de Errores:** Páginas personalizadas para los estados HTTP 403 (Acceso prohibido) y 404 (No encontrado).
- **Base de Datos:** Persistencia de datos utilizando **SQLite** y el ORM **Flask-SQLAlchemy**.

---

## 📂 Estructura del Proyecto
El diseño sigue una arquitectura modular mediante el uso de **Blueprints**:

```text
├── auth/                  # Módulo de Autenticación (Rutas y lógica)
├── events/                # Módulo de Eventos e Inscripciones (Rutas y lógica)
├── users/                 # Módulo de Perfiles de Usuario (Rutas y lógica)
├── templates/             # Vistas HTML puras (Estructura de páginas)
│   ├── auth/              # Formularios de login y registro
│   ├── events/            # Catálogo, Dashboard, formularios de creación/edición
│   ├── users/             # Interfaz de perfil
│   ├── base.html          # Plantilla maestra del sistema
│   └── error.html         # Manejador visual de errores (403/404)
├── app.py                 # Punto de entrada y configuración de la aplicación
├── models.py              # Definición de tablas y relaciones de la base de datos
├── seed.py                # Script automatizado para cargar datos de prueba
└── requirements.txt       # Listado de dependencias del proyecto