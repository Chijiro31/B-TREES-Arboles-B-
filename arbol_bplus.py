from simulador_disco import SimuladorDisco

class NodoBPlus:
    def __init__(self, es_hoja=False):
        self.es_hoja = es_hoja
        self.claves = []
        self.hijos = []          # ids de bloques (interno) o vacío (hoja)
        self.siguiente = None    # solo hojas

class ArbolBPlus:
    def __init__(self, disco: SimuladorDisco, orden: int = 32):
        if orden < 3:
            raise ValueError("orden debe ser >=3")
        self.disco = disco
        self.orden = orden
        self.raiz = self._nueva_hoja()

    # ---------- helpers ----------
    def _nueva_hoja(self) -> int:
        return self.disco.nuevo_bloque(NodoBPlus(es_hoja=True))

    def _nuevo_interno(self) -> int:
        return self.disco.nuevo_bloque(NodoBPlus(es_hoja=False))

    def _leer(self, bid: int):
        return self.disco.leer_bloque(bid)

    def _escribir(self, bid: int, nodo):
        self.disco.escribir_bloque(bid, nodo)

    # ---------- búsqueda ----------
    def buscar(self, clave: int) -> bool:
        actual = self.raiz
        while True:
            nodo = self._leer(actual)
            if nodo.es_hoja:
                return clave in nodo.claves
            i = 0
            while i < len(nodo.claves) and clave >= nodo.claves[i]:
                i += 1
            actual = nodo.hijos[i]

    # ---------- inserción ----------
    def insertar(self, clave: int):
        # 1) encontrar hoja
        pila = []  # (bid, nodo, idx_hijo)
        actual = self.raiz
        while True:
            nodo = self._leer(actual)
            if nodo.es_hoja:
                break
            i = 0
            while i < len(nodo.claves) and clave >= nodo.claves[i]:
                i += 1
            pila.append((actual, nodo, i))
            actual = nodo.hijos[i]

        # 2) insertar en hoja
        self._insertar_en_hoja(actual, clave)

        # 3) subir si hace falta
        while pila:
            padre_id, padre, idx_hijo = pila.pop()
            hijo_id = padre.hijos[idx_hijo]
            hijo = self._leer(hijo_id)
            if len(hijo.claves) <= self.orden - 1:
                break  # sin overflow
            self._split_hijo(padre_id, padre, idx_hijo, hijo_id, hijo)

        # 4) posible split de raíz
        raiz_nodo = self._leer(self.raiz)
        if len(raiz_nodo.claves) > self.orden - 1:
            self._split_raiz(raiz_nodo)

    # ---------- insertar en hoja ----------
    def _insertar_en_hoja(self, hoja_id: int, clave: int):
        hoja = self._leer(hoja_id)
        i = 0
        while i < len(hoja.claves) and hoja.claves[i] < clave:
            i += 1
        hoja.claves.insert(i, clave)
        self._escribir(hoja_id, hoja)

    # ---------- split de hijo ----------
    def _split_hijo(self, padre_id, padre, idx_hijo, hijo_id, hijo):
        mitad = len(hijo.claves) // 2
        if hijo.es_hoja:
            nueva_hoja = NodoBPlus(es_hoja=True)
            nueva_hoja.claves = hijo.claves[mitad:]
            nueva_hoja.siguiente = hijo.siguiente
            hijo.claves = hijo.claves[:mitad]
            hijo.siguiente = self.disco.nuevo_bloque(nueva_hoja)
            self._escribir(hijo_id, hijo)
            # subir copia
            clave_subir = nueva_hoja.claves[0]
            padre.claves.insert(idx_hijo, clave_subir)
            padre.hijos.insert(idx_hijo + 1, hijo.siguiente)
            self._escribir(padre_id, padre)
        else:
            nueva_int = NodoBPlus(es_hoja=False)
            clave_subir = hijo.claves[mitad]
            nueva_int.claves = hijo.claves[mitad + 1:]
            nueva_int.hijos = hijo.hijos[mitad + 1:]
            hijo.claves = hijo.claves[:mitad]
            hijo.hijos = hijo.hijos[:mitad + 1]
            self._escribir(hijo_id, hijo)
            nuevo_id = self.disco.nuevo_bloque(nueva_int)
            padre.claves.insert(idx_hijo, clave_subir)
            padre.hijos.insert(idx_hijo + 1, nuevo_id)
            self._escribir(padre_id, padre)

    # ---------- split de raíz ----------
    def _split_raiz(self, raiz_nodo):
        mitad = len(raiz_nodo.claves) // 2
        if raiz_nodo.es_hoja:
            nueva_hoja = NodoBPlus(es_hoja=True)
            nueva_hoja.claves = raiz_nodo.claves[mitad:]
            nueva_hoja.siguiente = raiz_nodo.siguiente
            raiz_nodo.claves = raiz_nodo.claves[:mitad]
            raiz_nodo.siguiente = self.disco.nuevo_bloque(nueva_hoja)
            self._escribir(self.raiz, raiz_nodo)
            # nueva raíz interna
            nueva_raiz = NodoBPlus(es_hoja=False)
            nueva_raiz.claves = [nueva_hoja.claves[0]]
            nueva_raiz.hijos = [self.raiz, raiz_nodo.siguiente]
            self.raiz = self.disco.nuevo_bloque(nueva_raiz)
        else:
            clave_subir = raiz_nodo.claves[mitad]
            nueva_int = NodoBPlus(es_hoja=False)
            nueva_int.claves = raiz_nodo.claves[mitad + 1:]
            nueva_int.hijos = raiz_nodo.hijos[mitad + 1:]
            raiz_nodo.claves = raiz_nodo.claves[:mitad]
            raiz_nodo.hijos = raiz_nodo.hijos[:mitad + 1]
            self._escribir(self.raiz, raiz_nodo)
            nuevo_id = self.disco.nuevo_bloque(nueva_int)
            nueva_raiz = NodoBPlus(es_hoja=False)
            nueva_raiz.claves = [clave_subir]
            nueva_raiz.hijos = [self.raiz, nuevo_id]
            self.raiz = self.disco.nuevo_bloque(nueva_raiz)