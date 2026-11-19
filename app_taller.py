import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
from datetime import datetime

# ==========================================
# FUNCIÓN DE ENCRIPTACIÓN
# ==========================================
def encriptar_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ==========================================
# CONEXIÓN A BASE DE DATOS
# ==========================================
def conectar_db():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="taller_automotriz"
        )
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Fallo la conexion: {error}")
        return None

# ==========================================
# CLASE BASE (Diseño Básico por defecto)
# ==========================================
class VistaBase(tk.Frame):
    # NUEVO: Se agregó tabla_db para saber a qué tabla consultarle el siguiente ID
    def __init__(self, parent, app, titulo, texto_busqueda="Buscar ID:", tabla_db=None):
        super().__init__(parent)
        self.app = app 
        self.entradas = {}
        self.tabla_db = tabla_db
        self.es_nuevo = False # NUEVO: Control para saber si guardamos o editamos
        
        tk.Label(self, text=titulo, font=("Arial", 14)).pack(pady=10)
        
        frame_busqueda = tk.Frame(self)
        frame_busqueda.pack(pady=5)
        
        tk.Label(frame_busqueda, text=texto_busqueda).pack(side="left")
        self.entry_busqueda = tk.Entry(frame_busqueda, width=20)
        self.entry_busqueda.pack(side="left")
        self.btn_buscar = tk.Button(frame_busqueda, text="Buscar", command=self.accion_buscar)
        self.btn_buscar.pack(side="left", padx=5)
        
        tk.Label(self, text="------------------------------------------------------").pack()

        self.frame_formulario = tk.Frame(self)
        self.frame_formulario.pack(pady=10)

        self.frame_botones = tk.Frame(self)
        self.frame_botones.pack(pady=10)

    def crear_botones(self):
        self.btn_nuevo = tk.Button(self.frame_botones, text="Nuevo", command=self.accion_nuevo, width=10)
        self.btn_nuevo.pack(side="left", padx=2)

        self.btn_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.accion_guardar, width=10)
        self.btn_guardar.pack(side="left", padx=2)

        self.btn_editar = tk.Button(self.frame_botones, text="Editar", command=self.accion_editar, width=10)
        self.btn_editar.pack(side="left", padx=2)

        self.btn_remover = tk.Button(self.frame_botones, text="Remover", command=self.accion_remover, width=10)
        self.btn_remover.pack(side="left", padx=2)
        
        self.btn_cancelar = tk.Button(self.frame_botones, text="Cancelar", command=self.accion_cancelar, width=10)
        self.btn_cancelar.pack(side="left", padx=2)
        
        self.estado_inicial()

    def alternar_campos(self, estado):
        estado_tk = "normal" if estado else "disabled"
        for campo, widget in self.entradas.items():
            if campo not in ["ID", "Usuario (Atiende)"]: 
                widget.config(state=estado_tk)

    def limpiar_campos(self):
        for campo, widget in self.entradas.items():
            if campo != "Usuario (Atiende)": 
                widget.config(state="normal")
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ttk.Combobox):
                    widget.set('')
        self.alternar_campos(False)

    def estado_inicial(self):
        self.es_nuevo = False
        self.limpiar_campos()
        self.entry_busqueda.config(state="normal")
        self.entry_busqueda.delete(0, tk.END)
        self.btn_buscar.config(state="normal")

        self.btn_nuevo.config(state="normal")
        self.btn_guardar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")
        self.btn_editar.config(state="disabled")
        self.btn_remover.config(state="disabled")
        
        if "ID" in self.entradas: self.entradas["ID"].config(state="readonly")
        if "Matricula" in self.entradas: self.entradas["Matricula"].config(state="disabled")

    # NUEVO: Función para calcular el número que sigue en la base de datos
    def obtener_siguiente_id(self):
        siguiente = "Automático"
        if self.tabla_db:
            if self.tabla_db == "usuarios": pk = "usuario_id"
            elif self.tabla_db == "clientes": pk = "cliente_id"
            elif self.tabla_db == "piezas": pk = "pieza_id"
            elif self.tabla_db == "reparaciones": pk = "folio"
            else: return siguiente

            conexion = conectar_db()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(f"SELECT MAX({pk}) FROM {self.tabla_db}")
                    max_id = cursor.fetchone()[0]
                    siguiente = str(max_id + 1) if max_id is not None else "1"
                except Exception:
                    pass
                finally:
                    conexion.close()
        return siguiente

    def accion_nuevo(self):
        self.es_nuevo = True
        self.limpiar_campos()
        self.alternar_campos(True) 
        
        self.entry_busqueda.config(state="disabled")
        self.btn_buscar.config(state="disabled")
        
        if "ID" in self.entradas:
            self.entradas["ID"].config(state="normal")
            # NUEVO: En lugar de "Automático", inserta el número real calculado
            self.entradas["ID"].insert(0, self.obtener_siguiente_id())
            self.entradas["ID"].config(state="readonly")
            
        if "Matricula" in self.entradas:
            self.entradas["Matricula"].config(state="normal")

        self.btn_nuevo.config(state="disabled")
        self.btn_guardar.config(state="normal") 
        self.btn_cancelar.config(state="normal")
        self.btn_editar.config(state="disabled")
        self.btn_remover.config(state="disabled")

    def estado_post_busqueda(self):
        self.entry_busqueda.config(state="disabled")
        self.btn_buscar.config(state="disabled")
        
        if "ID" in self.entradas: self.entradas["ID"].config(state="readonly")
        if "Matricula" in self.entradas: self.entradas["Matricula"].config(state="readonly")
            
        self.btn_nuevo.config(state="disabled")
        self.btn_guardar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.btn_editar.config(state="normal")
        self.btn_remover.config(state="normal")

    def accion_cancelar(self):
        self.estado_inicial()

    def accion_editar(self):
        self.es_nuevo = False
        self.alternar_campos(True)
        if "Matricula" in self.entradas:
            self.entradas["Matricula"].config(state="readonly") 
            
        self.btn_editar.config(state="disabled")
        self.btn_remover.config(state="disabled")
        self.btn_guardar.config(state="normal")

    def rellenar_datos(self, campos_ordenados, datos):
        self.alternar_campos(True)
        if "ID" in self.entradas: self.entradas["ID"].config(state="normal")
        if "Matricula" in self.entradas: self.entradas["Matricula"].config(state="normal")
        
        for campo, valor in zip(campos_ordenados, datos):
            if campo in self.entradas:
                self.entradas[campo].delete(0, tk.END)
                if valor is None:
                    valor = ""
                self.entradas[campo].insert(0, str(valor))
                if isinstance(self.entradas[campo], ttk.Combobox):
                    self.entradas[campo].set(str(valor))
                    
        self.alternar_campos(False)
        self.estado_post_busqueda()

    def accion_buscar(self): pass 
    def accion_guardar(self): pass
    def accion_remover(self): pass


# ==========================================
# MÓDULOS ESPECÍFICOS
# ==========================================
class VistaUsuarios(VistaBase):
    def __init__(self, parent, app):
        # Se agrega "usuarios" como el parámetro de tabla
        super().__init__(parent, app, "Módulo de Usuarios", "Buscar por ID:", "usuarios")
        self.crear_widgets()

    def crear_widgets(self):
        campos = ["ID", "Nombre", "Username", "Password", "Telefono", "Email"]
        for i, campo in enumerate(campos):
            tk.Label(self.frame_formulario, text=campo+":").grid(row=i, column=0, pady=5, sticky="e")
            entry = tk.Entry(self.frame_formulario, width=30)
            entry.grid(row=i, column=1, pady=5)
            self.entradas[campo] = entry

        tk.Label(self.frame_formulario, text="Perfil:").grid(row=len(campos), column=0, pady=5, sticky="e")
        self.combo_perfil = ttk.Combobox(self.frame_formulario, values=["Administrador", "Mecanico", "Auxiliar"], width=27, state="readonly")
        self.combo_perfil.grid(row=len(campos), column=1, pady=5)
        self.entradas["Perfil"] = self.combo_perfil
        self.crear_botones()

    def accion_buscar(self):
        id_busqueda = self.entry_busqueda.get().strip()
        if not id_busqueda.isdigit(): 
            messagebox.showwarning("Aviso", "Ingrese ID valido")
            return
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT usuario_id, nombre, username, password, telefono, email, perfil FROM usuarios WHERE usuario_id = %s", (id_busqueda,))
            resultado = cursor.fetchone()
            conexion.close()
            
            if resultado:
                resultado_lista = list(resultado)
                resultado_lista[3] = "********" 
                self.rellenar_datos(["ID", "Nombre", "Username", "Password", "Telefono", "Email", "Perfil"], resultado_lista)
            else:
                messagebox.showinfo("Mensaje", "Usuario no encontrado")

    def accion_guardar(self):
        datos = [self.entradas[c].get().strip() for c in ["Nombre", "Username", "Password", "Perfil", "Telefono", "Email"]]
        if "" in datos:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        password_ingresada = datos[2]
        if password_ingresada != "********":
            datos[2] = encriptar_password(password_ingresada)
        else:
            messagebox.showwarning("Aviso", "Por favor escriba la contraseña nuevamente para guardar.")
            return

        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                username = datos[1]

                if self.es_nuevo:
                    cursor.execute("SELECT usuario_id FROM usuarios WHERE username = %s", (username,))
                    if cursor.fetchone():
                        messagebox.showwarning("Aviso", "El username ya está en uso. Elija otro.")
                        return

                    cursor.execute("INSERT INTO usuarios (nombre, username, password, perfil, telefono, email) VALUES (%s, %s, %s, %s, %s, %s)", datos)
                    messagebox.showinfo("Exito", "Guardado ok")
                else:
                    id_actual = self.entradas["ID"].get()
                    cursor.execute("SELECT usuario_id FROM usuarios WHERE username = %s AND usuario_id != %s", (username, id_actual))
                    if cursor.fetchone():
                        messagebox.showwarning("Aviso", "El username ya está en uso. Elija otro.")
                        return

                    datos.append(id_actual)
                    cursor.execute("UPDATE usuarios SET nombre=%s, username=%s, password=%s, perfil=%s, telefono=%s, email=%s WHERE usuario_id=%s", datos)
                    messagebox.showinfo("Exito", "Actualizado ok")
                conexion.commit()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conexion.close()
        self.estado_inicial()

    def accion_remover(self):
        if self.es_nuevo: return
        id_actual = self.entradas["ID"].get()
        if not id_actual: return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este usuario?"):
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    cursor.execute("DELETE FROM usuarios WHERE usuario_id = %s", (id_actual,))
                    conexion.commit()
                    messagebox.showinfo("Exito", "Usuario eliminado correctamente.")
                    self.estado_inicial()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                finally:
                    conexion.close()

class VistaClientes(VistaBase):
    def __init__(self, parent, app):
        # Se agrega "clientes" como parámetro de tabla
        super().__init__(parent, app, "Módulo de Clientes", "Buscar por ID:", "clientes")
        self.crear_widgets()

    def crear_widgets(self):
        campos = ["ID", "RFC", "Nombre", "Telefono", "Email"]
        for i, campo in enumerate(campos):
            tk.Label(self.frame_formulario, text=campo+":").grid(row=i, column=0, pady=5, sticky="e")
            entry = tk.Entry(self.frame_formulario, width=30)
            entry.grid(row=i, column=1, pady=5)
            self.entradas[campo] = entry

        tk.Label(self.frame_formulario, text="Usuario (Atiende):").grid(row=len(campos), column=0, pady=5, sticky="e")
        entry_user = tk.Entry(self.frame_formulario, width=30)
        entry_user.insert(0, f"{self.app.id_usuario} - {self.app.nombre_usuario}")
        entry_user.config(state="readonly") 
        entry_user.grid(row=len(campos), column=1, pady=5)
        self.entradas["Usuario (Atiende)"] = entry_user
        self.crear_botones()

    def accion_buscar(self):
        id_busqueda = self.entry_busqueda.get().strip()
        if not id_busqueda.isdigit(): return
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            query = """SELECT c.cliente_id, c.rfc, c.nombre, c.telefono, c.email, CONCAT(u.usuario_id, ' - ', u.nombre) 
                       FROM clientes c JOIN usuarios u ON c.usuario_id = u.usuario_id WHERE c.cliente_id = %s"""
            cursor.execute(query, (id_busqueda,))
            resultado = cursor.fetchone()
            conexion.close()
            
            if resultado:
                self.entradas["Usuario (Atiende)"].config(state="normal")
                self.rellenar_datos(["ID", "RFC", "Nombre", "Telefono", "Email", "Usuario (Atiende)"], resultado)
                self.entradas["Usuario (Atiende)"].config(state="readonly")
            else:
                messagebox.showinfo("Mensaje", "Cliente no encontrado")

    def accion_guardar(self):
        datos = [self.entradas[c].get().strip() for c in ["RFC", "Nombre", "Telefono", "Email"]]
        if "" in datos:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                rfc = datos[0]

                if self.es_nuevo:
                    cursor.execute("SELECT cliente_id FROM clientes WHERE rfc = %s", (rfc,))
                    if cursor.fetchone():
                        messagebox.showwarning("Aviso", "Este RFC ya está registrado en el sistema.")
                        return

                    cursor.execute("INSERT INTO clientes (rfc, nombre, telefono, email, usuario_id) VALUES (%s, %s, %s, %s, %s)", (*datos, self.app.id_usuario))
                    messagebox.showinfo("Exito", "Guardado ok")
                else:
                    id_actual = self.entradas["ID"].get()
                    cursor.execute("SELECT cliente_id FROM clientes WHERE rfc = %s AND cliente_id != %s", (rfc, id_actual))
                    if cursor.fetchone():
                        messagebox.showwarning("Aviso", "Este RFC ya está registrado en otro cliente.")
                        return

                    cursor.execute("UPDATE clientes SET rfc=%s, nombre=%s, telefono=%s, email=%s WHERE cliente_id=%s", (*datos, id_actual))
                    messagebox.showinfo("Exito", "Actualizado ok")
                conexion.commit()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conexion.close()
        self.estado_inicial()

    def accion_remover(self):
        if self.es_nuevo: return
        id_actual = self.entradas["ID"].get()
        if not id_actual: return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este cliente?"):
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    cursor.execute("DELETE FROM clientes WHERE cliente_id = %s", (id_actual,))
                    conexion.commit()
                    messagebox.showinfo("Exito", "Cliente eliminado correctamente.")
                    self.estado_inicial()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                finally:
                    conexion.close()


class VistaVehiculos(VistaBase):
    def __init__(self, parent, app):
        # Vehículos no tiene auto-increment (usa Matrícula), pasamos None
        super().__init__(parent, app, "Módulo de Vehículos", "Matrícula:", None)
        self.crear_widgets()
        self.cargar_clientes()

    def crear_widgets(self):
        campos = ["Matricula", "Marca", "Modelo", "Año", "Color", "Kilometros"]
        for i, campo in enumerate(campos):
            tk.Label(self.frame_formulario, text=campo+":").grid(row=i, column=0, pady=5, sticky="e")
            entry = tk.Entry(self.frame_formulario, width=30)
            entry.grid(row=i, column=1, pady=5)
            self.entradas[campo] = entry

        tk.Label(self.frame_formulario, text="Cliente ID:").grid(row=len(campos), column=0, pady=5, sticky="e")
        self.combo_clientes = ttk.Combobox(self.frame_formulario, width=27, state="readonly")
        self.combo_clientes.grid(row=len(campos), column=1, pady=5)
        self.entradas["ClienteID"] = self.combo_clientes
        self.crear_botones()

    def cargar_clientes(self):
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT cliente_id, nombre FROM clientes")
            clientes = cursor.fetchall()
            self.combo_clientes['values'] = [f"{c[0]} - {c[1]}" for c in clientes]
            conexion.close()

    def accion_buscar(self):
        matricula = self.entry_busqueda.get().strip()
        if not matricula: return
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            query = """SELECT v.matricula, v.marca, v.modelo, v.año, v.color, v.kilometros, CONCAT(c.cliente_id, ' - ', c.nombre) 
                       FROM vehiculos v JOIN clientes c ON v.cliente_id = c.cliente_id WHERE v.matricula = %s"""
            cursor.execute(query, (matricula,))
            resultado = cursor.fetchone()
            conexion.close()
            
            if resultado:
                self.rellenar_datos(["Matricula", "Marca", "Modelo", "Año", "Color", "Kilometros", "ClienteID"], resultado)
            else:
                messagebox.showinfo("Mensaje", "Vehículo no encontrado")

    def accion_guardar(self):
        datos = [self.entradas[c].get().strip() for c in ["Matricula", "Marca", "Modelo", "Año", "Color", "Kilometros"]]
        cliente_sel = self.entradas["ClienteID"].get()
        if "" in datos or not cliente_sel:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        try:
            int(datos[3]) 
            int(datos[5]) 
        except ValueError:
            messagebox.showwarning("Aviso", "El Año y los Kilómetros deben ser números enteros.")
            return

        id_cliente = cliente_sel.split(" - ")[0]
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                matricula = datos[0]
                cursor.execute("SELECT cliente_id FROM vehiculos WHERE matricula = %s", (matricula,))
                vehiculo_existente = cursor.fetchone()

                if vehiculo_existente:
                    if str(vehiculo_existente[0]) != id_cliente:
                        messagebox.showerror("Aviso Lógico", "Esta matrícula ya está registrada a otro cliente.")
                        return
                    else:
                        datos_update = datos[1:] + [id_cliente, matricula]
                        cursor.execute("UPDATE vehiculos SET marca=%s, modelo=%s, año=%s, color=%s, kilometros=%s, cliente_id=%s WHERE matricula=%s", datos_update)
                        messagebox.showinfo("Exito", "Actualizado ok")
                else:
                    cursor.execute("INSERT INTO vehiculos (matricula, marca, modelo, año, color, kilometros, cliente_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (*datos, id_cliente))
                    messagebox.showinfo("Exito", "Guardado ok")
                conexion.commit()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conexion.close()
        self.estado_inicial()

    def accion_remover(self):
        if self.es_nuevo: return
        matricula_actual = self.entradas["Matricula"].get()
        if not matricula_actual: return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este vehículo?"):
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    cursor.execute("DELETE FROM vehiculos WHERE matricula = %s", (matricula_actual,))
                    conexion.commit()
                    messagebox.showinfo("Exito", "Vehículo eliminado correctamente.")
                    self.estado_inicial()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                finally:
                    conexion.close()


class VistaPiezas(VistaBase):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Módulo de Piezas", "Buscar por ID:", "piezas")
        self.crear_widgets()

    def crear_widgets(self):
        campos = ["ID", "Descripcion", "Marca", "Stock"]
        for i, campo in enumerate(campos):
            tk.Label(self.frame_formulario, text=campo+":").grid(row=i, column=0, pady=5, sticky="e")
            entry = tk.Entry(self.frame_formulario, width=30)
            entry.grid(row=i, column=1, pady=5)
            self.entradas[campo] = entry
        self.crear_botones()

    def accion_buscar(self):
        id_busqueda = self.entry_busqueda.get().strip()
        if not id_busqueda.isdigit(): return
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT pieza_id, descripcion, marca, stock FROM piezas WHERE pieza_id = %s", (id_busqueda,))
            resultado = cursor.fetchone()
            conexion.close()
            
            if resultado:
                self.rellenar_datos(["ID", "Descripcion", "Marca", "Stock"], resultado)
            else:
                messagebox.showinfo("Mensaje", "Pieza no encontrada")

    def accion_guardar(self):
        datos = [self.entradas[c].get().strip() for c in ["Descripcion", "Marca", "Stock"]]
        if "" in datos:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        try:
            stock = int(datos[2])
            if stock < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "El Stock debe ser un número entero positivo.")
            return

        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                if self.es_nuevo:
                    cursor.execute("INSERT INTO piezas (descripcion, marca, stock) VALUES (%s, %s, %s)", datos)
                    messagebox.showinfo("Exito", "Pieza guardada ok")
                else:
                    id_actual = self.entradas["ID"].get()
                    cursor.execute("UPDATE piezas SET descripcion=%s, marca=%s, stock=%s WHERE pieza_id=%s", (*datos, id_actual))
                    messagebox.showinfo("Exito", "Pieza actualizada ok")
                conexion.commit()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conexion.close()
        self.estado_inicial()

    def accion_remover(self):
        if self.es_nuevo: return
        id_actual = self.entradas["ID"].get()
        if not id_actual: return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta pieza?"):
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    cursor.execute("DELETE FROM piezas WHERE pieza_id = %s", (id_actual,))
                    conexion.commit()
                    messagebox.showinfo("Exito", "Pieza eliminada correctamente.")
                    self.estado_inicial()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                finally:
                    conexion.close()


class VistaReparaciones(VistaBase):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Módulo de Reparaciones", "Buscar Folio:", "reparaciones")
        self.crear_widgets()
        self.cargar_vehiculos()
        self.cargar_piezas()

    def crear_widgets(self):
        campos = ["Folio", "Fecha Entrada", "Fecha Salida", "Falla"]
        for i, campo in enumerate(campos):
            tk.Label(self.frame_formulario, text=campo+":").grid(row=i, column=0, pady=5, sticky="e")
            entry = tk.Entry(self.frame_formulario, width=30)
            entry.grid(row=i, column=1, pady=5)
            if campo == "Folio":
                self.entradas["ID"] = entry
            else:
                self.entradas[campo] = entry

        row_idx = len(campos)

        tk.Label(self.frame_formulario, text="Matrícula:").grid(row=row_idx, column=0, pady=5, sticky="e")
        self.combo_vehiculos = ttk.Combobox(self.frame_formulario, width=27, state="readonly")
        self.combo_vehiculos.grid(row=row_idx, column=1, pady=5)
        self.entradas["MatriculaVehiculo"] = self.combo_vehiculos
        row_idx += 1

        tk.Label(self.frame_formulario, text="Usuario:").grid(row=row_idx, column=0, pady=5, sticky="e")
        entry_user = tk.Entry(self.frame_formulario, width=30)
        entry_user.insert(0, f"{self.app.id_usuario} - {self.app.nombre_usuario}")
        entry_user.config(state="readonly") 
        entry_user.grid(row=row_idx, column=1, pady=5)
        self.entradas["Usuario (Atiende)"] = entry_user
        row_idx += 1

        tk.Label(self.frame_formulario, text="Pieza:").grid(row=row_idx, column=0, pady=5, sticky="e")
        self.combo_piezas = ttk.Combobox(self.frame_formulario, width=27, state="readonly")
        self.combo_piezas.grid(row=row_idx, column=1, pady=5)
        row_idx += 1

        tk.Label(self.frame_formulario, text="Cantidad:").grid(row=row_idx, column=0, pady=5, sticky="e")
        self.entry_cantidad = tk.Entry(self.frame_formulario, width=30)
        self.entry_cantidad.insert(0, "0") 
        self.entry_cantidad.grid(row=row_idx, column=1, pady=5)
        row_idx += 1

        frame_btn_detalle = tk.Frame(self.frame_formulario)
        frame_btn_detalle.grid(row=row_idx, column=1, sticky="e", pady=5)
        self.btn_agregar = tk.Button(frame_btn_detalle, text="Agregar", command=self.agregar_detalle)
        self.btn_agregar.pack(side="left", padx=2)
        self.btn_quitar = tk.Button(frame_btn_detalle, text="Quitar", command=self.quitar_detalle)
        self.btn_quitar.pack(side="left", padx=2)
        row_idx += 1

        self.tree_detalle = ttk.Treeview(self.frame_formulario, columns=("Folio", "PiezaID", "Descripcion", "Cantidad"), show="headings", height=5)
        self.tree_detalle.heading("Folio", text="Folio")
        self.tree_detalle.heading("PiezaID", text="Pieza ID")
        self.tree_detalle.heading("Descripcion", text="Descripción")
        self.tree_detalle.heading("Cantidad", text="Cant.")
        
        self.tree_detalle.column("Folio", width=60, anchor="center")
        self.tree_detalle.column("PiezaID", width=60, anchor="center")
        self.tree_detalle.column("Descripcion", width=180)
        self.tree_detalle.column("Cantidad", width=50, anchor="center")
        
        self.tree_detalle.grid(row=row_idx, column=0, columnspan=2, pady=10)

        self.crear_botones()

    def limpiar_campos(self):
        super().limpiar_campos()
        if hasattr(self, 'tree_detalle'):
            for item in self.tree_detalle.get_children():
                self.tree_detalle.delete(item)
            self.entry_cantidad.delete(0, tk.END)
            self.entry_cantidad.insert(0, "0")
            self.combo_piezas.set("")

    def alternar_campos(self, estado):
        super().alternar_campos(estado)
        estado_tk = "normal" if estado else "disabled"
        if hasattr(self, 'btn_agregar'):
            self.btn_agregar.config(state=estado_tk)
            self.btn_quitar.config(state=estado_tk)
            self.entry_cantidad.config(state=estado_tk)
            self.combo_piezas.config(state="readonly" if estado else "disabled")

    def cargar_vehiculos(self):
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT matricula FROM vehiculos")
            vehiculos = cursor.fetchall()
            self.combo_vehiculos['values'] = [v[0] for v in vehiculos]
            conexion.close()

    def cargar_piezas(self):
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT pieza_id, descripcion FROM piezas")
            piezas = cursor.fetchall()
            self.combo_piezas['values'] = [f"{p[0]} - {p[1]}" for p in piezas]
            conexion.close()

    def agregar_detalle(self):
        folio_actual = self.entradas["ID"].get()
        pieza_sel = self.combo_piezas.get()
        cant_str = self.entry_cantidad.get().strip()
        
        if not pieza_sel or not cant_str.isdigit() or int(cant_str) <= 0:
            messagebox.showwarning("Aviso", "Seleccione una pieza y escriba una cantidad válida.")
            return
            
        pieza_id, descripcion = pieza_sel.split(" - ", 1)
        self.tree_detalle.insert("", tk.END, values=(folio_actual, pieza_id, descripcion, cant_str))
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "0")
        self.combo_piezas.set("")

    def quitar_detalle(self):
        seleccion = self.tree_detalle.selection()
        if seleccion:
            self.tree_detalle.delete(seleccion[0])
        else:
            messagebox.showwarning("Aviso", "Seleccione una pieza de la tabla para quitar.")

    def accion_buscar(self):
        folio = self.entry_busqueda.get().strip()
        if not folio.isdigit(): return
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            query_maestro = """SELECT r.folio, r.fecha_entrada, r.fecha_salida, r.falla, r.matricula, 
                                      CONCAT(u.usuario_id, ' - ', u.nombre) 
                               FROM reparaciones r JOIN usuarios u ON r.usuario_id = u.usuario_id WHERE r.folio = %s"""
            cursor.execute(query_maestro, (folio,))
            resultado_maestro = cursor.fetchone()
            
            if resultado_maestro:
                self.entradas["Usuario (Atiende)"].config(state="normal")
                self.rellenar_datos(["ID", "Fecha Entrada", "Fecha Salida", "Falla", "MatriculaVehiculo", "Usuario (Atiende)"], resultado_maestro)
                self.entradas["Usuario (Atiende)"].config(state="readonly")
                
                for item in self.tree_detalle.get_children():
                    self.tree_detalle.delete(item)
                
                query_detalle = """SELECT d.folio, d.pieza_id, p.descripcion, d.cantidad 
                                   FROM det_reparaciones d 
                                   JOIN piezas p ON d.pieza_id = p.pieza_id WHERE d.folio = %s"""
                cursor.execute(query_detalle, (folio,))
                for det in cursor.fetchall():
                    self.tree_detalle.insert("", tk.END, values=(det[0], det[1], det[2], det[3]))
            else:
                messagebox.showinfo("Mensaje", "Folio no encontrado")
            conexion.close()

    def accion_guardar(self):
        datos = [self.entradas[c].get().strip() for c in ["Fecha Entrada", "Fecha Salida", "Falla", "MatriculaVehiculo"]]
        if "" in datos:
            messagebox.showwarning("Aviso", "Llene los datos principales de la reparación.")
            return

        try:
            f_entrada = datetime.strptime(datos[0], "%Y-%m-%d")
            f_salida = datetime.strptime(datos[1], "%Y-%m-%d")
            if f_salida < f_entrada:
                messagebox.showerror("Error", "La fecha de salida NO puede ser anterior a la fecha de entrada.")
                return
        except ValueError:
            messagebox.showwarning("Aviso", "Formato de fecha inválido. Utilice AAAA-MM-DD.")
            return

        conexion = conectar_db()
        if conexion:
            try:
                conexion.start_transaction()
                cursor = conexion.cursor()
                
                if self.es_nuevo:
                    cursor.execute("INSERT INTO reparaciones (fecha_entrada, fecha_salida, falla, matricula, usuario_id) VALUES (%s, %s, %s, %s, %s)", 
                                   (*datos, self.app.id_usuario))
                    folio_real = cursor.lastrowid
                else:
                    folio_real = self.entradas["ID"].get()
                    cursor.execute("SELECT pieza_id, cantidad FROM det_reparaciones WHERE folio = %s", (folio_real,))
                    for pid, cant in cursor.fetchall():
                        cursor.execute("UPDATE piezas SET stock = stock + %s WHERE pieza_id = %s", (cant, pid))
                        
                    cursor.execute("DELETE FROM det_reparaciones WHERE folio = %s", (folio_real,))
                    cursor.execute("UPDATE reparaciones SET fecha_entrada=%s, fecha_salida=%s, falla=%s, matricula=%s WHERE folio=%s", 
                                   (*datos, folio_real))

                for child in self.tree_detalle.get_children():
                    fol_visual, pid, desc, cant = self.tree_detalle.item(child, 'values')
                    cant = int(cant)
                    
                    cursor.execute("SELECT stock FROM piezas WHERE pieza_id = %s", (pid,))
                    stock_actual = cursor.fetchone()[0]
                    if stock_actual < cant:
                        raise ValueError(f"No hay stock suficiente para la pieza: {desc}. Quedan {stock_actual}.")
                        
                    cursor.execute("INSERT INTO det_reparaciones (folio, pieza_id, cantidad) VALUES (%s, %s, %s)", (folio_real, pid, cant))
                    cursor.execute("UPDATE piezas SET stock = stock - %s WHERE pieza_id = %s", (cant, pid))
                
                conexion.commit()
                messagebox.showinfo("Exito", "Reparación y piezas guardadas correctamente.")
            except ValueError as ve:
                conexion.rollback()
                messagebox.showerror("Sin Stock", str(ve))
            except Exception as e:
                conexion.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conexion.close()
        self.estado_inicial()

    def accion_remover(self):
        if self.es_nuevo: return
        id_actual = self.entradas["ID"].get()
        if not id_actual: return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar esta reparación?\n\nLas piezas utilizadas se devolverán al inventario."):
            conexion = conectar_db()
            if conexion:
                try:
                    conexion.start_transaction()
                    cursor = conexion.cursor()
                    
                    cursor.execute("SELECT pieza_id, cantidad FROM det_reparaciones WHERE folio = %s", (id_actual,))
                    for pid, cant in cursor.fetchall():
                        cursor.execute("UPDATE piezas SET stock = stock + %s WHERE pieza_id = %s", (cant, pid))

                    cursor.execute("DELETE FROM reparaciones WHERE folio = %s", (id_actual,))
                    conexion.commit()
                    messagebox.showinfo("Exito", "Reparación eliminada y piezas devueltas al inventario.")
                    self.estado_inicial() 
                except Exception as e:
                    conexion.rollback()
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                finally:
                    conexion.close()

class AplicacionPrincipal(tk.Tk):
    def __init__(self, id_usuario, perfil_usuario, nombre_usuario):
        super().__init__()
        self.id_usuario = id_usuario
        self.perfil_usuario = perfil_usuario
        self.nombre_usuario = nombre_usuario
        
        self.title(f"Sistema - {nombre_usuario}")
        self.geometry("500x750") 
        
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)
        self.vista_actual = None
        self.crear_menu()
        
        tk.Label(self.contenedor, text="Elija una opcion del menu").pack(pady=50)

    def crear_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)
        
        menu_modulos = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Modulos", menu=menu_modulos)

        if self.perfil_usuario == "Administrador":
            menu_modulos.add_command(label="Usuarios", command=lambda: self.mostrar_vista(VistaUsuarios))
            menu_modulos.add_command(label="Clientes", command=lambda: self.mostrar_vista(VistaClientes))
            menu_modulos.add_command(label="Vehiculos", command=lambda: self.mostrar_vista(VistaVehiculos))
            menu_modulos.add_command(label="Reparaciones", command=lambda: self.mostrar_vista(VistaReparaciones))
            menu_modulos.add_command(label="Piezas", command=lambda: self.mostrar_vista(VistaPiezas))
        elif self.perfil_usuario == "Mecanico":
            menu_modulos.add_command(label="Vehiculos", command=lambda: self.mostrar_vista(VistaVehiculos))
            menu_modulos.add_command(label="Reparaciones", command=lambda: self.mostrar_vista(VistaReparaciones))
            menu_modulos.add_command(label="Piezas", command=lambda: self.mostrar_vista(VistaPiezas))
        elif self.perfil_usuario == "Auxiliar":
            menu_modulos.add_command(label="Clientes", command=lambda: self.mostrar_vista(VistaClientes))
            menu_modulos.add_command(label="Vehiculos", command=lambda: self.mostrar_vista(VistaVehiculos))
            menu_modulos.add_command(label="Piezas", command=lambda: self.mostrar_vista(VistaPiezas))

        menu_modulos.add_separator()
        menu_modulos.add_command(label="Salir", command=self.cerrar_sesion)

    def mostrar_vista(self, clase_vista):
        if self.vista_actual:
            self.vista_actual.destroy()
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.vista_actual = clase_vista(self.contenedor, self)
        self.vista_actual.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.destroy()
        Login().mainloop()

class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("250x200")

        tk.Label(self, text="Login de Acceso").pack(pady=10)
        
        tk.Label(self, text="User:").pack()
        self.txt_user = tk.Entry(self)
        self.txt_user.pack()
        
        tk.Label(self, text="Pass:").pack()
        self.txt_pass = tk.Entry(self, show="*")
        self.txt_pass.pack()
        
        tk.Button(self, text="Entrar", command=self.verificar_login).pack(pady=15)

    def verificar_login(self):
        user = self.txt_user.get()
        pwd = self.txt_pass.get()
        
        if not user or not pwd:
            messagebox.showwarning("Aviso", "Por favor llene ambos campos.")
            return

        pwd_encriptada = encriptar_password(pwd)
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT usuario_id, perfil, nombre FROM usuarios WHERE username = %s AND password = %s", (user, pwd_encriptada))
            resultado = cursor.fetchone()
            conexion.close()
            if resultado:
                id_usuario, perfil, nombre = resultado
                self.destroy()
                app = AplicacionPrincipal(id_usuario, perfil, nombre)
                app.mainloop()
            else:
                messagebox.showerror("Error", "Datos erroneos")

if __name__ == "__main__":
    Login().mainloop()