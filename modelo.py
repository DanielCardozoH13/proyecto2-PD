import Pyro4
import mysql.connector
import time

@Pyro4.expose
class Modelo():
    def __init__(self):
        self.host = '127.0.0.1'
        self.name = 'chatmulticliente'
        self.user = 'root'
        self.password = ''
        self.usuario = ''
        self.conn = None
        self.conn = mysql.connector.connect(user=str(self.user),
                                            passwd=str(self.password),
                                            host=str(self.host),
                                            db=str(self.name))

        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def logup(self, usuario, passw, nombre, addre):
        resultado = self.login(usuario, passw, addre)
        if resultado != 0:
            result = 1 #el usuario existia
        else:
            #result  = 0 #el usuario no existe y se registro
            respuesta = self.agregarUser(usuario, passw, nombre)
            if respuesta == "ok":
                result = 0 #usuario no existia y se registro
            else:
                result = 2 #el usuario existe, no se registra
        return result

    def login(self, user, passw, addr):
        sql = "SELECT * FROM usuarios WHERE usuario = '"+user +"' AND contrasena = '"+passw+"'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        if result:
            intento = "ok"
            hoy = time.strftime("%Y%m%d")
            hora = time.strftime("%H:%M:%S")
            # ip = socket.gethostbyname(socket.gethostname())

            sqlcon = 'INSERT INTO logs (fecha_ingreso,usuario,intentos,hora_ingreso,ip) VALUES ("%s","%s","%s","%s","%s")' % (
                hoy, user, intento, hora, addr)
            self.cursor.execute(sqlcon)
            self.conn.commit()

            for registro in result:
                self.datosUser = registro
        else:
            self.datosUser = 0

            intento = 'Fallo'
            hoy = time.strftime("%Y%m%d")
            hora = time.strftime("%H:%M:%S")

            sqlcon = 'INSERT INTO logs (fecha_ingreso,usuario,intentos,hora_ingreso, ip) VALUES ("%s","%s","%s","%s","%s")' % (
                hoy, user, intento, hora, addr)
            self.cursor.execute(sqlcon)
            self.conn.commit()
        return self.datosUser

    def agregarUser(self, user, passw, nombre):
        try:
            sql = "INSERT INTO usuarios (usuario, contrasena, nombre) VALUES ('%s','%s','%s')" % (user, passw, nombre)
            self.cursor.execute(sql)
            self.conn.commit()
            result = "ok"
        except:
            result = "fail"
        return result

    def actualizar_activos(self, user, estado):
        sql = "UPDATE usuarios SET estado='"+estado+"' WHERE usuario = '"+user+"'"
        self.cursor.execute(sql)
        self.conn.commit()

        if sql:
            respuesta = "ok"
        else:
            respuesta = "fail"
        return respuesta

    def users_activos(self):
        sql = "SELECT usuario FROM usuarios WHERE estado = 'activo'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if result:
            for registro in result:
                respuesta = registro
        else:
            respuesta = "fail"
        return respuesta

def main():
    try:
        m = Modelo()
        print("Modelo Iniciado ...")
        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(m)
        ns.register("myModel", uri)
        print("Uri para acceder remotamente a los metodos de la clase Modelo")
        print(uri)
        daemon.requestLoop()
    except:
        print("hubo un error en la conexión")
        print("Verifique que en la terminal del sistema operativo este en ejecución el servidor de nombre de Pyro4 \ncomando: python -m Pyro4.naming")


if __name__ == "__main__":
    main()
