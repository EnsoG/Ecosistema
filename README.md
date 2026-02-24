# Ecosistema

**Ecosistema** es una plataforma web desarrollada en Django, diseñada para facilitar la gestión de usuarios y la generación automatizada de credenciales digitales mediante códigos QR.

## 🚀 Características Principales

- **Gestión Integral de Usuarios**: Administración centralizada de perfiles y datos de usuarios.
- **Generación de QR Automatizada**: Sistema inteligente (`generate_qrs.py`) para crear códigos QR únicos para cada miembro.
- **Asignación Dinámica de Emojis**: Funcionalidad creativa que asigna identificadores visuales (emojis) a los usuarios para una experiencia más amigable.
- **Paneles Dedicados**: Incluye módulos de autenticación (`login`) y administración (`paneladm`).

## 📋 Prerrequisitos

Asegúrate de tener instalado lo siguiente antes de comenzar:

- **Python**: Versión 3.12 o superior.
- **uv**: Gestor de paquetes ultrarrápido (Recomendado para la instalación).

## 🛠️ Guía de Instalación

Sigue estos pasos para configurar el entorno de desarrollo:

1.  **Crear el Entorno Virtual**
    Utilizamos `uv` para una configuración eficiente:
    ```powershell
    uv venv
    ```

2.  **Activar el Entorno**
    ```powershell
    .venv\Scripts\activate
    ```

3.  **Instalar Dependencias**
    Carga todas las librerías necesarias:
    ```powershell
    uv pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos**
    Genera la estructura inicial de la base de datos:
    ```powershell
    python manage.py migrate
    ```

    *(Opcional) Crea un administrador para tener acceso total:*
    ```powershell
    python manage.py createsuperuser
    ```

## 💻 Uso del Sistema

### 🌐 Iniciar el Servidor Web
Para interactuar con la aplicación web:

```powershell
python manage.py runserver
```
La aplicación estará disponible en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 📱 Generar Códigos QR
Para ejecutar el proceso por lotes de generación de QRs y asignación de emojis:

```powershell
python generate_qrs.py
```
*Este script procesará todos los usuarios existentes, generará sus QRs y actualizará sus perfiles.*

## 📂 Estructura del Proyecto

- **`Ecosistema/`**: Núcleo de configuración del proyecto Django.
- **`usuario/`**: Lógica de negocio relacionada con los usuarios y modelos de datos.
- **`paneladm/`**: Interfaz de administración del sistema.
- **`login/`**: Módulo de seguridad y autenticación.
- **`generate_qrs.py`**: Script de utilidad para tareas en segundo plano.
- **`media/`**: Almacenamiento de archivos generados (como los códigos QR).

---
*Documentación generada automáticamente para Ecosistema.*
