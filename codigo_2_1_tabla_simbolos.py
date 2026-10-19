# ==============================================================================
# PROGRAMACIÓN DE SISTEMAS DE BASE II
# IMPLEMENTACIÓN DE LA TABLA DE SÍMBOLOS JERÁRQUICA Y VERIFICADOR DE ERRORES SEMÁNTICOS
# Modalidad: POO Nativa Pura en Python (Sin librerías externas)
# ==============================================================================

class ErrorSemantico(Exception):
    """Clase base para excepciones semánticas personalizadas."""
    pass

class ErrorRedeclaracion(ErrorSemantico):
    """Excepción para cuando una variable ya fue declarada en el mismo ámbito."""
    pass

class ErrorVariableNoDeclarada(ErrorSemantico):
    """Excepción para cuando se intenta acceder a una variable inexistente en el contexto."""
    pass


class Simbolo:
    """Representa la información asociada a un identificador dentro de la Tabla de Símbolos."""
    def __init__(self, nombre, tipo_dato, categoria="variable", direccion_offset=0):
        self.nombre = nombre
        self.tipo_dato = tipo_dato          # ej. 'int', 'float', 'string'
        self.categoria = categoria          # ej. 'variable', 'parametro', 'constante'
        self.direccion_offset = direccion_offset  # Dirección de memoria relativa

    def __repr__(self):
        return f"Simbolo('{self.nombre}', tipo='{self.tipo_dato}', cat='{self.categoria}', offset={self.direccion_offset})"


class EntornoAmbito:
    """
    Representa un bloque o ámbito local específico dentro del programa.
    Mantiene un diccionario local de símbolos y una referencia a su entorno padre.
    """
    def __init__(self, id_bloque, padre=None, nivel_profundidad=0):
        self.id_bloque = id_bloque
        self.padre = padre                  # Entorno del bloque contenedor (padre)
        self.nivel_profundidad = nivel_profundidad
        self.tabla_local = {}               # Diccionario de identificadores locales

    def insertar_local(self, simbolo):
        """Inserta un símbolo en la tabla local si no existe previamente en este mismo bloque."""
        if simbolo.nombre in self.tabla_local:
            raise ErrorRedeclaracion(
                f"Error Semántico [Bloque {self.id_bloque}, Nivel {self.nivel_profundidad}]: "
                f"Redeclaración ilegal de la variable '{simbolo.nombre}' en el mismo ámbito local."
            )
        self.tabla_local[simbolo.nombre] = simbolo

    def buscar_local(self, nombre):
        """Busca un símbolo únicamente dentro del ámbito local actual."""
        return self.tabla_local.get(nombre, None)


class TablaSimbolosJerarquica:
    """
    Administrador central de la Tabla de Símbolos Jerárquica con soporte
    para bloques anidados y pila de entornos.
    """
    def __init__(self):
        self.contador_bloques = 0
        # Ámbito global inicial (Bloque 0, Nivel 0)
        self.ambito_global = EntornoAmbito(id_bloque=0, padre=None, nivel_profundidad=0)
        self.ambito_actual = self.ambito_global
        self.offset_acumulado = 0  # Gestor de direcciones relativas de memoria

    def abrir_bloque(self, nombre_contexto=""):
        """Abre un nuevo bloque anidado y actualiza el entorno activo."""
        self.contador_bloques += 1
        nuevo_nivel = self.ambito_actual.nivel_profundidad + 1
        nuevo_entorno = EntornoAmbito(
            id_bloque=self.contador_bloques,
            padre=self.ambito_actual,
            nivel_profundidad=nuevo_nivel
        )
        self.ambito_actual = nuevo_entorno
        tag = f" ({nombre_contexto})" if nombre_contexto else ""
        print(f"\n[+] ABRIR BLOQUE {self.contador_bloques}{tag} | Nivel de profundidad: {nuevo_nivel}")

    def cerrar_bloque(self):
        """Cierra el bloque actual y retorna al entorno padre."""
        if self.ambito_actual.padre is None:
            raise ErrorSemantico("Error: Intentando cerrar el ámbito global del programa.")

        print(f"\n[-] CERRAR BLOQUE {self.ambito_actual.id_bloque} | Retornando a Nivel {self.ambito_actual.padre.nivel_profundidad}")
        self.ambito_actual = self.ambito_actual.padre

    def insertar(self, nombre, tipo_dato, categoria="variable", tamano_bytes=4):
        """Inserta un nuevo símbolo en el ámbito local actual y calcula su dirección offset."""
        simbolo = Simbolo(nombre, tipo_dato, categoria, self.offset_acumulado)
        self.ambito_actual.insertar_local(simbolo)
        self.offset_acumulado += tamano_bytes
        print(f"   ✓ SIMBOLO REGISTRADO: '{nombre}' -> {simbolo} (Ámbito {self.ambito_actual.id_bloque})")
        return simbolo

    def buscar(self, nombre):
        """Busca un símbolo desde el ámbito actual ascendiendo por la jerarquía de padres (Scoping Léxico)."""
        entorno_cursor = self.ambito_actual
        while entorno_cursor is not None:
            simbolo = entorno_cursor.buscar_local(nombre)
            if simbolo is not None:
                print(f"   🔍 BUSQUEDA EXITOSA: '{nombre}' encontrado en Bloque {entorno_cursor.id_bloque} (Nivel {entorno_cursor.nivel_profundidad}) -> {simbolo}")
                return simbolo
            entorno_cursor = entorno_cursor.padre

        raise ErrorVariableNoDeclarada(
            f"Error Semántico [Bloque {self.ambito_actual.id_bloque}]: "
            f"La variable '{nombre}' no ha sido declarada en el ámbito activo ni en sus ámbitos contenedores."
        )

    def mostrar_cadena_ambitos(self):
        """Muestra los bloques actualmente activos desde la cima local hasta el ámbito global."""
        print("\n" + "=" * 70)
        print("ESTADO ACTUAL DE LA CADENA DE ÁMBITOS VISIBLES:")
        print("=" * 70)
        entorno_cursor = self.ambito_actual
        while entorno_cursor is not None:
            simbolos_str = ", ".join(entorno_cursor.tabla_local.keys()) if entorno_cursor.tabla_local else "vacío"
            print(f" ► [Bloque {entorno_cursor.id_bloque} | Nivel {entorno_cursor.nivel_profundidad}] Símbolos locales: {{{simbolos_str}}}")
            entorno_cursor = entorno_cursor.padre
        print("=" * 70 + "\n")


# ==============================================================================
# ENTORNO DE DEMOSTRACIÓN Y CASOS DE PRUEBA
# ==============================================================================
if __name__ == "__main__":
    ts = TablaSimbolosJerarquica()

    print("=" * 70)
    print("DEMOSTRACIÓN: TABLA DE SÍMBOLOS CON GESTIÓN DE ÁMBITOS Y ANIDAMIENTO")
    print("=" * 70)

    # 1. Declaraciones en Ámbito Global (Bloque 0)
    print("\n--- 1. Declaraciones en Ámbito Global ---")
    ts.insertar("global_x", "int")
    ts.insertar("PI", "float", categoria="constante")
    ts.mostrar_cadena_ambitos()

    # 2. Entrada a Función principal (Bloque 1)
    ts.abrir_bloque("Funcion main")
    ts.insertar("a", "int")
    ts.insertar("b", "float")

    # Búsqueda de variable global desde dentro de main
    ts.buscar("global_x")
    ts.mostrar_cadena_ambitos()

    # 3. Entrada a Bloque Interno (Bloque 2 - IF / WHILE)
    ts.abrir_bloque("Bloque interno IF")
    ts.insertar("a", "string")  # Ocultamiento/Sombra de variable 'a' local de main
    ts.insertar("temp", "int")

    ts.mostrar_cadena_ambitos()

    # Búsquedas en ámbito anidado
    ts.buscar("a")         # Encuentra la 'a' local del Bloque 2 (string)
    ts.buscar("b")         # Encuentra la 'b' del Bloque 1 (float)
    ts.buscar("global_x")  # Encuentra 'global_x' del Bloque 0 (int)

    # 4. Prueba de Manejo de Errores Semánticos
    print("\n--- 4. Demostración de Captura de Errores Semánticos ---")

    # Error A: Redeclaración en el mismo ámbito local
    try:
        print("\n   [Prueba A] Intentando redeclarar 'temp' en el mismo bloque local...")
        ts.insertar("temp", "float")
    except ErrorRedeclaracion as e:
        print(f"     [CAPTURADO EXITO] {e}")

    # 5. Salida del Bloque Interno
    ts.cerrar_bloque()

    # Tras cerrar Bloque 2, 'temp' ya no es visible y 'a' vuelve a ser la de main (int)
    ts.buscar("a")  # Ahora encuentra la 'a' de main (int)

    # Error B: Búsqueda de variable no declarada / fuera de ámbito
    try:
        print("\n   [Prueba B] Intentando buscar 'temp' fuera de su ámbito...")
        ts.buscar("temp")
    except ErrorVariableNoDeclarada as e:
        print(f"     [CAPTURADO EXITO] {e}")

    # Salida final de la función main
    ts.cerrar_bloque()
    ts.mostrar_cadena_ambitos()
