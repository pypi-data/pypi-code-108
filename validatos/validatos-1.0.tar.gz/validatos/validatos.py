
class Validatos():

    # Función para validar la longitud de un cadena retorna un booleano usando la funcion len()
    def __validar_len(self, dato: str, longitud: int) -> bool:
        while (x := len(dato)) <= longitud:
            return True


    # Función para validar si existe o no algún caracter especial en la cadena retorna un boolean
    def __validacion_caracteres(self, dato: str) -> bool:
        lcaracter = "'áéíóú ´/*+,;:{}[]()¨!|¬#$%&=?¿¡!"
        for i in dato:
            if i in lcaracter:
                return True
        else:
            return False


    # Nueva función para validar la existencia de un primary_key ingresado en la tabla de elección
    def existencia_tablas(conexion, nombre_tabla: str, nombre_columna: str, primary_key :str, id: str) -> bool or str:
        cursor_obj = conexion.cursor()
        cursor_obj.execute(f'SELECT {nombre_columna} FROM {nombre_tabla} WHERE {primary_key} = {id}')
        id_bd = cursor_obj.fetchone()
        if type(id_bd) == tuple:
            return False
        else:
            return int(id)


    # Función para validar una entrada numerica str y retornarla como str
    # es necesario convertir el número a int siempre y cuando se requiera
    # Se usa la función .isnumeric() para verificar que la entrada sea numerica
    # y el metodo _valida_len() para verificar que la longitud sea la correcta
    def numero(dato: str, longitud: int) -> str:
        while not dato.isnumeric() or not Validatos.__validar_len(dato, longitud):
            dato = input('¡ERROR! Verifique e ingrese de nuevo la información: ')
        return dato



    # Función para validar que una entrada sea unicamente alfabetica
    # Se usa la función .replace para remplazar los espacios en blanco por una cadena vacía
    # y .isalpha() para verificar que la entrada sea alfabetica
    def letra(dato: str, longitud: int) -> str:
        while not (d := dato.replace(' ', '').isalpha()) or not Validatos.__validar_len(dato, longitud):
            dato = input('¡ERROR! Verifique e ingrese de nuevo la información: ')
        return dato.strip()



    # Función para validar que un número sea acorde a la longitud tanto mínimo como máxima
    # Se usa la función .isdigit() para verificar que la entrada sea numerica
    def telefono(dato: str, longitud: int) -> str or int:
        while not (d := dato.isdigit()) or not Validatos.__validar_len(dato, longitud) or dato[0] != '3' or len(dato) != 10:
            dato = input('''¡ERROR! Verifique e ingrese de nuevo la información: ''')
        return int(dato)



    # Función para validar la longitud y escritura acepta para un correo electrónico
    # Función que usa el método _validación_caracteres() para verificar que no existan caracteres especiales
    def correo(dato: str, longitud: int) -> str:
        state = True
        while state:
            try:
                if Validatos.__validacion_caracteres(dato) or len(dato.split('@')[0]) < 6 or len(dato.split('@')) > 2:
                    raise ValueError
                else:
                    a = Validatos.__validar_len(dato, longitud)
                    dato_list = dato.split('@')
                    if a and ('.') in dato_list[1]:
                        return dato.lower()
                        state = False
                    else:
                        raise ValueError
            except:
                dato = input('''¡ERROR! Verifique e ingrese de nuevo la información: ''')



    # Función para validar si un número decimal es correcto
    def decimal(dato: str, longitud: int) -> float:
        while not (d := any(i.isdigit() for i in dato)) or not Validatos.__validar_len(dato, longitud):
            dato = input('''¡ERROR! Verifique e ingrese de nuevo la información: ''')
        return float(dato)



    # Función publica para validar solo la longitud de entrada
    # Función con un límite de longitud para la entrada de datos
    def longitud(dato: str, longitud: int) -> str:
        while not Validatos.__validar_len(dato, longitud) or len(dato) == 0:
            dato = input('''¡ERROR! Verifique e ingrese de nuevo la información: ''')
        return dato
