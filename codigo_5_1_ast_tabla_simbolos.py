# ==============================================================================
# PROGRAMACIÓN DE SISTEMAS DE BASE II
# PRÁCTICA INTEGRADORA: ÁRBOLES DE SINTAXIS ABSTRACTA (AST) + TABLA DE SÍMBOLOS
# Modalidad: POO Nativa Pura en Python (Sin librerías externas)
# ==============================================================================

class ErrorSemantico(Exception):
  """Excepción base para errores semánticos."""

  pass


class ErrorRedeclaracion(ErrorSemantico):
  """Error al intentar redeclarar una variable en el mismo ámbito."""

  pass


class ErrorVariableNoDeclarada(ErrorSemantico):
  """Error al intentar usar una variable no existente en el contexto."""

  pass


class ErrorTipoIncompatible(ErrorSemantico):
  """Error al operar o asignar tipos de datos incompatibles."""

  pass


# ------------------------------------------------------------------------------
# 1. MÓDULO DE LA TABLA DE SÍMBOLOS Y ÁMBITOS
# ------------------------------------------------------------------------------
class Simbolo:

  def __init__(
      self, nombre, tipo_dato, valor=None, categoria="variable", offset=0
  ):
    self.nombre = nombre
    self.tipo_dato = tipo_dato  # 'int', 'float', 'string'
    self.valor = valor
    self.categoria = categoria
    self.offset = offset

  def __repr__(self):
    return (
        f"Simbolo('{self.nombre}', tipo='{self.tipo_dato}', val={self.valor},"
        f" offset={self.offset})"
    )


class EntornoAmbito:

  def __init__(self, id_bloque, padre=None, nivel=0):
    self.id_bloque = id_bloque
    self.padre = padre
    self.nivel = nivel
    self.tabla_local = {}

  def insertar_local(self, simbolo):
    if simbolo.nombre in self.tabla_local:
      raise ErrorRedeclaracion(
          f"Error Semántico [Bloque {self.id_bloque}]: Redeclaración ilegal de"
          f" la variable '{simbolo.nombre}' en el mismo ámbito."
      )
    self.tabla_local[simbolo.nombre] = simbolo

  def buscar_local(self, nombre):
    return self.tabla_local.get(nombre, None)


class TablaSimbolosJerarquica:

  def __init__(self):
    self.contador_bloques = 0
    self.ambito_global = EntornoAmbito(id_bloque=0, padre=None, nivel=0)
    self.ambito_actual = self.ambito_global
    self.offset_acumulado = 0

  def abrir_bloque(self, etiqueta=""):
    self.contador_bloques += 1
    nuevo_entorno = EntornoAmbito(
        id_bloque=self.contador_bloques,
        padre=self.ambito_actual,
        nivel=self.ambito_actual.nivel + 1,
    )
    self.ambito_actual = nuevo_entorno
    tag = f" ({etiqueta})" if etiqueta else ""
    print(
        f"\n[+] ABRIR BLOQUE {self.contador_bloques}{tag} | Nivel"
        f" {nuevo_entorno.nivel}"
    )

  def cerrar_bloque(self):
    if self.ambito_actual.padre is None:
      raise ErrorSemantico("No se puede cerrar el ámbito global.")
    print(
        f"[-] CERRAR BLOQUE {self.ambito_actual.id_bloque} | Retornando a"
        f" Nivel {self.ambito_actual.padre.nivel}"
    )
    self.ambito_actual = self.ambito_actual.padre

  def declarar(self, nombre, tipo_dato, valor_inicial=None, tamano=4):
    simbolo = Simbolo(nombre, tipo_dato, valor_inicial, offset=self.offset_acumulado)
    self.ambito_actual.insertar_local(simbolo)
    self.offset_acumulado += tamano
    print(
        f"   ✓ DECLARACIÓN: Variable '{nombre}' ({tipo_dato}) registrada en"
        f" Bloque {self.ambito_actual.id_bloque}"
    )
    return simbolo

  def buscar(self, nombre):
    cursor = self.ambito_actual
    while cursor is not None:
      simbolo = cursor.buscar_local(nombre)
      if simbolo is not None:
        return simbolo
      cursor = cursor.padre
    raise ErrorVariableNoDeclarada(
        f"Error Semántico [Bloque {self.ambito_actual.id_bloque}]: La variable"
        f" '{nombre}' no ha sido declarada en el ámbito activo ni en sus"
        " contenedores."
    )


# ------------------------------------------------------------------------------
# 2. MÓDULO DEL ÁRBOL DE SINTAXIS ABSTRACTA (AST) CON VALIDACIÓN SEMÁNTICA
# ------------------------------------------------------------------------------
class NodoAST:

  def evaluar(self, ts):
    raise NotImplementedError


class Numero(NodoAST):

  def __init__(self, valor):
    self.valor = valor
    self.tipo_dato = "int" if isinstance(valor, int) else "float"

  def evaluar(self, ts):
    return self.valor, self.tipo_dato


class Variable(NodoAST):

  def __init__(self, nombre):
    self.nombre = nombre

  def evaluar(self, ts):
    simbolo = ts.buscar(self.nombre)
    if simbolo.valor is None:
      raise ErrorSemantico(
          f"Error Semántico: La variable '{self.nombre}' no ha sido"
          " inicializada."
      )
    return simbolo.valor, simbolo.tipo_dato


class Operador(NodoAST):

  def __init__(self, operador, izq, der):
    self.operador = operador
    self.izq = izq
    self.der = der

  def evaluar(self, ts):
    val_izq, tipo_izq = self.izq.evaluar(ts)
    val_der, tipo_der = self.der.evaluar(ts)

    if tipo_izq == "string" or tipo_der == "string":
      raise ErrorTipoIncompatible(
          f"Error Semántico de Tipos: Operación '{self.operador}' no permitida"
          f" entre '{tipo_izq}' y '{tipo_der}'."
      )

    tipo_resultante = (
        "float" if (tipo_izq == "float" or tipo_der == "float") else "int"
    )

    if self.operador == "+":
      res = val_izq + val_der
    elif self.operador == "-":
      res = val_izq - val_der
    elif self.operador == "*":
      res = val_izq * val_der
    elif self.operador == "/":
      if val_der == 0:
        raise ZeroDivisionError(
            "Error Semántico/Aritmético: División entre cero."
        )
      res = val_izq / val_der
      tipo_resultante = "float"

    return res, tipo_resultante


class Declaracion(NodoAST):

  def __init__(self, nombre, tipo_declarado, expresion_inicial=None):
    self.nombre = nombre
    self.tipo_declarado = tipo_declarado
    self.expresion_inicial = expresion_inicial

  def evaluar(self, ts):
    val_expr = None
    if self.expresion_inicial is not None:
      val_expr, tipo_expr = self.expresion_inicial.evaluar(ts)
      if self.tipo_declarado == "int" and tipo_expr == "string":
        raise ErrorTipoIncompatible(
            "Error Semántico de Tipos: No se puede inicializar variable 'int'"
            " con 'string'."
        )
    simbolo = ts.declarar(self.nombre, self.tipo_declarado, val_expr)
    return val_expr, self.tipo_declarado


class Asignacion(NodoAST):

  def __init__(self, nombre_var, expresion):
    self.nombre_var = nombre_var
    self.expresion = expresion

  def evaluar(self, ts):
    simbolo = ts.buscar(self.nombre_var)
    val_expr, tipo_expr = self.expresion.evaluar(ts)

    if simbolo.tipo_dato == "int" and tipo_expr == "string":
      raise ErrorTipoIncompatible(
          f"Error Semántico de Tipos: No se puede asignar 'string' a la"
          f" variable '{self.nombre_var}' de tipo '{simbolo.tipo_dato}'."
      )
    elif simbolo.tipo_dato == "int" and tipo_expr == "float":
      print(
          "   [COERCIÓN ADVERTENCIA]: Truncando 'float' a 'int' para asignación"
          f" en '{self.nombre_var}'"
      )
      val_expr = int(val_expr)

    simbolo.valor = val_expr
    print(
        f"   ✓ ASIGNACIÓN EXITOSA: {self.nombre_var} = {val_expr} (Tipo:"
        f" {simbolo.tipo_dato})"
    )
    return val_expr, simbolo.tipo_dato


class BloqueAST(NodoAST):

  def __init__(self, instrucciones, etiqueta=""):
    self.instrucciones = instrucciones
    self.etiqueta = etiqueta

  def evaluar(self, ts):
    ts.abrir_bloque(self.etiqueta)
    ultimo_res = None
    for instr in self.instrucciones:
      ultimo_res = instr.evaluar(ts)
    ts.cerrar_bloque()
    return ultimo_res


# ------------------------------------------------------------------------------
# 3. DEMOSTRACIÓN DE EJECUCIÓN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  ts = TablaSimbolosJerarquica()

  # Variables globales
  ts.declarar("global_a", "int", 10)
  ts.declarar("global_b", "float", 20.5)

  # AST de un programa con bloques anidados
  programa = BloqueAST(
      [
          Declaracion(
              "x", "int", Operador("*", Variable("global_a"), Numero(2))
          ),
          Asignacion("x", Operador("+", Variable("x"), Numero(5))),
          BloqueAST(
              [Declaracion("x", "float", Numero(3.14))],
              etiqueta="Bloque Anidado",
          ),
      ],
      etiqueta="Programa Principal",
  )

  print(
      "--- Ejecutando Evaluación del AST e Integración con Tabla de Símbolos"
      " ---"
  )
  programa.evaluar(ts)

  print("\n--- Pruebas de Captura de Errores Semánticos ---")
  # Captura de error: Operación int + string
  try:
    ts.declarar("texto", "string", "hola")
    err = Operador("+", Variable("global_a"), Variable("texto"))
    err.evaluar(ts)
  except ErrorTipoIncompatible as e:
    print(f"   [CAPTURADO ÉXITO]: {e}")
