"""Pruebas unitarias de generación automática de paleta de colores (its_pipeline.plotting)."""

import re

from its_pipeline.plotting import generar_paleta

_HEX_VALIDO = re.compile(r"^#[0-9a-f]{6}$")


def test_genera_un_color_por_muestra():
    muestras = ["it-its_1", "it-its_2", "it-its_3"]
    paleta = generar_paleta(muestras)

    assert set(paleta.keys()) == set(muestras)
    assert len(paleta) == 3


def test_colores_son_hex_validos():
    paleta = generar_paleta(["a", "b", "c"])
    for color in paleta.values():
        assert _HEX_VALIDO.match(color), f"{color!r} no es un color hex válido"


def test_no_falla_con_lista_vacia():
    assert generar_paleta([]) == {}


def test_escala_a_muchas_muestras_reciclando_colores():
    """Con más muestras que colores del colormap, no debe fallar — recicla."""
    muestras = [f"muestra_{i}" for i in range(300)]
    paleta = generar_paleta(muestras)

    assert len(paleta) == 300
    assert all(_HEX_VALIDO.match(c) for c in paleta.values())
