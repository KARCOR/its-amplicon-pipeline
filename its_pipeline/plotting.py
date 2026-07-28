"""Utilidades de visualización compartidas por el notebook.

Existen para que los gráficos no dependan de una paleta de colores escrita a
mano para 3 muestras exactas (`{"it-its_1": "#2563eb", ...}`) — con eso, el
notebook fallaba con `KeyError` en cuanto se usaba un nombre de muestra
distinto. `generar_paleta` asigna un color a cualquier lista de muestras,
sea de longitud 3 o 300.
"""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


def generar_paleta(muestras, colormap="tab20"):
    """Genera un color distinto por muestra a partir de un colormap de matplotlib.

    Parameters
    ----------
    muestras : list[str]
        Nombres de muestra, en cualquier cantidad.
    colormap : str
        Nombre de un colormap categórico de matplotlib. "tab20" da 20 colores
        distinguibles; con más de 20 muestras los colores se reciclan (con
        muchas muestras, de todas formas se recomienda no depender de leyenda
        individual — ver `config.LIMITE_MUESTRAS_PARA_ETIQUETAS`).

    Returns
    -------
    dict[str, str]
        Mapeo muestra -> color en formato hexadecimal.
    """
    cmap = plt.get_cmap(colormap)
    return {m: mcolors.to_hex(cmap(i % cmap.N)) for i, m in enumerate(muestras)}
