# 🔧 Sistema de Gestión de Taller Automotriz

Aplicación de escritorio desarrollada en **Python** con **Tkinter** y **MySQL** para administrar las operaciones diarias de un taller mecánico. Incluye autenticación segura con encriptación, control de acceso basado en roles (RBAC), gestión de inventario de refacciones y registro transaccional de órdenes de reparación.

## ✨ Características Principales

* **Autenticación y Control de Roles:**
  * Inicio de sesión con contraseñas cifradas mediante **SHA-256** (`hashlib`).
  * **Administrador:** Acceso total (Usuarios, Clientes, Vehículos, Reparaciones y Piezas).
  * **Mecánico:** Acceso a Vehículos, Reparaciones y Piezas.
  * **Auxiliar:** Acceso a Clientes, Vehículos y Piezas.
* **Módulos CRUD Completos:**
  * **Usuarios:** Gestión de personal con validación de `username` único y asignación de perfiles.
  * **Clientes:** Registro con validación de `RFC` único y trazabilidad automática del usuario que atiende.
  * **Vehículos:** Control por matrícula única vinculada a un cliente propietario.
  * **Piezas (Inventario):** Administración de stock de refacciones con validaciones numéricas.
* **Órdenes de Reparación Transaccionales (Maestro-Detalle):**
  * Asignación múltiple de piezas por folio de reparación mediante tabla dinámica (`ttk.Treeview`).
  * **Control de Stock Automático:** Descuenta piezas del inventario al guardar una orden, valida disponibilidad antes de confirmar y reintegra el stock automáticamente si la orden se edita o elimina.
  * Validación cronológica de fechas de entrada y salida (`AAAA-MM-DD`).

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** `tkinter` / `ttk`
* **Base de Datos:** MySQL (compatible con **XAMPP** / MariaDB)
* **Conector MySQL:** `mysql-connector-python`
* **Seguridad y Fechas:** `hashlib` (SHA-256) y `datetime`

## ⚙️ Requisitos e Instalación

1. **Clona este repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/sistema-taller-automotriz.git](https://github.com/tu-usuario/sistema-taller-automotriz.git)
   cd sistema-taller-automotriz
