# experimento.py
import random, time, pandas as pd, matplotlib.pyplot as plt
from simulador_disco import SimuladorDisco
from arbol_bst import ArbolBST
from arbol_bplus import ArbolBPlus

def ejecutar_prueba(n_claves=5000, n_busquedas=2000, orden_bpt=64,
                    cache_bloques=0, latencia_ms=0.0):
    disco_bst = SimuladorDisco(cache_bloques)
    disco_bpt = SimuladorDisco(cache_bloques)
    bst = ArbolBST(disco_bst)
    bpt = ArbolBPlus(disco_bpt, orden=orden_bpt)

    claves = list(range(n_claves))
    random.shuffle(claves)

    # inserciones
    t0 = time.perf_counter()
    for k in claves: bst.insertar(k)
    t_cpu_bst_ins = time.perf_counter() - t0

    t0 = time.perf_counter()
    for k in claves: bpt.insertar(k)
    t_cpu_bpt_ins = time.perf_counter() - t0

    # búsquedas
    buscar = [random.randint(0, 2 * n_claves) for _ in range(n_busquedas)]

    t0 = time.perf_counter()
    encontrados_bst = sum(bst.buscar(k) for k in buscar)
    t_cpu_bst_bus = time.perf_counter() - t0

    t0 = time.perf_counter()
    encontrados_bpt = sum(bpt.buscar(k) for k in buscar)
    t_cpu_bpt_bus = time.perf_counter() - t0

    # estadísticas
    stats_bst = disco_bst.estadisticas()
    stats_bpt = disco_bpt.estadisticas()
    lat_s = latencia_ms / 1000.0
    sim_bst = (stats_bst['lecturas'] + stats_bst['escrituras']) * lat_s + t_cpu_bst_ins + t_cpu_bst_bus
    sim_bpt = (stats_bpt['lecturas'] + stats_bpt['escrituras']) * lat_s + t_cpu_bpt_ins + t_cpu_bpt_bus

    return dict(
        n_claves=n_claves, n_busquedas=n_busquedas, orden_bpt=orden_bpt,
        cache_bloques=cache_bloques, latencia_ms=latencia_ms,
        bst_lect=stats_bst['lecturas'], bst_escr=stats_bst['escrituras'],
        bpt_lect=stats_bpt['lecturas'], bpt_escr=stats_bpt['escrituras'],
        bpt_aciertos=stats_bpt['aciertos'],
        bst_cpu=t_cpu_bst_ins + t_cpu_bst_bus,
        bpt_cpu=t_cpu_bpt_ins + t_cpu_bpt_bus,
        bst_sim=sim_bst, bpt_sim=sim_bpt,
        bst_encontrados=encontrados_bst, bpt_encontrados=encontrados_bpt,
        bst_bloques=stats_bst['total_bloques'], bpt_bloques=stats_bpt['total_bloques'],
    )

# ---------- lanzar ----------
parametros = [
    (5000, 2000, 3, 0, 0.0),
    (5000, 2000, 64, 0, 0.0),
    (5000, 2000, 3, 0, 5.0),
    (5000, 2000, 64, 0, 5.0),
    (5000, 2000, 64, 100, 5.0),
]

resultados = [ejecutar_prueba(*p) for p in parametros]
df = pd.DataFrame(resultados)
print(df)

# gráfico
plt.figure(figsize=(8, 4))
x = range(len(resultados))
plt.plot(x, df['bst_sim'], marker='o', label='BST tiempo simulado')
plt.plot(x, df['bpt_sim'], marker='o', label='B+ Tree tiempo simulado')
plt.xticks(x, [f'exp{i}' for i in x])
plt.ylabel('Tiempo simulado (s)')
plt.legend()
plt.tight_layout()
plt.show()