import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

###----------Configuración de la conexión a PostgreSQL----------###
def conectar_db():
    try:
        conexion = psycopg2.connect(
            dbname="personas_db",
            user="postgres",  
            password="1234",  
            host="localhost",
            port="5432"
        )
        return conexion
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
        return None

###----------creacion de la tabla si no existe----------###
def crear_tabla():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    edad INTEGER NOT NULL,
                    fecha_nacimiento DATE NOT NULL,
                    genero VARCHAR(50) NOT NULL,
                    profesion VARCHAR(100) NOT NULL
                )
            ''')
            conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla: {e}")
        finally:
            conexion.close()

###----------Guardar una persona en la base de datos----------###
def guardar_persona(nombre, apellido, edad, fecha_nacimiento, genero, profesion):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO personas (nombre, apellido, edad, fecha_nacimiento, genero, profesion)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombre, apellido, edad, fecha_nacimiento, genero, profesion))
            conexion.commit()
            messagebox.showinfo("Éxito", "Los datos fueron guardados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {e}")
        finally:
            conexion.close()

###----------Actualizar persona----------###
def actualizar_persona(id, nombre, apellido, edad, fecha_nacimiento, genero, profesion):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('''
                UPDATE personas
                SET nombre = %s, apellido = %s, edad = %s, fecha_nacimiento = %s, genero = %s, profesion = %s
                WHERE id = %s
            ''', (nombre, apellido, edad, fecha_nacimiento, genero, profesion, id))
            conexion.commit()
            messagebox.showinfo("Éxito", "Los datos fueron actualizados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron actualizar los datos: {e}")
        finally:
            conexion.close()

###----------Obtener todas las personas de la base de datos----------###
def obtener_personas():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM personas')
            personas = cursor.fetchall()
            return personas
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {e}")
            return []
        finally:
            conexion.close()
    return []

###----------Obtener personas mayores de edad----------###
def obtener_mayores_de_edad():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM personas WHERE edad >= 18')
            personas = cursor.fetchall()
            return personas
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {e}")
            return []
        finally:
            conexion.close()
    return []

###----------Obtener personas por nombre, apellido, edad, genero----------###
def obtener_dato(dato, tipo):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            if tipo == "nombre":
                cursor.execute('SELECT * FROM personas WHERE nombre ILIKE %s', (f'%{dato}%',))
            elif tipo == "apellido":
                cursor.execute('SELECT * FROM personas WHERE apellido ILIKE %s', (f'%{dato}%',))
            elif tipo == "edad":
                try:
                    edad = int(dato)  # Validar que la edad sea un número
                    cursor.execute('SELECT * FROM personas WHERE edad = %s', (edad,))
                except ValueError:
                    messagebox.showwarning("Error", "La edad debe ser un número válido.")
                    return []
            elif tipo == "genero":
                cursor.execute('SELECT * FROM personas WHERE genero ILIKE %s', (f'%{dato}%',))
            else:
                messagebox.showwarning("Error", "Tipo de filtro no válido.")
                return []
            personas = cursor.fetchall()
            return personas
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {e}")
            return []
        finally:
            conexion.close()
    return []

###----------Eliminar persona por ID----------###
def eliminar_persona(id):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('DELETE FROM personas WHERE id = %s', (id,))
            conexion.commit()
            messagebox.showinfo("Éxito", "Persona eliminada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la persona: {e}")
        finally:
            conexion.close()

###----------Actualizar persona en la interfaz----------###
def actualizar_tabla(personas=None):
    for row in tabla.get_children():
        tabla.delete(row)
    if personas is None:
        personas = obtener_personas()
    for persona in personas:
        tabla.insert("", tk.END, values=persona)

###----------Función para enviar el formulario (guardar o actualizar)----------###
def enviar_formulario():
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    edad = entry_edad.get()
    fecha_nacimiento = entry_fecha_nacimiento.get()
    genero = entry_genero.get()
    profesion = entry_profesion.get()

    if nombre and apellido and edad and fecha_nacimiento and genero and profesion:
        try:
            edad = int(edad)  # Validar que la edad sea un número
            if id_actual:  # Si hay un ID actual, actualizar el registro
                actualizar_persona(id_actual, nombre, apellido, edad, fecha_nacimiento, genero, profesion)
            else:  # Si no hay un ID actual, guardar un nuevo registro
                guardar_persona(nombre, apellido, edad, fecha_nacimiento, genero, profesion)
            # Limpiar los campos después de guardar o actualizar
            limpiar_formulario()
            actualizar_tabla()  # Actualizar la tabla con los nuevos datos
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número válido.")
    else:
        messagebox.showwarning("Error", "Todos los campos son obligatorios.")

###----------Obtener los datos de una persona en el formulario----------###
def cargar_datos_seleccionados(event):
    seleccionado = tabla.selection()
    if seleccionado:
        global id_actual
        datos = tabla.item(seleccionado)["values"]
        id_actual = datos[0]  # Guardar el ID actual
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, datos[1])
        entry_apellido.delete(0, tk.END)
        entry_apellido.insert(0, datos[2])
        entry_edad.delete(0, tk.END)
        entry_edad.insert(0, datos[3])
        entry_fecha_nacimiento.delete(0, tk.END)
        entry_fecha_nacimiento.insert(0, datos[4])
        entry_genero.delete(0, tk.END)
        entry_genero.insert(0, datos[5])
        entry_profesion.delete(0, tk.END)
        entry_profesion.insert(0, datos[6])

###----------Se limpia el formulario----------###
def limpiar_formulario():
    global id_actual
    id_actual = None
    entry_nombre.delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_edad.delete(0, tk.END)
    entry_fecha_nacimiento.delete(0, tk.END)
    entry_genero.delete(0, tk.END)
    entry_profesion.delete(0, tk.END)

###----------Elimina persona selecionada----------###
def eliminar_persona_seleccionada():
    seleccionado = tabla.selection()
    if seleccionado:
        id_persona = tabla.item(seleccionado)["values"][0]
        eliminar_persona(id_persona)
        actualizar_tabla()
    else:
        messagebox.showwarning("Error", "Selecciona una persona para eliminar.")

###----------Muestra los mayores de edad----------###
def mostrar_mayores_de_edad():
    mayores = obtener_mayores_de_edad()
    actualizar_tabla(mayores)

###----------Habilita y deshabilita el boton de buscar----------###
def validar_busqueda(*args):
    dato = entry_buscar_dato.get()
    tipo = tipo_filtro.get()
    if dato and tipo:
        boton_buscar.config(state=tk.NORMAL)
    else:
        boton_buscar.config(state=tk.DISABLED)

###----------Busca por dato y actualiza la tabla----------###
def buscar_por_dato():
    dato = entry_buscar_dato.get()  # Obtener el dato del campo de entrada
    tipo = tipo_filtro.get()  # Obtener el tipo de filtro seleccionado
    if dato and tipo:
        personas = obtener_dato(dato, tipo)
        actualizar_tabla(personas)
    else:
        messagebox.showwarning("Error", "Ingresa un dato y selecciona un tipo de filtro.")

###------Interfaz Gráfica------###

ventana = tk.Tk()
ventana.title("Formulario de Registro de Personas")
ventana.geometry("1080x600")

# Variable global para almacenar el ID actual (para edición)
id_actual = None

# Frame para el formulario (izquierda)
frame_formulario = tk.Frame(ventana)
frame_formulario.grid(row=0, column=0, padx=10, pady=10, sticky="n")

# Campos del formulario
tk.Label(frame_formulario, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nombre = tk.Entry(frame_formulario, width=30)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Apellido:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_apellido = tk.Entry(frame_formulario, width=30)
entry_apellido.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Edad:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_edad = tk.Entry(frame_formulario, width=30)
entry_edad.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="F.Nacimiento:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_fecha_nacimiento = tk.Entry(frame_formulario, width=30)
entry_fecha_nacimiento.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Género:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
entry_genero = tk.Entry(frame_formulario, width=30)
entry_genero.grid(row=4, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Profesión:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
entry_profesion = tk.Entry(frame_formulario, width=30)
entry_profesion.grid(row=5, column=1, padx=5, pady=5)

# Botón para guardar o actualizar
tk.Button(frame_formulario, text="Guardar", command=enviar_formulario).grid(row=6, column=0, pady=10)

# Botón para eliminar persona seleccionada
tk.Button(frame_formulario, text="Eliminar Seleccionado", command=eliminar_persona_seleccionada).grid(row=6, column=1, pady=10)

# Botón para mostrar mayores de edad
tk.Button(frame_formulario, text="Mostrar Mayores de Edad", command=mostrar_mayores_de_edad).grid(row=7, column=0, columnspan=2, pady=10)

# Menu para seleccionar el tipo de filtro
tk.Label(frame_formulario, text="Tipo de Filtro:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
tipo_filtro = tk.StringVar(value="nombre")  # Valor por defaul: nombre
opciones_filtro = ["nombre", "apellido", "edad","genero"]
menu_filtro = tk.OptionMenu(frame_formulario, tipo_filtro, *opciones_filtro, command=lambda _: validar_busqueda())
menu_filtro.grid(row=8, column=1, padx=5, pady=5)

# Campo de entrada para el dato a buscar
tk.Label(frame_formulario, text="Dato a Buscar:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
entry_buscar_dato = tk.Entry(frame_formulario, width=30)
entry_buscar_dato.grid(row=9, column=1, padx=5, pady=5)
entry_buscar_dato.bind("<KeyRelease>", validar_busqueda)

# Botón para buscar
boton_buscar = tk.Button(frame_formulario, text="Buscar", command=buscar_por_dato, state=tk.DISABLED)
boton_buscar.grid(row=10, column=0, columnspan=2, pady=10)


# Botón para buscar
boton_buscar = tk.Button(frame_formulario, text="Buscar", command=buscar_por_dato, state=tk.DISABLED)
boton_buscar.grid(row=10, column=0, columnspan=2, pady=10)

# Frame para la tabla (derecha)
frame_tabla = tk.Frame(ventana)
frame_tabla.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Tabla para mostrar los datos
columnas = ("ID", "Nombre", "Apellido", "Edad", "Fecha Nacimiento", "Género", "Profesión")
tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100)
tabla.pack(fill=tk.BOTH, expand=True)

# Evento para cargar datos al hacer clic en una fila
tabla.bind("<ButtonRelease-1>", cargar_datos_seleccionados)

# Crear la tabla al iniciar la aplicación
crear_tabla()
actualizar_tabla()  # Mostrar los datos al iniciar

# Iniciar la aplicación
ventana.mainloop()