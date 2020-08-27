from tkinter import *
import pyodbc
import tkinter.messagebox
from tkinter import font


def conexion_bd():
	global cursor
	global conexion
	try:
		conexion = pyodbc.connect(
			driver='{SQL Server}',
			server='LUISENRIQUE-PC\SQLEXPRESS',
			database='proyecto_agenda',
			uid='',
			pwd='')
	
	except:
		tkinter.messagebox.showinfo("ERROR", "ERROR \nNo se puede conectar a la base de datos")
	else:
		cursor = conexion.cursor()
		cursor.execute("USE proyecto_agenda")


def guardar_contacto():
	global _click
	try:
		conexion_bd()
		if _click == 1:
			nombre = txt_nombre.get()
			email = txt_email.get()
			telefono = txt_telefono.get()
			if nombre!="" and email!="" and telefono!="":
				cat = "SELECT * FROM categoria WHERE id_usuario = "+str(_id_user)+" "
				cursor.execute(cat)
				verificar = cursor.fetchone()#si no hay una categoria manda un mensaje
				validarCorreo = validar_correo_contacto(email)#valida si algun contacto tiene el mismo correo
				validarTelefono = validar_telefono_contacto(telefono)

				if verificar == None:
					tkinter.messagebox.showinfo("info","Selecciona una categoria o crea \nuna categoría para tu lista de contactos")
				if validarCorreo!=None:
					tkinter.messagebox.showinfo("info","El contacto ["+validarCorreo[0]+"] ya tiene el correo ["+validarCorreo[1]+"]")
					txt_email.set("")
				elif validarTelefono!=None:
					tkinter.messagebox.showinfo("info","El contacto ["+validarTelefono[0]+"] ya tiene el teléfono ["+validarTelefono[1]+"]")
					txt_telefono.set("")
				else:
					cursor.execute("SELECT * FROM contacto")
					filas = cursor.fetchall()
					for num in filas:
						indice = num[0]

					id_contacto = indice + 1
					id_catSelct = categoria_seleccionada()

					nuevoContacto = """INSERT INTO contacto (id,nombre,correo,numero_tel,id_usuariof,id_categoria) 
					values("""+str(id_contacto)+""",'"""+nombre.strip(" ")+"""','"""+email.strip(" ")+"""','"""+telefono.strip(" ")+"""',
					"""+str(_id_user)+""","""+str(id_catSelct)+""");"""
					cursor.execute(nuevoContacto)
					txt_nombre.set("")
					txt_email.set("")
					txt_telefono.set("")
					tkinter.messagebox.showinfo("info","se ha guardado satisfactoriamente")
			else:
				tkinter.messagebox.showerror("ERROR","ERROR \nNo dejar espacios vacios")
		if _click == 2:
			nombre = txt_nombre.get()
			email = txt_email.get()
			telefono = txt_telefono.get()
			queryModificar = """UPDATE contacto 
			SET nombre = '"""+nombre+"""', correo = '"""+email+"""', numero_tel = '"""+telefono+"""' 
			WHERE id="""+str(_id_contacto)+""" and id_usuariof =  """+str(_id_user)+""" """
			cursor.execute(queryModificar)

			txt_nombre.set("")
			txt_email.set("")
			txt_telefono.set("")

			ListaContactos.delete(_item)
			ListaContactos.insert(_item,"Nombre-->"+nombre+"......Correo-->"+email+"......Teléfono-->"+telefono)
			_click = 1 
		conexion.commit()
		conexion.close()
	except Exception as e:
		print(e)
		tkinter.messagebox.showerror("error","ERROR al querer guardar el contacto")


def categoria_seleccionada():
	global id_cat
	cat = "SELECT * FROM categoria WHERE id_usuario = "+str(_id_user)+" "
	cursor.execute(cat)
	filas = cursor.fetchall()
	for i in filas:
		if categorias.get() == i[1]:
			id_cat = i[0]
			print(categorias.get()+"--"+str(i[0])+i[1]+str(i[2]))
	return id_cat


def mostrar():
	ListaContactos.delete(0,END)
	ListaContactos.insert(0,"        Lista de contactos")
	conexion_bd()
	cont = 1
	cursor.execute("SELECT nombre, correo, numero_tel from contacto where id_usuariof = "+str(_id_user))
	filas = cursor.fetchall()
	for fila in filas:
		ListaContactos.insert(cont,"Nombre-->"+fila[0]+"......Correo-->"+fila[1]+"......Teléfono-->"+fila[2])
		cont+=1
	conexion.commit()
	conexion.close()


def eliminar():
	try:
		conexion_bd()
		indice_item = ListaContactos.curselection()
		for item in indice_item:
			fila = ListaContactos.get(item)

		seleccion1 = fila.find("categoría:")
		seleccion2 = fila.find("Nombre")
		seleccion3 = fila.find("Lista de contactos")
		if seleccion1!=-1:
			if tkinter.messagebox.askokcancel("Mensaje","Se eliminara la categoría incluyendo todos los contactos \ncontenidos en ella"):
				eliminar = seleccion_de_contacto(fila,"categoria")
				print(eliminar[0])
				queryEliminar = "DELETE FROM categoria WHERE id = "+str(eliminar[0])+" and id_usuario = "+str(_id_user)
				cursor.execute(queryEliminar)
				ListaContactos.delete(0,END)
		elif seleccion2!=-1:
			if tkinter.messagebox.askyesno("Mensaje","Realmente desea eliminar este contacto?"):
				eliminar = seleccion_de_contacto(fila,"contacto")
				print(eliminar[0])
				queryEliminar = "DELETE FROM contacto WHERE id = "+str(eliminar[0])+" and id_usuariof = "+str(_id_user)
				cursor.execute(queryEliminar)
				ListaContactos.delete(item)
		elif seleccion3!=-1:
			tkinter.messagebox.showerror("ERROR","ERROR \nNo valido")
		txt_nombre.set("")
		txt_email.set("")
		txt_telefono.set("")
		conexion.commit()
		conexion.close()
	except:
		tkinter.messagebox.showerror("ERROR","ERROR al querer eliminar una categoría o contacto")


def seleccion_de_contacto(fila,selecciono):
	if selecciono == "categoria":
		lista = fila.split(":")
		nombre = lista[1]
		query = "SELECT * from categoria where nombre = '"+nombre.strip(" ")+"' and id_usuario = "+str(_id_user)
		cursor.execute(query)
		Categoria = cursor.fetchone()
		return Categoria
	elif selecciono == "contacto":
		lista = fila.split("......")#convierte en una lista apartir del caracter seleccionado
		nombre = lista[0].replace("Nombre-->","")#elimina el caracter no deseado en la cadena
		email = lista[1].replace("Correo-->","")
		telefono = lista[2].replace("Teléfono-->","")
		query = "SELECT * from contacto where nombre='"+nombre+"' and correo='"+email+"' and numero_tel='"+telefono+"' and id_usuariof="+str(_id_user)
		cursor.execute(query)
		Contacto = cursor.fetchone()
		return Contacto
	

def buscar():
	global _id_user
	try:
		conexion_bd()
		b_por = busqueda.get()
		if b_por == "Nombre":
			if txt_nombre.get()=="":
				tkinter.messagebox.showinfo("info","El campo Nombre esta vacio")
			else:
				queryBuscar = "SELECT * from contacto where nombre LIKE '%"+txt_nombre.get()+"%' and id_usuariof = "+str(_id_user)
				cursor.execute(queryBuscar)
				filas = cursor.fetchall()
				if filas:
					ListaContactos.delete(0,END)
					cont=0
					for fila in filas:
						ListaContactos.insert(cont,"Nombre-->"+fila[1]+"......Correo-->"+fila[2]+"......Teléfono-->"+fila[3])
						cont+=1
					txt_nombre.set("")
				else:
					tkinter.messagebox.showinfo("info","No se encontraron los valores ingresados")

		elif b_por == "Email":
			if txt_email.get()=="":
				tkinter.messagebox.showinfo("info","El campo Email esta vacio")
			else:
				queryBuscar = "SELECT * from contacto where correo LIKE '%"+txt_email.get()+"%' and id_usuariof = "+str(_id_user)
				cursor.execute(queryBuscar)
				filas = cursor.fetchall()
				if filas:
					ListaContactos.delete(0,END)
					cont=0
					for fila in filas:
						ListaContactos.insert(cont,"Nombre-->"+fila[1]+"......Correo-->"+fila[2]+"......Teléfono-->"+fila[3])
						cont+=1
					txt_nombre.set("")
				else:
					tkinter.messagebox.showinfo("info","No se encontraron los valores ingresados")

		elif b_por == "Teléfono":
			if txt_telefono.get()=="":
				tkinter.messagebox.showinfo("info","El campo Teléfono esta vacio")
			else:
				queryBuscar = "SELECT * from contacto where numero_tel LIKE '%"+txt_telefono.get()+"%' and id_usuariof = "+str(_id_user)
				cursor.execute(queryBuscar)
				filas = cursor.fetchall()
				if filas:
					ListaContactos.delete(0,END)
					cont=0
					for fila in filas:
						ListaContactos.insert(cont,"Nombre-->"+fila[1]+"......Correo-->"+fila[2]+"......Teléfono-->"+fila[3])
						cont+=1
					txt_nombre.set("")
				else:
					tkinter.messagebox.showinfo("info","No se encontraron los valores ingresados")
		conexion.close()

	except Exception as e:
		print(e)
		tkinter.messagebox.showerror("ERROR","ERROR \nNo puede realizarse la busqueda deseada")

	

def crear_categoria():
	nuevaCategoria = txt_crear_categoria.get()
	conexion_bd()
	id_cat = asignar_id_categoria()
	print(id_cat)
	cursor.execute("SELECT nombre FROM categoria where id_usuario = "+str(_id_user)+" AND nombre LIKE '%"+nuevaCategoria+"%'")
	verificar = cursor.fetchone()
	if verificar == None:
		queryCat = """INSERT INTO categoria 
		(id,nombre,id_usuario)
		values("""+str(id_cat)+""",'"""+nuevaCategoria+"""',"""+str(_id_user)+""");"""
		cursor.execute(queryCat)
		txt_crear_categoria.set("")
		tkinter.messagebox.showinfo("info","La categoría ["+nuevaCategoria+"] se ha guardado correctamente")
	else:
		tkinter.messagebox.showinfo("info","Esta lista ya existe")
	conexion.commit()
	conexion.close()
	

#muestra la lista de las categorias creadas por el usuario
def cargar_categorias():
	try:
		conexion_bd()
		cat = "SELECT * FROM categoria WHERE id_usuario = "+str(_id_user)+" "
		cursor.execute(cat)
		verificar = cursor.fetchone()
		print(verificar)
		if verificar == None:
			tkinter.messagebox.showinfo("info","Aun no tienes ninguna categoría")
		else:
			lista = []
			cat = "SELECT * FROM categoria WHERE id_usuario = "+str(_id_user)+" "
			cursor.execute(cat)
			filas = cursor.fetchall()
			for i in filas:
				lista.append(i[1])
				print(str(i[0])+i[1]+str(i[2]))
			_Categorias = tuple(lista)
			print(_Categorias)
			spinCategorias = Spinbox(v_principal,textvariable=categorias,values=_Categorias,font="Calibri",
			state='readonly',width=12).place(x=160,y=385)
		conexion.close()
	except:
		tkinter.messagebox.showinfo("ERROR","ERROR al mostrar categorias")


def mostrar_categoria():
	global _id_categoria
	try:
		ListaContactos.delete(0,END)
		selecciono_cat = categorias.get()
		conexion_bd()
		cursor.execute("select * from categoria where id_usuario = "+str(_id_user)+" ")
		filas = cursor.fetchall()
		for fila in filas:
			if selecciono_cat == fila[1]:
				print("cat-->"+selecciono_cat+"="+fila[1]+"-"+str(fila[0]))
				_id_categoria = fila[0]
			
		#mostrar los contactos de de la categoria seleccionada 
		cont = 1
		queryCont = "select id, nombre, correo, numero_tel from contacto con where id_usuariof = "+str(_id_user)+" and id_categoria = "+str(_id_categoria)+" "
		cursor.execute(queryCont)
		filas = cursor.fetchall()
		ListaContactos.insert(0,"Lista de la categoría: "+selecciono_cat)
		for fila in filas:
			ListaContactos.insert(cont,"Nombre-->"+fila[1]+"......Correo-->"+fila[2]+"......Teléfono-->"+fila[3])
			cont+=1
		#ListaContactos.insert(1,categorias.get())
		conexion.close()
	except Exception as e:
		tkinter.messagebox.showerror("ERROR","ERROR \nNo se puede mostrar la lista de categorías")


#funciones de validacion de usuario
def validar_usuario():
	global _id_user
	global _click
	compUsuario = usuario.get()
	compPasswd = password.get() 
	_click = 1
	if compUsuario=="" or compPasswd=="":
		tkinter.messagebox.showwarning("info","No dejar espacios vacios")
	else:
		encontrado = False
		conexion_bd()
		cursor.execute('SELECT * FROM usuario')
		filas = cursor.fetchall()
		for i in filas:
			if compUsuario==i[2] and compPasswd==i[3]:
				print(compUsuario+"=="+i[2]+"||"+compPasswd+"=="+i[3])
				_id_user = i[0]
				encontrado = True
				break
			else:
				continue
		conexion.close()

		#entrar a la interfaz de la agenda del usuario
		if encontrado==True:
			usuario.set("")
			password.set("")
			mostrar_agenda()
		else:
			password.set("")
			tkinter.messagebox.showerror("ERROR","ERROR \nUsuario o contraseña no validos \nvuelva a ingresarlas de nuevo ")



def guardar_registro():
	nombre = txt_nombreR.get()
	correo = txt_correoR.get()
	password1 = txt_password1R.get()
	password2 = txt_password2R.get()
	completo = verificar_correo(correo)
	
	if correo=="" or password1=="" or password2=="":
		tkinter.messagebox.showerror("ERROR", "ERROR no dejar espacios vacios")
	elif completo == False:
		tkinter.messagebox.showinfo("info",'Correo no valido \nes probable que no tenga "@" o ".com"')
	elif password1!=password2:
		tkinter.messagebox.showwarning("incongruencia","Las contraseñas no son iguales \nvuelva a ingresarlas correctamente")
		txt_password1R.set("")
		txt_password2R.set("")
	else:
		conexion_bd()
		validarCorreo = validar_correo_usuario(correo)

		if validarCorreo == None:
			x_id = asignar_id_usuario()
			print("id-",x_id)	
			nuevoUsuario = """INSERT INTO usuario 
			(id,nombre,correo,passwd) 
			VALUES("""+str(x_id)+""",'"""+nombre+"""','"""+correo+"""','"""+password1+"""');"""
			cursor.execute(nuevoUsuario)
			print(nuevoUsuario)
			txt_nombreR.set("")
			txt_correoR.set("")
			txt_password1R.set("")
			txt_password2R.set("")
			tkinter.messagebox.showinfo("info","["+correo+"] se ha guardado satisfactoriamente")
		else:
			txt_password1R.set("")
			txt_password2R.set("")
			tkinter.messagebox.showinfo("info","El usuario ["+validarCorreo[0]+"] ya existe \ningrese uno diferente")
		conexion.commit()
		conexion.close()


def modificar_contacto():
	global _click
	global _id_contacto
	global _item 
	try:
		conexion_bd()
		indice_item = ListaContactos.curselection()
		for item in indice_item:
			fila = ListaContactos.get(item)
		seleccion = fila.find("Nombre-->")
		if seleccion!=-1:
			modificar = seleccion_de_contacto(fila,"contacto")
			txt_nombre.set(modificar[1])
			txt_email.set(modificar[2])
			txt_telefono.set(modificar[3])
			_id_contacto = modificar[0]
			print(modificar)
			_item = item
			_click = 2
		else:
			tkinter.messagebox.showwarning("info","Selección incorrecta")
		conexion.close()
	except:
		tkinter.messagebox.showerror("ERROR","ERROR \nSelecciona de la lista el contacto a modificar")
		_click = 1
	

def verificar_correo(cadena):
	valor1 = cadena.find(".com")
	valor2 = cadena.find("@")
	if valor1!=-1 and valor2!=-1:
		return True
	else:
		return False

def validar_correo_usuario(correo):
	cursor.execute("SELECT correo from usuario where correo LIKE '%"+correo+"%'")
	validar = cursor.fetchone()
	return validar
	
def validar_correo_contacto(correo):
	cursor.execute("SELECT nombre, correo from contacto where correo LIKE '%"+correo+"%' and id_usuariof = "+str(_id_user))
	validar = cursor.fetchone()
	return validar

def validar_telefono_contacto(telefono):
	cursor.execute("SELECT nombre, numero_tel from contacto where numero_tel LIKE '%"+telefono+"%' and id_usuariof = "+str(_id_user))
	validar = cursor.fetchone()
	return validar

def asignar_id_usuario():
	cursor.execute("SELECT id from usuario")
	filas = cursor.fetchall()
	for num in filas:
		indice = num[0]
	return indice+1

def asignar_id_categoria():
	cursor.execute("SELECT id FROM categoria")
	filas = cursor.fetchall()
	for num in filas:
		indice = num[0]
	return indice+1
	#pendiente saber si no existe ningun id



#funciones para el manejo de ventanas
def mostrar_agenda():
	ocultar_login()
	ocultar_crear_categoria()
	v_principal.deiconify()
	spinCategorias = Spinbox(v_principal,textvariable=categorias,font="Calibri",
	state='readonly',width=12).place(x=160,y=385)
	v_principal.protocol("WM_DELETE_WINDOW", cerrar_aplicacion) 

def mostrar_registro():
	ocultar_login()
	v_registro.deiconify()
	v_registro.protocol("WM_DELETE_WINDOW",mostrar_login)

def mostrar_login():
	usuario.set("")
	password.set("")
	ocultar_registro()
	v_login.deiconify()

def mostrar_crear_categoria():
	v_categoria.deiconify()
	v_categoria.protocol("WM_DELETE_WINDOW",mostrar_agenda)

def ocultar_login():
	v_login.withdraw()
def ocultar_registro():
	v_registro.withdraw() 
def ocultar_crear_categoria():
	v_categoria.withdraw()

def cerrar_aplicacion():
	v_login.destroy()


""""
********************************************
Login de usuario
entrada del usuario a sus datos de la agenda
********************************************
"""
v_login = Tk()
#variables declaradas para el get del textBox
usuario = StringVar()
password = StringVar()


fondoLogin = PhotoImage(file="imagenes/fondo_login.png")
v_login.title("Agenda")
v_login.geometry("600x400")
#Bloquear el redimencionamiento de la ventana
v_login.resizable(0,0)
tituloLogin = font.Font(family='Bernard MT Condensed',size=25)
labelsLogin = font.Font(family='Lucida Calligraphy',size=12)
textBtnLogin = font.Font(family='Bookman Old Style',size=12)
FontLogin = "#E6FCF5"
bgLogin = "#8AC4B4"


#label Login
labelFondoLogin = Label(v_login,image=fondoLogin).place(x=0,y=0)
labelTituloLogin = Label(v_login,text="Login",bg="#44A6F8",font=tituloLogin,fg=FontLogin).place(x=260,y=40)
labelUsuario = Label(v_login,text="Usuario:",font=labelsLogin,relief=GROOVE,fg=FontLogin,bg=bgLogin).place(x=108,y=115)
labelPassword = Label(v_login,text="Contraseña:",font=labelsLogin,relief=GROOVE,fg=FontLogin,bg=bgLogin).place(x=80,y=165)
#entrada de datos login 
textUsuario = Entry(v_login,textvariable=usuario,font="Arial",relief=RAISED,width=25).place(x=190,y=120) 
textPassword = Entry(v_login,textvariable=password,font="Arial",relief=RAISED,width=25,show="*").place(x=190,y=170)
#textPassword.config(show="*");
#botones login
btnIngresar = Button(v_login,text="Ingresar",command=validar_usuario,font=textBtnLogin,bg="#F8A168",cursor="hand2")
btnIngresar.place(x=258,y=220)

btnRegistrarse = Button(v_login,text="Registrarse",command=mostrar_registro,font=textBtnLogin,bg="#F8A168",cursor="hand2")
btnRegistrarse.place(x=246,y=280)




"""
***************************
Ventana registro de usuario
***************************
"""
v_registro = Toplevel()
#variables declaradas para el get del textBox
txt_nombreR = StringVar()
txt_correoR = StringVar()
txt_password1R = StringVar()
txt_password2R = StringVar()

fondoRegistro = PhotoImage(file="imagenes/fondo_registro.png")
FontBtnRegistro = font.Font(family='Bookman Old Style',size=15)
fontTitulo = font.Font(family='Bernard MT Condensed',size=20)
v_registro.title("Agenda")
v_registro.geometry("600x400")
#Bloquear el redimencionamiento de la ventana
v_registro.resizable(0,0)


#labels ventana registro
labelFondoRegistro = Label(v_registro,image=fondoRegistro).place(x=0,y=0)
lblVentanaRegistro = Label(v_registro,text="Registro de usuario",font=fontTitulo,bg="#D25B0D",fg="#FCF7F4").place(x=200,y=30)
lblNombre = Label(v_registro,text="Nombre:",font=labelsLogin,relief=GROOVE,bg="#DCAF3F").place(x=265,y=70)                  
lblCorreo = Label(v_registro,text="Correo:",font=labelsLogin,relief=GROOVE,bg="#DCAF3F").place(x=270,y=130)
lblpassword1 = Label(v_registro,text="Contraseña:",font=labelsLogin,relief=GROOVE,bg="#DCAF3F").place(x=250,y=190)
lblpassword2 = Label(v_registro,text="Confirmar contraseña:",font=labelsLogin,relief=GROOVE,bg="#DCAF3F").place(x=205,y=250)

#text ventana resgistro
txtNombre = Entry(v_registro,textvariable=txt_nombreR,font="Arial",relief=RAISED,width=25).place(x=190,y=100)
txtCorreo = Entry(v_registro,textvariable=txt_correoR,font="Arial",relief=RAISED,width=25).place(x=190,y=160)
txtPassword1 = Entry(v_registro,textvariable=txt_password1R,font="Arial",relief=RAISED,width=25,show="*").place(x=190,y=220)
txtPassword2 = Entry(v_registro,textvariable=txt_password2R,font="Arial",relief=RAISED,width=25,show="*").place(x=190,y=280)

#botones ventana registro
btnRegistro = Button(v_registro,text="Guardar",bg="#F8A168",font=FontBtnRegistro,cursor="hand2",command=guardar_registro).place(x=250,y=330)


"""
**********************
ventana
crear categoria
**********************
"""
v_categoria = Toplevel()
txt_crear_categoria = StringVar()
fontNuevaCategoria = font.Font(family='Lucida Calligraphy',size=12)
fontBtnCategoria = font.Font(family='Bookman Old Style',size=12)
fondoCategoria = PhotoImage(file="imagenes/fondo_registro.png")
v_categoria.title("Agenda - Crear categoría")
v_categoria.geometry("350x130")
#Bloquear el redimencionamiento de la ventana
v_categoria.resizable(0,0)

#label ventana crear categoria
labelFondoCategoria = Label(v_categoria,image=fondoCategoria).place(x=0,y=0)
etiquetaCategoria = Label(v_categoria,text="Nueva categoría:",font=fontNuevaCategoria,bg="#DCAF3F",relief=GROOVE)
etiquetaCategoria.place(x=97,y=10)

#entrada de texto 
txtCategoria = Entry(v_categoria,textvariable=txt_crear_categoria,font="Arial").place(x=82,y=40)

#botones
btnGuardarCategoria = Button(v_categoria,text="Guardar",font=fontBtnCategoria,bg="#F8A168",cursor="hand2",
	command=crear_categoria).place(x=135,y=80)


"""
************************************************
Ventana agenda
esta entra hasta que se haya validado el usuario
************************************************
"""
v_principal = Toplevel(v_login)
fondoPrincipal = PhotoImage(file="imagenes/fondo_imagen.png")
#variables declaradas para obtener el texto ingresado
txt_nombre = StringVar()
txt_email = StringVar()
txt_telefono = StringVar()
categorias = StringVar()
busqueda = StringVar()
#colores de fondo
fondo = "#DC6349"
etiquetas = "#EA8937"
texto = "#C1BEBB"
botones = "#D30501"

#funciones de la paqueteria tipo de letras 
titulo = font.Font(family='Lucida Calligraphy',size=15, weight='bold')
FontEtiquetas = font.Font(family='Lucida Calligraphy',size=10, weight='bold')
FontCategorias = font.Font(family='Bookman Old Style',size=10, weight='bold')
FontBoton = font.Font(family='Broadway',size=12)
CrearC = font.Font(family='Arial',size=15)
v_principal.title("Agenda")
v_principal.config(bg=fondo)
v_principal.geometry("800x600")
v_principal.resizable(0,0)


#labels ventana principal
fondoImagen = Label(v_principal,image=fondoPrincipal).place(x=0,y=0) 
labeltitulo = Label(v_principal,text="Agenda Contactos",font=titulo,bg="white",fg="#DE9E43").place(x=300,y=8)
labelNombre = Label(v_principal,text="Nombre: ",font=FontEtiquetas,relief=GROOVE,bg=etiquetas).place(x=70,y=120)
labelEmail = Label(v_principal,text="Email: ",font=FontEtiquetas,relief=GROOVE,bg=etiquetas).place(x=70,y=200)
labelTelefono = Label(v_principal,text="Teléfono: ",font=FontEtiquetas,relief=GROOVE,bg=etiquetas).place(x=70,y=280)
labelTelefono = Label(v_principal,text="Buscar por: ",font=FontEtiquetas,bg="#FFFFFF").place(x=165,y=485)

#spin el cual busca por: nombre, email, telefono
spinBuscar = Spinbox(v_principal,textvariable=busqueda,values=("Nombre","Email","Teléfono"),font="Calibri",
state='readonly',width=12).place(x=160,y=510)


#textbox ventana principal
txtnombre = Entry(v_principal,textvariable=txt_nombre,font="Arial",relief=RAISED,bg=texto,width=30).place(x=70,y=144)
txtemail = Entry(v_principal,textvariable=txt_email,font="Arial",relief=RAISED,bg=texto,width=30).place(x=70,y=224)
txttelefono = Entry(v_principal,textvariable=txt_telefono,font="Arial",relief=RAISED,bg=texto,width=30).place(x=70,y=304)



#frame para el listbox dentro de ventana principal
FontListbox = font.Font(family='Arial',size=10, weight='bold')
frameListBox = Frame(v_principal,relief=SUNKEN)
frameListBox.place(x=460,y=100)
ListaContactos = Listbox(frameListBox,height=18,width=38,font=FontListbox)
ListaContactos.insert(0,"Crea una categoría y agrega tus")
ListaContactos.insert(1,"contactos a la lista...")
ListaContactos.grid(row=0, column=0,sticky=N+S+E+W)
#scrollbar en el eje Y
scrollbarY = Scrollbar(frameListBox, orient="vertical")
scrollbarY.config(command=ListaContactos.yview)
scrollbarY.grid(row=0, column=1, sticky=N+S)
#scrollbar en el eje X
scrollbarX = Scrollbar(frameListBox, orient="horizontal")
scrollbarX.config(command=ListaContactos.xview)
scrollbarX.grid(row=1, column=0, sticky=E+W)
#desabilita los scrollbars hasta que se activan con el tamaño del texto
ListaContactos.config(yscrollcommand=scrollbarY.set)
ListaContactos.config(xscrollcommand=scrollbarX.set)


#botones ventana principal (agenda)
btnCrearCategoria = Button(v_principal,text="Crear Categoría",font=CrearC,bg="#5BD00A",cursor="hand2",
	fg="#F9F4F4",relief=RIDGE,command=mostrar_crear_categoria).place(x=48,y=40)
btnGuardar = Button(v_principal,text="Guardar",font=FontBoton,bg=botones,cursor="hand2",
	fg="#F9F4F4",relief=RAISED,command=guardar_contacto).place(x=100,y=450)
btnBuscar = Button(v_principal,text="Buscar",font=FontBoton,bg=botones,cursor="hand2",
	fg="#F9F4F4",relief=RAISED,command=buscar).place(x=240,y=450)
btnMostrar = Button(v_principal,text="Mostrar",font=FontBoton,bg=botones,cursor="hand2",
	fg="#F9F4F4",relief=RAISED,command=mostrar).place(x=490,y=450)
btnEliminar = Button(v_principal,text="Eliminar",font=FontBoton,bg=botones,cursor="hand2",
	fg="#F9F4F4",relief=RAISED,command=eliminar).place(x=630,y=450)
btnCategoria = Button(v_principal,text="Categorías",font=FontCategorias,relief=GROOVE,bg="#3181AF",
	cursor="hand2",fg="#F9F4F4",command=mostrar_categoria).place(x=170,y=350)
btnCategoria = Button(v_principal,text="<--Cargar-->",relief=GROOVE,bg="#9431BF",
	cursor="hand2",fg="#F9F4F4",command=cargar_categorias).place(x=172,y=410)
btnModificar = Button(v_principal,text="Modificar",relief=GROOVE,bg=etiquetas,
	cursor="hand2",font=FontEtiquetas,command=modificar_contacto).place(x=250,y=85)


#loop y cierre de ventanas
v_categoria.withdraw()
v_registro.withdraw()
v_principal.withdraw()
v_login.mainloop()