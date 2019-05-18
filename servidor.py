import socket
from socket import socket, error
from threading import Thread
import Pyro4
import time

#clientes = {}  ##variable donde se almacenaran las direcciones activas en el programa
#direcciones = {}
clientes = []
class Servidor(Thread):
    def __init__(self, conn, addr, model, s):
        # Inicializar clase padre.
        Thread.__init__(self)

        self.socket = s
        self.conn = conn
        self.addr = addr
        self.model = model

        clientes.append(conn)

    def run(self):
        while True:
            try:
                # Recibir datos del cliente.
                input_data = self.conn.recv(1024)
                mensaje_recv=input_data.decode('utf-8')  ##se decodifica el mensaje enviado por el cliente
                datos_mens=mensaje_recv.split('{?[/-/]¿}')  ###se crea una lista, donde cada elemento esta separado por '{?[/-/]¿}'
                #print("cliente dice:")
                #print(datos_mens)
                ##======datos_mens[0] indica el tipo de acción
                ##======datos_mens[1] mensaje introducido por el usuario
                ##======datos_mens[2] correo del usuario
                if datos_mens[0] == 'login':
                    if datos_mens[1] == "s" or datos_mens[1] == "S":
                        msg = 'login{?[/-/]¿}1{?[/-/]¿}'+ str(self.addr)
                        self.conn.send(bytes(msg, "utf-8"))
                    else:
                        print("se ha desconectado %s" % self.conn)
                elif datos_mens[0] == 'todos_chats':
                    self.broadcast(str(datos_mens[1]), datos_mens[2]+": ", 'todos_chats{?[/-/]¿}')
                elif datos_mens[0] == 'un_chat':
                    pass
                elif datos_mens[0] == "name_user":
                    self.model.actualizar_activos(datos_mens[1], "activo")
                    self.broadcast("ok","","usuarios_activos{?[/-/]¿}")

                    """
                    print("guardar sockety user name en Bd")
                    
                    indice = len(direcciones)
                    print(indice)
                    print("da")
                    direcciones.setdefault({datos_mens[1]:self.conn})
                    print(direcciones)
                    """
                elif datos_mens[0] == "salir":
                    clientes.remove(self.conn)
                    self.model.actualizar_activos(datos_mens[1], "inactivo")
                    self.broadcast(datos_mens[1]+" ha salido del chat.","", "todos_chats{?[/-/]¿}")
                    break


            except error:
                print("[%s] Error de lectura." % self.name)
                #eliminar conexion de lista coonexiones
                #cerrar socket
                break

    def broadcast(self, mensaje, prefix="", tipo = ""):
        mensaje =str(tipo )+ str(prefix) + str(mensaje)
        for sock in clientes:
            sock.send(bytes(mensaje, "utf-8"))

    """
    def enviar_activos(self):
        while True:
            try:
                pass
                tip_accion = 'usuarios_activos{?[/-/]¿}'
                print(tip_accion)
                
                for key in direcciones:
                    print(key)
                    print(direcciones[key])
                    connexion = direcciones[key][1]
                    mensa = tip_accion+str(direcciones)
                    #print(mensa)
                    connexion.send(bytes(mensa, "utf-8"))
                    time.sleep(30)
                
            except:
                pass
                """


def main():
    s = socket()

    # Escuchar peticiones en el puerto 35000.
    s.bind(("localhost", 35000))
    s.listen(10)

    print("Servidor Activo")
    while True:
        #instanciando modelo con procedimientos remotos del modelo
        model = Pyro4.Proxy("PYRONAME:myModel")

        conn, addr = s.accept()
        #addr.setblocking(False)
        c = Servidor(conn, addr, model,s)
        c.start()
        print("%s:% d se ha conectado." % addr)

        """
        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(c)
        ns.register("myServer", uri)
        print(uri)     ###==== IMPRIME LA URI CON LA QUE PUEDEN ACCEDER REMOTAMENTE A METODOS DE LA CLASE Servidor
        daemon.requestLoop(loopCondition=lambda:c.status)##==== lambda es una funcion independiente de una sola linea que en el caso detiene el ciclo requesLoop cuando la variable status sea False
        """

if __name__ == "__main__":
    main()