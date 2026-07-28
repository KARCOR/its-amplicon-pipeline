"""Pruebas unitarias de los índices de diversidad alfa (its_pipeline.diversity)."""

import math

import numpy as np
import pandas as pd
import pytest

from its_pipeline.diversity import calcular_diversidad, shannon_index, simpson_index


def test_shannon_uniforme_da_ln_n():
    """Con abundancias perfectamente uniformes, Shannon = ln(n_especies)."""
    counts = np.array([10, 10, 10, 10])
    assert shannon_index(counts) == pytest.approx(math.log(4), rel=1e-9)


def test_shannon_una_sola_especie_es_cero():
    """Si solo hay una especie presente, no hay incertidumbre: H' = 0."""
    counts = np.array([50, 0, 0, 0])
    assert shannon_index(counts) == pytest.approx(0.0)


def test_shannon_ignora_ceros():
    """Los ceros no deben alterar el resultado frente a no incluirlos."""
    con_ceros = np.array([5, 0, 3, 0, 2])
    sin_ceros = np.array([5, 3, 2])
    assert shannon_index(con_ceros) == pytest.approx(shannon_index(sin_ceros))


def test_simpson_una_sola_especie_es_cero():
    """Con una sola especie, Simpson (1-D) = 0: no hay diversidad."""
    counts = np.array([100, 0, 0])
    assert simpson_index(counts) == pytest.approx(0.0)


def test_simpson_uniforme_tiende_a_uno():
    """Con muchas especies igual de abundantes, Simpson (1-D) se acerca a 1."""
    counts = np.array([1] * 100)
    assert simpson_index(counts) > 0.95


def test_simpson_rango_valido():
    """Simpson (1-D) siempre debe estar entre 0 y 1."""
    counts = np.array([7, 3, 15, 1, 0, 9])
    valor = simpson_index(counts)
    assert 0.0 <= valor <= 1.0


def test_calcular_diversidad_columnas_esperadas():
    """calcular_diversidad debe devolver Shannon, Simpson y Riqueza_observada."""
    asv_table = pd.DataFrame({
        "ASV_1": [10, 0, 5],
        "ASV_2": [10, 20, 0],
        "ASV_3": [0, 0, 5],
    }, index=["muestra_1", "muestra_2", "muestra_3"])

    resultado = calcular_diversidad(asv_table)

    assert list(resultado.columns) == ["Shannon", "Simpson", "Riqueza_observada"]
    assert resultado.loc["muestra_2", "Riqueza_observada"] == 1  # solo ASV_2 presente
    assert resultado.loc["muestra_2", "Shannon"] == pytest.approx(0.0)
