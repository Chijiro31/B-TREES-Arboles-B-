from simulador_disco import SimuladorDisco

class NodoBST:
    def __init__(self, clave, izq=None, der=None):
        self.clave = clave
        self.izq = izq   # id bloque
        self.der = der   # id bloque

class ArbolBST:
    def __init__(self, disco: SimuladorDisco):
        self.disco = disco
        self.raiz = None

    def insertar(self, clave: int):
        if self.raiz is None:
            self.raiz = self.disco.nuevo_bloque(NodoBST(clave))
            return
        actual = self.raiz
        while True:
            nodo = self.disco.leer_bloque(actual)
            if clave < nodo.clave:
                if nodo.izq is None:
                    nuevo_id = self.disco.nuevo_bloque(NodoBST(clave))
                    nodo.izq = nuevo_id
                    self.disco.escribir_bloque(actual, nodo)
                    return
                actual = nodo.izq
            else:
                if nodo.der is None:
                    nuevo_id = self.disco.nuevo_bloque(NodoBST(clave))
                    nodo.der = nuevo_id
                    self.disco.escribir_bloque(actual, nodo)
                    return
                actual = nodo.der

    def buscar(self, clave: int) -> bool:
        actual = self.raiz
        while actual:
            nodo = self.disco.leer_bloque(actual)
            if nodo is None:
                return False
            if clave == nodo.clave:
                return True
            actual = nodo.izq if clave < nodo.clave else nodo.der
        return False