# ==============================================================================
# PROGRAMACIÓN DE SISTEMAS DE BASE II
# SIMULACIÓN DE PILA SEMÁNTICA Y EVALUACIÓN "ON-THE-FLY" (AL VUELO) EN PYTHON
# ==============================================================================

class ElementoPila:
    """Estructura de la tupla/registro de la Pila Semántica: (estado, simbolo, atributo)"""
    def __init__(self, estado, simbolo, atributo=None):
        self.estado = estado
        self.simbolo = simbolo
        self.atributo = atributo  # Almacena tipos, valores o temporales

    def __repr__(self):
        val_str = f", attr={self.atributo}" if self.atributo is not None else ""
        return f"[{self.estado}: {self.simbolo}{val_str}]"


class SimulacionPilaSemantica:
    """
    Simula un analizador ascendente (LR) con Pila Semántica paralela
    que realiza la evaluación 'On-the-Fly' (al vuelo) generando Código de
    Tres Direcciones (3AC) sin construir un árbol sintáctico explícito en memoria.
    """
    def __init__(self):
        self.pila = [ElementoPila(0, '$')]  # Estado inicial 0 con centinela $
        self.contador_temporales = 0
        self.codigo_intermedio = []

    def nuevo_temporal(self):
        self.contador_temporales += 1
        return f"t{self.contador_temporales}"

    def emitir(self, instruccion):
        self.codigo_intermedio.append(instruccion)
        print(f"   ⚡ [ON-THE-FLY EMISIÓN]: {instruccion}")

    def mostrar_pila(self):
        pila_str = " ".join([str(elem) for elem in self.pila])
        print(f"PILA: {pila_str}")

    def desplazar(self, nuevo_estado, simbolo, atributo=None):
        """Operación Shift: Apila el estado, el símbolo y su atributo léxico ($1, $2...)"""
        elem = ElementoPila(nuevo_estado, simbolo, atributo)
        self.pila.append(elem)
        print(f"\n---> DESPLAZAR (Shift): Token '{simbolo}' (Atributo: {atributo}) -> Estado {nuevo_estado}")
        self.mostrar_pila()

    def reducir(self, num_regla, antecedente, num_simbolos_cuerpo, accion_semantica_fn, nuevo_estado_ir_a):
        """
        Operación Reduce:
        1. Desapila los 'num_simbolos_cuerpo' elementos de la regla.
        2. Accede a sus atributos ($1, $2, ..., $n).
        3. Ejecuta la acción semántica On-the-Fly ($$).
        4. Apila el antecedente con su nuevo atributo ($$) y el estado IR_A.
        """
        print(f"\n<--- REDUCIR (Reduce R{num_regla}): {antecedente} -> ({num_simbolos_cuerpo} símbolos)")
        
        # Extraer operandos del cuerpo de la regla desde la pila
        elementos_extraidos = []
        for _ in range(num_simbolos_cuerpo):
            elementos_extraidos.insert(0, self.pila.pop())
        
        # Los atributos extraídos corresponden a $1, $2, ..., $n
        atributos_cuerpo = [elem.atributo for elem in elementos_extraidos]
        print(f"   Atributos desapilados ($1..${num_simbolos_cuerpo}): {atributos_cuerpo}")

        # Ejecución de la acción semántica On-the-fly para calcular $$
        atributo_sintetizado = accion_semantica_fn(atributos_cuerpo)

        # Apilar antecedente con el estado indicado por la tabla IR_A
        self.pila.append(ElementoPila(nuevo_estado_ir_a, antecedente, atributo_sintetizado))
        print(f"   Resultado sintetizado ($$ = {atributo_sintetizado}) apilado en estado {nuevo_estado_ir_a}")
        self.mostrar_pila()
# ==============================================================================
# EJECUCIÓN PASO A PASO DE LA SIMULACIÓN
# Cadena de entrada: "a + b * 5"
# Gramática y Reglas Semánticas:
#  (1) E -> E + T   { $$ = nuevo_temp(); emitir($$ = $1 + $3); }
#  (2) E -> T       { $$ = $1; }
#  (3) T -> T * F   { $$ = nuevo_temp(); emitir($$ = $1 * $3); }
#  (4) T -> F       { $$ = $1; }
#  (5) F -> id      { $$ = $1.nombre; }
#  (6) F -> num     { $$ = $1.valor; }
# ==============================================================================

if __name__ == "__main__":
    sim = SimulacionPilaSemantica()
    print("=" * 70)
    print("SIMULACIÓN DE LA PILA SEMÁNTICA Y TRADUCCIÓN ON-THE-FLY DE 'a + b * 5'")
    print("=" * 70)
    sim.mostrar_pila()

    # 1. Shift 'id' (a)
    sim.desplazar(nuevo_estado=3, simbolo='id', atributo='a')

    # 2. Reduce (5) F -> id
    sim.reducir(
        num_regla=5, antecedente='F', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('a')
        nuevo_estado_ir_a=2
    )

    # 3. Reduce (4) T -> F
    sim.reducir(
        num_regla=4, antecedente='T', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('a')
        nuevo_estado_ir_a=1
    )

    # 4. Reduce (2) E -> T
    sim.reducir(
        num_regla=2, antecedente='E', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('a')
        nuevo_estado_ir_a=4
    )

    # 5. Shift '+'
    sim.desplazar(nuevo_estado=6, simbolo='+')

    # 6. Shift 'id' (b)
    sim.desplazar(nuevo_estado=3, simbolo='id', atributo='b')

    # 7. Reduce (5) F -> id
    sim.reducir(
        num_regla=5, antecedente='F', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('b')
        nuevo_estado_ir_a=2
    )

    # 8. Reduce (4) T -> F
    sim.reducir(
        num_regla=4, antecedente='T', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('b')
        nuevo_estado_ir_a=7
    )

    # 9. Shift '*'
    sim.desplazar(nuevo_estado=8, simbolo='*')

    # 10. Shift 'num' (5)
    sim.desplazar(nuevo_estado=5, simbolo='num', atributo='5')

    # 11. Reduce (6) F -> num
    sim.reducir(
        num_regla=6, antecedente='F', num_simbolos_cuerpo=1,
        accion_semantica_fn=lambda attrs: attrs[0],  # $$ = $1 ('5')
        nuevo_estado_ir_a=9
    )

    # 12. Reduce (3) T -> T * F (Acción con emisión de código On-The-Fly)
    def accion_multiplicacion(attrs):
        t = sim.nuevo_temporal()
        sim.emitir(f"{t} = {attrs[0]} * {attrs[2]}")  # $1 * $3
        return t

    sim.reducir(
        num_regla=3, antecedente='T', num_simbolos_cuerpo=3,
        accion_semantica_fn=accion_multiplicacion,
        nuevo_estado_ir_a=7
    )

    # 13. Reduce (1) E -> E + T (Acción con emisión de código On-The-Fly)
    def accion_suma(attrs):
        t = sim.nuevo_temporal()
        sim.emitir(f"{t} = {attrs[0]} + {attrs[2]}")  # $1 + $3
        return t

    sim.reducir(
        num_regla=1, antecedente='E', num_simbolos_cuerpo=3,
        accion_semantica_fn=accion_suma,
        nuevo_estado_ir_a=4
    )

    print("\n" + "=" * 70)
    print("CÓDIGO DE TRES DIRECCIONES GENERADO ON-THE-FLY:")
    print("=" * 70)
    for i, inst in enumerate(sim.codigo_intermedio, 1):
        print(f" {i}. {inst}")
    print("=" * 70)
