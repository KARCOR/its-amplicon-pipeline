"""Índices de diversidad alfa: Shannon y Simpson.

Fórmulas estándar (ver README y estandares_industria_ITS.md para las citas
completas). Extraídas del notebook a funciones puras y testeadas: antes
vivían como `def` dentro de una celda, sin ninguna prueba automática de que
devuelven el valor correcto.
"""

import numpy as np
import pandas as pd


def shannon_index(counts):
    """Índice de Shannon-Wiener: H' = -sum(p_i * ln(p_i))."""
    counts = np.asarray(counts)
    counts = counts[counts > 0]
    if counts.sum() == 0:
        return 0.0
    p = counts / counts.sum()
    return -np.sum(p * np.log(p))


def simpson_index(counts):
    """Índice de Simpson invertido (Gini-Simpson): 1 - sum(p_i^2)."""
    counts = np.asarray(counts)
    counts = counts[counts > 0]
    if counts.sum() == 0:
        return 0.0
    p = counts / counts.sum()
    return 1 - np.sum(p ** 2)


def calcular_diversidad(asv_table):
    """Calcula Shannon, Simpson y riqueza observada por muestra (fila) de una tabla ASV."""
    return pd.DataFrame({
        "Shannon": asv_table.apply(shannon_index, axis=1),
        "Simpson": asv_table.apply(simpson_index, axis=1),
        "Riqueza_observada": (asv_table > 0).sum(axis=1),
    })
