class MaquinaDePilaAbstracta:

    def __init__(self):
        self.pila = []
        self.memoria = {}  # Simula la memoria de variables

    def ejecutar_instrucciones(self, programa):
        print("=== INICIO DE EJECUCIÓN EN MÁQUINA DE PILA ===")
        for instruccion in programa:
            partes = instruccion.split()
            op = partes[0]

            if op == "PUSH_NUM":
                val = float(partes[1])
                self.pila.append(val)
                print(f"PUSH_NUM {val:<5} -> Pila: {self.pila}")

            elif op == "LOAD_VAR":
                var_nombre = partes[1]
                val = self.memoria.get(var_nombre, 0.0)
                self.pila.append(val)
                print(f"LOAD_VAR {var_nombre:<5} ({val}) -> Pila: {self.pila}")

            elif op == "STORE_VAR":
                var_nombre = partes[1]
                val = self.pila.pop()
                self.memoria[var_nombre] = val
                print(f"STORE_VAR {var_nombre:<4} ({val}) -> Pila: {self.pila}")

            elif op in ("ADD", "SUB", "MUL", "DIV"):
                b = self.pila.pop()
                a = self.pila.pop()
                res = 0.0
                if op == "ADD":
                    res = a + b
                elif op == "SUB":
                    res = a - b
                elif op == "MUL":
                    res = a * b
                elif op == "DIV":
                    res = a / b
                self.pila.append(res)
                print(f"{op:<12} ({a} {op} {b}) -> Pila: {self.pila}")

if __name__ == "__main__":
    # Ejemplo de programa traducido a instrucciones de Máquina de Pila:
    # Corresponde a la asignación: x = 5; y = 10; resultado = (x + y) * 2
    codigo_pila = [
        "PUSH_NUM 5",
        "STORE_VAR x",
        "PUSH_NUM 10",
        "STORE_VAR y",
        "LOAD_VAR x",
        "LOAD_VAR y",
        "ADD",
        "PUSH_NUM 2",
        "MUL",
        "STORE_VAR resultado",
    ]

    vm = MaquinaDePilaAbstracta()
    vm.ejecutar_instrucciones(codigo_pila)
    print("\nEstado final de la memoria principal:", vm.memoria)
