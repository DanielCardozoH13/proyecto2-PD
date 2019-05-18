from socket import socket
from tkinter import *
from tkinter import messagebox
from threading import Thread
import Pyro4
from hashlib import sha1
from playsound import playsound
import time


@Pyro4.expose
class Cliente(Frame):

    def __init__(self, parent, sock, model, addre):

        #Frame.__init__(self, parent)
        self.sock = sock
        self.addre = addre
        self.model = model
        self.parent = parent #hace referencia a la vetana principal de Tkinter()
        self.ventana = parent
        self.ventana.title("chatroom Python Tkinter")
        self.ventana.geometry("700x400")
        self.ventana.minsize(700,400)
        self.ventana.maxsize(700,400)

        #self.login = Frame(parent) #lo que era self.parent
        self.logup = Frame(parent)
        self.home = Frame(parent) #lo que era master
        recibir_hilo = Thread(target=self.recibir)
        recibir_hilo.start()

        self.login_fun()


    def login_fun(self):
        self.parent.protocol("WM_DELETE_WINDOW", self.cerrando_sin_login)
        self.login = Frame(self.parent)
        self.login.pack()

        frame01 = Frame(self.login)
        frame01.pack(fill=BOTH, padx=30, pady=30, side=BOTTOM)

        frameArr = Frame(frame01)
        frameArr.pack(side = TOP, expand = True, fill=X)

        frameIz = Frame(frameArr)
        frameIz.pack(side=LEFT, fill=X)
        label_user = Label(frameIz, text="Usuario: ", anchor=W, background="dark slate gray",
                           foreground="white", font="Helvetica 8  bold")
        label_password = Label(frameIz, text="Clave:", anchor=W, background="dark slate gray",
                               foreground="white", font="Helvetica 8  bold")

        label_user.pack(fill=X, side=TOP)
        label_password.pack(fill=X, side=TOP)

        frameDr = Frame(frameArr)
        frameDr.pack(side=LEFT, fill=X)

        self.dbuser = Entry(frameDr)
        self.dbpassword = Entry(frameDr, show="*")
        self.dbuser.pack(side=TOP)
        self.dbpassword.pack(side=TOP)

        frameDown = Frame(frame01)
        frameDown.pack(side=TOP, fill=X)
        connectb = Button(frameDown, text="Ingresar", font="Helvetica 10 bold", command=self.ingreso_app)
        registrarse = Button(frameDown, text="Registrarse", font="Helvetica 10 bold", command=self.ir_a_logup)

        registrarse.pack(side=BOTTOM)
        connectb.pack(side=BOTTOM)


    def logup_fun(self):
        self.logup = Frame(self.ventana)
        self.logup.pack(fill=Y, side=TOP)

        frame = Frame(self.logup)
        frame.grid(row=0, column=2, columnspan=6, pady=20)

        label_email = Label(frame, text="Email: ", anchor=W, background="dark slate gray",
                            foreground="white", font="Helvetica 8  bold")
        label_contrasena = Label(frame, text="Contraseña:", anchor=W,
                                 background="dark slate gray",
                                 foreground="white", font="Helvetica 8  bold")
        label_nombre = Label(frame, text="Nombre:", anchor=W,
                             background="dark slate gray",
                             foreground="white", font="Helvetica 8  bold")

        label_email.grid(row=0, column=0,    pady=5, columnspan=1, sticky=N + S + W + E)
        label_contrasena.grid(row=1, column=0, pady=5, columnspan=1, sticky=N + S + W + E)
        label_nombre.grid(row=2, column=0, pady=5, columnspan=1, sticky=N + S + W + E)

        self.txtemail = Entry(frame)
        self.txtcontra = Entry(frame, show="*")
        self.txtnombre = Entry(frame)

        self.txtemail.grid(row=0, column=1, pady=5, columnspan=4, sticky=N + S + W + E)
        self.txtcontra.grid(row=1, column=1, pady=5, columnspan=4, sticky=N + S + W + E)
        self.txtnombre.grid(row=2, column=1, pady=5, columnspan=4, sticky=N + S + W + E)

        registar_btn = Button(frame, text="Crear", font="Helvetica 10 bold", command=self.registrar_user)

        registar_btn.grid(row=6, column=1, sticky=W)


    def ir_a_logup(self):
        self.login.destroy()
        self.logup_fun()

    def registrar_user(self):
        usuario = self.txtemail.get()
        passw = sha1(self.txtcontra.get().encode('utf-8')).hexdigest() ### ==== encriptación de contraseña
        nombre = self.txtnombre.get()

        if (usuario != "") and (passw != ""):
            self.datosUser = self.model.logup(usuario, passw, nombre, self.addre)

            if self.datosUser == 0:
                #======== SI NO EXISTE, MENSAJE "USUARIO creado"
                self.datosUser=self.model.login(usuario, passw, self.addre)
                messagebox.showinfo("Información", "Usuario Creado")
                self.logup.destroy()
                self.inicio_chat()
            elif self.datosUser == 1:
                #============= si la contraseña y usuario existe, mensaje "usuario ya registrado"
                self.datosUser = self.model.login(usuario, passw, self.addre)
                messagebox.showinfo("Información", "El Usuario Ya Existía")
                self.logup.destroy()
                self.login_fun()
            elif self.datosUser == 2:
                # ======= si el user existe, mensaje "contraseña incorrecta"
                messagebox.showerror("error", "El usuario ya esta registrado, ingrese una contraseña valida")
                self.logup.destroy()
                self.login_fun()
        else:
            messagebox.showerror("error", "Debe ingresar la informacióon requerida")
            self.logup.destroy()
            self.logup_fun()


    def ingreso_app(self):
        self.parent.protocol("WM_DELETE_WINDOW", self.cerrando)
        self.usuario = self.dbuser.get()
        #/////////////////////////// contraseña encriptada ////////////////////////////////////
        self.passw = sha1(self.dbpassword.get().encode('utf-8')).hexdigest()

        if (self.usuario != "") and (self.passw != ""):
            self.datosUser = self.model.login(self.usuario, self.passw, self.addre)
            #self.datosUser = respuesta_server
            #respuesta_server

            if self.datosUser != 0:
                self.login.destroy()
                self.inicio_chat()
                ##===================== se envia el nombre con del usuario al servidor.
                try:
                    tipo_peticion = "name_user{?[/-/]¿}"
                    mss = tipo_peticion + self.usuario
                    self.sock.send(bytes(mss, "utf-8"))
                except TypeError:
                    pass

            else:
                messagebox.showerror("error", "Usuario o Contraseña incorrecta")
                self.login.destroy()
                self.login_fun()
        else:
            messagebox.showerror("error", "Ingrese los datos solicitados")
            self.login.destroy()
            self.login_fun()

    def inicio_chat(self):  ####===================> esta función crea la ventana principal del chat =======
        ###=================================> MENU HORIZONTAL
        menu = Menu(self.ventana)
        self.ventana.config(menu=menu)

        # acciones
        acciones = Menu(menu, tearoff=0)
        menu.add_cascade(label="Acciones", menu=acciones)
        acciones.add_command(label="Borrar Chat")#, command=self.clear_chat)
        acciones.add_separator()
        acciones.add_command(label="Salir", command=self.cerrando)

        ####========================================== FIN DE MENU HORIZONTAL

        # ========================================= INTERFAZ PRINCIPAL============================

        ###============= MARCO chat CONTIENEN TEXTBOX Y BOTONES
        chat = Frame(self.ventana, bd=6)
        chat.pack(expand=True, fill=BOTH, side=LEFT)

        # ======= lista donde se guardan los usuarios conectados
        list_logins = Frame(self.ventana, bd=0)
        list_logins.pack(expand=True, side=LEFT)
        label_logins = Label(list_logins, text="Usuarios Conectados: ", anchor=CENTER, background="dark slate gray",
                             foreground="white", font="verdana 10  bold", width=2)
        label_logins.pack(fill=BOTH)
        list_logins.pack(expand=True, fill=BOTH, side=RIGHT)
        self.logins_list = Listbox(list_logins, selectmode=SINGLE, font="Verdana 10",
                              exportselection=False, width=2)
        self.logins_list.bind('<<ListboxSelect>>', self.selected_login_event)
        self.logins_list.pack(expand=True, fill=BOTH)

        text_frame = Frame(chat, bd=6)
        text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        text_box_scrollbar = Scrollbar(text_frame, bd=0)
        text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(text_frame, yscrollcommand=text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 12", relief=GROOVE,
                             width=15, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        entry_frame = Frame(chat, bd=1)
        entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # users_message = self.entry_field.get()

        # frame containing send button and emoji button
        send_button_frame = Frame(chat, bd=0)
        send_button_frame.pack(fill=BOTH)

        # send button
        send_button = Button(send_button_frame, text="Send", width=8, relief=GROOVE, bg='white',
                             bd=1, command=lambda: self.send_message(), activebackground="#FFFFFF",
                             activeforeground="#000000")
        send_button.pack(side=LEFT, ipady=2)
        self.ventana.bind("<Return>", self.send_message_event)

        # emoticons
        emoji_button = Button(send_button_frame, text="☺", width=5, relief=GROOVE, bg='white',
                              bd=1, activebackground="#FFFFFF",
                              activeforeground="#000000", command=self.emoji_options)
        emoji_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)
        emoji_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")

    def emoji_options(self):
        # Con Toplevel coloca coloca la venta sobre la anterior y es necesaria cerrarla para volver a la anterior ventana
        self.emoji_selection_window = Toplevel(bg="#FFFFFF", )
        self.emoji_selection_window.bind("<Return>", self.send_message_event)
        selection_frame = Frame(self.emoji_selection_window, bd=4, bg="#FFFFFF")
        selection_frame.grid()
        self.emoji_selection_window.focus_set()
        self.emoji_selection_window.grab_set()

        close_frame = Frame(self.emoji_selection_window)
        close_frame.grid(sticky=S)
        close_button = Button(close_frame, text="Close", font="Verdana 9", relief=GROOVE, bg="#FFFFFF",
                              fg="#000000", activebackground="#FFFFFF",
                              activeforeground="#000000", command=self.close_emoji)
        close_button.grid(sticky=S)

        root_width = self.ventana.winfo_width()
        root_pos_x = self.ventana.winfo_x()
        root_pos_y = self.ventana.winfo_y()

        position = '180x320' + '+' + str(root_pos_x + root_width) + '+' + str(root_pos_y)
        self.emoji_selection_window.geometry(position)
        self.emoji_selection_window.minsize(180, 320)
        self.emoji_selection_window.maxsize(180, 320)

        emoticon_1 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☺",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("☺"), relief=GROOVE, bd=0)
        emoticon_1.grid(column=1, row=0, ipadx=5, ipady=5)
        emoticon_2 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☻",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("☻"), relief=GROOVE, bd=0)
        emoticon_2.grid(column=2, row=0, ipadx=5, ipady=5)
        emoticon_3 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☹",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("☹"), relief=GROOVE, bd=0)
        emoticon_3.grid(column=3, row=0, ipadx=5, ipady=5)
        emoticon_4 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="♡",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("♡"), relief=GROOVE, bd=0)
        emoticon_4.grid(column=4, row=0, ipadx=5, ipady=5)

        emoticon_5 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="♥",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("♥"), relief=GROOVE, bd=0)
        emoticon_5.grid(column=1, row=1, ipadx=5, ipady=5)
        emoticon_6 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="♪",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("♪"), relief=GROOVE, bd=0)
        emoticon_6.grid(column=2, row=1, ipadx=5, ipady=5)
        emoticon_7 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❀",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("❀"), relief=GROOVE, bd=0)
        emoticon_7.grid(column=3, row=1, ipadx=5, ipady=5)
        emoticon_8 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❁",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("❁"), relief=GROOVE, bd=0)
        emoticon_8.grid(column=4, row=1, ipadx=5, ipady=5)

        emoticon_9 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✼",
                            activebackground="#FFFFFF", activeforeground="#000000",
                            font='Verdana 14', command=lambda: self.send_emoji("✼"), relief=GROOVE, bd=0)
        emoticon_9.grid(column=1, row=2, ipadx=5, ipady=5)
        emoticon_10 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☀",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("☀"), relief=GROOVE, bd=0)
        emoticon_10.grid(column=2, row=2, ipadx=5, ipady=5)
        emoticon_11 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✌",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✌"), relief=GROOVE, bd=0)
        emoticon_11.grid(column=3, row=2, ipadx=5, ipady=5)
        emoticon_12 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✊",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✊"), relief=GROOVE, bd=0)
        emoticon_12.grid(column=4, row=2, ipadx=5, ipady=5)

        emoticon_13 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✋",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✋"), relief=GROOVE, bd=0)
        emoticon_13.grid(column=1, row=3, ipadx=5, ipady=5)
        emoticon_14 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☃",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("☃"), relief=GROOVE, bd=0)
        emoticon_14.grid(column=2, row=3, ipadx=5, ipady=5)
        emoticon_15 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❄",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("❄"), relief=GROOVE, bd=0)
        emoticon_15.grid(column=3, row=3, ipadx=5, ipady=5)
        emoticon_16 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☕",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("☕"), relief=GROOVE, bd=0)
        emoticon_16.grid(column=4, row=3, ipadx=5, ipady=5)

        emoticon_17 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="☂",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("☂"), relief=GROOVE, bd=0)
        emoticon_17.grid(column=1, row=4, ipadx=5, ipady=5)
        emoticon_18 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="★",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("★"), relief=GROOVE, bd=0)
        emoticon_18.grid(column=2, row=4, ipadx=5, ipady=5)
        emoticon_19 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❎",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("❎"), relief=GROOVE, bd=0)
        emoticon_19.grid(column=3, row=4, ipadx=5, ipady=5)
        emoticon_20 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❓",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("❓"), relief=GROOVE, bd=0)
        emoticon_20.grid(column=4, row=4, ipadx=5, ipady=5)

        emoticon_21 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="❗",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("❗"), relief=GROOVE, bd=0)
        emoticon_21.grid(column=1, row=5, ipadx=5, ipady=5)
        emoticon_22 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✔",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✔"), relief=GROOVE, bd=0)
        emoticon_22.grid(column=2, row=5, ipadx=5, ipady=5)
        emoticon_23 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✏",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✏"), relief=GROOVE, bd=0)
        emoticon_23.grid(column=3, row=5, ipadx=5, ipady=5)
        emoticon_24 = Button(selection_frame, bg="#FFFFFF", fg="#000000", text="✨",
                             activebackground="#FFFFFF", activeforeground="#000000",
                             font='Verdana 14', command=lambda: self.send_emoji("✨"), relief=GROOVE, bd=0)
        emoticon_24.grid(column=4, row=5, ipadx=5, ipady=5)

    def send_emoji(self, emoticon):
        self.entry_field.insert(END, emoticon)

    def close_emoji(self):
        ## cierra ventana de emoticones
        self.emoji_selection_window.destroy()
    


    def send_message_event(self, event=None):
        self.send_message()

    def send_message(self):
        tipo_peticion= "todos_chats{?[/-/]¿}"
        nombre_usuario = "{?[/-/]¿}" + self.datosUser[1]
        mensaje = self.entry_field.get()
        #self.model.guardar_mensaje(self.datosUser[1], mensaje)
        mensaje=tipo_peticion+mensaje+nombre_usuario
        self.entry_field.delete(0, END)
        self.sock.send(bytes(mensaje, "utf-8"))

    def clear_chat(self):
        pass

    def cerrando_sin_login(self):
        tipo_peticion = "salir{?[/-/]¿}"
        mensaje = tipo_peticion + "no_login"
        self.sock.send(bytes(mensaje, "utf-8"))
        self.parent.destroy()

    def cerrando(self):
        #######=============agregar aca un UPDATE EN tabla logs
        tipo_peticion = "salir{?[/-/]¿}"
        mensaje = tipo_peticion + self.datosUser[1]
        self.sock.send(bytes(mensaje, "utf-8"))
        self.parent.destroy()

    def change_username(self):
        pass

    def selected_login_event(self):
        pass

    def cierra_ventana_chat(self):
        self.ventana.destroy()


    def exit_event(self):
        pass

    def recibir(self):
        while True:
            try:
                input_data = self.sock.recv(1024)
                mensaje_recv = input_data.decode('utf-8')  ##se decodifica el mensaje enviado por el cliente
                datos_mens = mensaje_recv.split('{?[/-/]¿}')
                #esta es la otra linea - como no me esta abriendo el programa ando a ciegas la verdad asi que si no va ahi solo esque mueva esa linea, es simple
                if datos_mens[0] == 'todos_chats':
                    menss = "\n"+datos_mens[1]

                    self.text_box.configure(state=NORMAL)
                    self.text_box.insert(END, menss)
                    self.text_box.see(END)
                    self.text_box.configure(state=DISABLED)
                    playsound('audio.mp3')
                elif datos_mens[0] == 'unicast':
                    pass
                elif datos_mens[0] == 'usuarios_activos':
                    listado_user_activos = self.model.users_activos()
                    for user in listado_user_activos:
                        #self.logins_list.configure(state=NORMAL)
                        self.logins_list.insert(END, user)
                        self.logins_list.see(END)
                        #self.logins_list.configure(state=DISABLED)

            except OSError:
                break

    def usuarios_activos(self):
        while True:
            respuesta = self.model.users_activos()
            time.sleep(30)
            if respuesta != "fail":
                self.logins_list.insert(END, respuesta[0])
                self.logins_list.see(END)


def main():
    s = socket()
    s.connect(("localhost", 35000))


    while True:
        output_data = input("Desea Ingresar a la Sala de Chat (S/N):  ")

        if output_data == 's' or output_data == 'S':
            tipo_peticion="login{?[/-/]¿}"
            mensaje=tipo_peticion+output_data
            s.send(bytes(mensaje, "utf-8"))

            # Recibir respuesta.
            input_data = s.recv(1024)
            mensaje_recv = input_data.decode('utf-8')  ##se decodifica el mensaje enviado por el cliente
            datos_mens = mensaje_recv.split('{?[/-/]¿}')
            addre = datos_mens[2]
            if datos_mens[1] == "1":
                #servidor de nombres de Pyro4s
                #server = Pyro4.Proxy("PYRONAME:myServer")
                model = Pyro4.Proxy("PYRONAME:myModel")

                root = Tk()

                #instancia de la clase Cliente con instancia de Tk y Pyro4
                app = Cliente(root, s, model, addre)

                root.mainloop()
                pass
            pass
        else:
            print("Terminando Conexión")
            break


if __name__ == "__main__":
    main()