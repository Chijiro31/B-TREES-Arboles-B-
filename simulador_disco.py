from collections import OrderedDict

class SimuladorDisco:
    def __init__(self, cache_bloques: int = 0):
        self.bloques = {}
        self.siguiente_id = 1
        self.lecturas = 0
        self.escrituras = 0
        self.tam_cache = cache_bloques
        self.cache = OrderedDict() if cache_bloques else None
        self.aciertos = 0
        self.fallos = 0

    def nuevo_bloque(self, objeto) -> int:
        bid = self.siguiente_id
        self.siguiente_id += 1
        self.bloques[bid] = objeto
        self.escrituras += 1
        self._meter_en_cache(bid, objeto)
        return bid

    def leer_bloque(self, bid: int):
        if self.cache is not None:
            if bid in self.cache:
                self.cache.move_to_end(bid)
                self.aciertos += 1
                return self.cache[bid]
            self.fallos += 1
        self.lecturas += 1
        obj = self.bloques.get(bid)
        if obj is not None:
            self._meter_en_cache(bid, obj)
        return obj

    def escribir_bloque(self, bid: int, objeto):
        self.bloques[bid] = objeto
        self.escrituras += 1
        self._meter_en_cache(bid, objeto)

    def _meter_en_cache(self, bid, obj):
        if self.cache is None:
            return
        self.cache[bid] = obj
        if len(self.cache) > self.tam_cache:
            self.cache.popitem(last=False)

    def reiniciar_contadores(self):
        self.lecturas = self.escrituras = self.aciertos = self.fallos = 0

    def estadisticas(self):
        return dict(lecturas=self.lecturas,
                    escrituras=self.escrituras,
                    aciertos=self.aciertos,
                    fallos=self.fallos,
                    total_bloques=len(self.bloques))