from flet import *
import flet
import mysql.connector
import threading

# Conexión a la base de datos de clientes
conexion_bd = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    db="appClientes"  # Nombre de la base de datos
)

# Crear cursor para interactuar con la base de datos
cursor_bd = conexion_bd.cursor()


def main(page: Page):
    # Configuraciones generales de la página
    page.padding = 30
    page.title = "Gestión de Clientes"

    # Título principal de la aplicación
    titulo_principal = Text("Sistema de Gestión de Clientes", size=26, weight="bold")

    # Label para mensajes de validación o notificación
    lbl_mensaje = Text("", size=12, color="blue")

    # Sección de ingreso de datos del cliente
    titulo_ingreso = Text("Ingreso de Datos del Cliente", size=20, weight="bold")

    # Inputs para ingresar datos de un cliente nuevo
    txt_nombre = TextField(label="Nombre del Cliente", width=250)
    txt_direccion = TextField(label="Dirección", width=250)
    txt_email = TextField(label="Correo Electrónico", width=250)
    txt_telefono = TextField(label="Teléfono", keyboard_type="number", width=250)

    # Inputs para editar datos de un cliente existente
    txt_edit_nombre = TextField(label="Nombre del Cliente", width=250)
    txt_edit_direccion = TextField(label="Dirección", width=250)
    txt_edit_email = TextField(label="Correo Electrónico", width=250)
    txt_edit_telefono = TextField(label="Teléfono", keyboard_type="number", width=250)
    txt_edit_id = Text()  # Campo oculto para almacenar el ID del cliente a editar

    # Tabla para mostrar la lista de clientes
    titulo_listado = Text("Listado de Clientes", size=20, weight="bold")
    tabla_clientes = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre")),
            DataColumn(Text("Dirección")),
            DataColumn(Text("Correo Electrónico")),
            DataColumn(Text("Teléfono")),
            DataColumn(Text("Acciones"))  # Columna para los botones de acciones (eliminar y editar)
        ],
        rows=[]
    )

    # Función para cargar los datos de clientes desde la base de datos y mostrarlos en la tabla
    def cargar_clientes():
        cursor_bd.execute("SELECT * FROM clientes")
        resultados = cursor_bd.fetchall()
        columnas = [columna[0] for columna in cursor_bd.description]
        filas = [dict(zip(columnas, fila)) for fila in resultados]

        tabla_clientes.rows.clear()
        for fila in filas:
            # Agrega cada cliente como una fila en la tabla
            tabla_clientes.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(str(fila['idcliente']))),
                        DataCell(Text(fila['cli_nombre'])),
                        DataCell(Text(fila['cli_direccion'])),
                        DataCell(Text(fila['cli_email'])),
                        DataCell(Text(fila['cli_telefono'])),
                        DataCell(
                            Row([  # Botones de eliminar y editar
                                IconButton("delete", icon_color="red", data=fila, on_click=eliminar_cliente),
                                IconButton("edit", icon_color="red", data=fila, on_click=lambda e: abrir_modal_editar(e))
                            ])
                        )
                    ]
                )
            )

        page.update()  # Actualiza la página para reflejar cambios en la tabla

    # Función para mostrar un mensaje temporal en la aplicación
    def mostrar_mensaje(mensaje, color="blue"):
        lbl_mensaje.value = mensaje
        lbl_mensaje.color = color
        page.update()
        threading.Timer(2, limpiar_mensaje).start()  # Limpia el mensaje después de 2 segundos

    # Función para limpiar el mensaje
    def limpiar_mensaje():
        lbl_mensaje.value = ""
        page.update()

    # Función para eliminar un cliente de la base de datos
    def eliminar_cliente(e):
        sql = "DELETE FROM clientes WHERE idcliente = %s"
        val = (e.control.data['idcliente'],)
        cursor_bd.execute(sql, val)
        conexion_bd.commit()
        cargar_clientes()  # Recargar la tabla después de eliminar el cliente
        mostrar_mensaje("Cliente eliminado exitosamente.", "blue")

    # Función para guardar cambios después de editar los datos de un cliente
    def guardar_edicion(e):
        # Validaciones para asegurar que los campos requeridos no estén vacíos
        if not txt_edit_nombre.value:
            mostrar_mensaje("Especifique un nombre para el cliente.", "blue")
            return
        if not txt_edit_direccion.value:
            mostrar_mensaje("Añada una dirección válida.", "blue")
            return
        if not txt_edit_email.value:
            mostrar_mensaje("Ingrese un correo electrónico válido.", "blue")
            return
        if not txt_edit_telefono.value:
            mostrar_mensaje("El número de teléfono no puede estar vacío.", "blue")
            return

        # Actualiza los datos del cliente en la base de datos
        sql = "UPDATE clientes SET cli_nombre=%s, cli_direccion=%s, cli_email=%s, cli_telefono=%s WHERE idcliente=%s"
        val = (txt_edit_nombre.value, txt_edit_direccion.value, txt_edit_email.value, txt_edit_telefono.value, txt_edit_id.value)
        cursor_bd.execute(sql, val)
        conexion_bd.commit()
        cargar_clientes()  # Recarga la tabla después de la edición
        modal_editar.open = False  # Cierra el modal de edición
        mostrar_mensaje("Datos del cliente actualizados correctamente.", "blue")

    # Modal para editar datos de un cliente
    modal_editar = AlertDialog(
        title=Text("Modificar Cliente"),
        content=Column([
            txt_edit_nombre,
            txt_edit_direccion,
            txt_edit_email,
            txt_edit_telefono
        ]),
        actions=[TextButton("Guardar", on_click=guardar_edicion)]  # Botón para guardar cambios
    )

    # Función para abrir el modal de edición con los datos del cliente seleccionado
    def abrir_modal_editar(e):
        txt_edit_nombre.value = e.control.data['cli_nombre']
        txt_edit_direccion.value = e.control.data['cli_direccion']
        txt_edit_email.value = e.control.data['cli_email']
        txt_edit_telefono.value = e.control.data['cli_telefono']
        txt_edit_id.value = e.control.data['idcliente']  # Almacena el ID del cliente que se está editando
        page.dialog = modal_editar
        modal_editar.open = True
        page.update()

    # Función para añadir un nuevo cliente a la base de datos
    def agregar_cliente(e):
        # Validaciones para asegurar que los campos requeridos no estén vacíos
        if not txt_nombre.value:
            mostrar_mensaje("Ingrese el nombre del cliente.", "blue")
            return
        if not txt_direccion.value:
            mostrar_mensaje("Añada una dirección.", "blue")
            return
        if not txt_email.value:
            mostrar_mensaje("Introduzca un correo electrónico válido.", "blue")
            return
        if not txt_telefono.value:
            mostrar_mensaje("Especifique el número de teléfono.", "blue")
            return

        # Inserta un nuevo cliente en la base de datos
        sql = "INSERT INTO clientes (cli_nombre, cli_direccion, cli_email, cli_telefono) VALUES (%s, %s, %s, %s)"
        val = (txt_nombre.value, txt_direccion.value, txt_email.value, txt_telefono.value)
        cursor_bd.execute(sql, val)
        conexion_bd.commit()
        cargar_clientes()  # Recarga la tabla después de agregar el cliente
        mostrar_mensaje("Cliente añadido exitosamente.", "blue")
        txt_nombre.value = txt_direccion.value = txt_email.value = txt_telefono.value = ""  # Limpia los campos
        page.update()

    cargar_clientes()  # Llama a la función para cargar clientes al iniciar la aplicación

    # Diseño de la página con ingreso de datos y listado de clientes en columnas
    page.add(
        Column([
            titulo_principal,
            lbl_mensaje,
            Row([
                Column([
                    titulo_ingreso,
                    txt_nombre,
                    txt_direccion,
                    txt_email,
                    txt_telefono,
                    ElevatedButton("Agregar Cliente", on_click=agregar_cliente)  # Botón para agregar cliente
                ], width=300),
                VerticalDivider(),
                Column([
                    titulo_listado,
                    tabla_clientes 
                ])
            ])
        ])
    )

flet.app(target=main)
