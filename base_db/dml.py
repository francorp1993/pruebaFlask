class Tabla:
    
    # Creación de la tabla
    def __init__(self, nombre, conexion, campos):
        self.tabla = nombre
        self.conexion = conexion
        self.campos = campos
    
    # CRUD
    def crear(self, valores, de_bbdd=False):
        if de_bbdd:
            # del modelo --> args = (valores) # (())
            for campo, valor in zip(self.campos, *valores):
                setattr(self, campo, valor)
        else:
            for campo, valor in zip(self.campos[1:], valores):
                setattr(self, campo, valor)
  
    def guardar_db(self):
        campos_q = str(self.campos[1:]).replace("'", "`")
        values_q = f"({'%s, ' * (len(self.campos) - 2)} %s)"
        consulta = (f"INSERT INTO {self.tabla} {campos_q} "
                    f"VALUES {values_q};")
        
        datos = tuple(getattr(self, campo) for campo in self.campos[1:])  # Excluido el 'id'
        
        try:           
            cursor = self.conexion.cursor()
            cursor.execute(consulta, datos)
            self.conexion.commit()
            cursor.close()
            return 'Creación exitosa.'
        except Exception as e:
            self.conexion.rollback()
            cursor.close()
            return f"Error al guardar en la base de datos: {str(e)}" 
    
          
    
    @classmethod
    def obtener(cls, campo=None, valor=None):
        
        if campo is None or valor is None:
            consulta = f"SELECT * FROM {cls.tabla};"
            resultado = cls.__conectar(consulta)
        else:
            consulta = f"SELECT * FROM {cls.tabla} WHERE {campo} = %s;"
            resultado = cls.__conectar(consulta, (valor,))
        
        return resultado
   
     
    @classmethod
    def eliminar(cls, id):
        consulta = (f"DELETE FROM {cls.tabla} WHERE id = %s ;")
        rta_db = cls.__conectar(consulta, (id,))
        
        if rta_db:
            return 'Eliminación exitosa.'
            
        return 'No se pudo eliminar el registro.'
        
    
    @classmethod
    def modificar(cls, registro):
        # type(registro) == dict
        """
        UPDATE tabla
        SET
            campo1 = %s,
            ...
            campoN = %s
        WHERE ... ;
        """
        
        update_q = f"UPDATE {cls.tabla} "
        set_q = 'SET'
        
        id = registro.pop('id')
        id = int(id) if type(id) != int else id #casteo a entero, si no es un entero, me quedo con el valor
        
        for c in list(registro.keys()):
            set_q += f' {c} = %s,'
        
        set_q = set_q[0:-1]       
        where_q = f" WHERE id = %s;"
        consulta = update_q + set_q + where_q    
        nvos_datos = *list(registro.values()), id
        rta_db = cls.__conectar(consulta, nvos_datos)
        
        if rta_db:   
            return 'Modificación exitosa.'
        
        return 'No se pudo modificar el registro.'

    @classmethod        
    def __conectar(cls, consulta, datos=None):
        
        try:
            cursor = cls.conexion.cursor()
            print("DDBB conectada")
        except Exception as e:
            print("DDBB conectada")
            cls.conexion.connect()
            cursor = cls.conexion.cursor()
        
        if consulta.startswith('SELECT'): # si empieza la consulta con SELECT quiere decir que me va a traer algo de la db. Entonces empiezo a analizar si vienen o no datos.
            
            if datos is not None:
                cursor.execute(consulta, datos)
            else:
                cursor.execute(consulta)
                
            rta_db = cursor.fetchall()
            
            if rta_db != []:
                resultado = [cls(registro, de_bbdd=True) for registro in rta_db]
                if len(resultado) == 1:
                    resultado = resultado[0]
            else:
                resultado = False          
            
            cls.conexion.close()
        
        else: # Si no hago un SELECT ... 
            
            try:
                # Crud-Update-Delete puede salir mal con esto lo contengo, agarro el error
                cursor.execute(consulta, datos)
                cls.conexion.commit()    
                cls.conexion.close()
                resultado = True
            except Exception as e:
                resultado = False
            
        return resultado
    
    # @classmethod
    # def obtener_para_login(cls, username):
    #     consulta = f"SELECT * FROM {cls.tabla} WHERE username = %s;"
    #     resultado = cls.__conectar(consulta, (username,))
        
    #     if resultado:
    #         if isinstance(resultado, list):
    #             if len(resultado) == 1:
    #                 return cls(**resultado[0])  # Devolver un objeto Usuario si es único
    #             else:
    #                 return [cls(**item) for item in resultado]  # Devolver una lista de objetos Usuario
    #         else:
    #             return cls(**resultado.__dict__)  # Devolver un objeto Usuario si es único
        
    #     return None  # Devolver None si no hay resultados
    
    @classmethod
    def obtener_para_login(cls, username):
        consulta = f"SELECT * FROM {cls.tabla} WHERE username = %s;"
        resultado = cls.__conectar(consulta, (username,))

        if resultado is not None:
            if isinstance(resultado, cls):
                # Si resultado es un objeto de la clase Usuario
                usuario = resultado
                usuario.password = usuario.password  # Asignar la contraseña en su formato almacenado
                return usuario
            else:
                raise ValueError("Tipo de resultado inesperado.")

        raise ValueError("Usuario no encontrado.")
    
    # @classmethod
    # def obtener_para_login(cls, username):
    #     consulta = f"SELECT * FROM {cls.tabla} WHERE username = %s"
    #     with cls.conexion.cursor() as cursor:
    #         cursor.execute(consulta, (username,))
    #         resultado = cursor.fetchone()
    #         if resultado:
    #             return cls(*resultado, de_bbdd=True)
    #         return None    
