"""Pruebas unitarias de control de calidad de FASTQ (its_pipeline.qc)."""

import gzip

import pytest

from its_pipeline.qc import leer_longitudes, resumen_lecturas


def _escribir_fastq(path, reads):
    """Escribe un FASTQ.gz mínimo válido a partir de una lista de secuencias."""
    with gzip.open(path, "wt") as f:
        for i, seq in enumerate(reads):
            f.write(f"@read{i}\n{seq}\n+\n{'I' * len(seq)}\n")


@pytest.fixture
def fastq_ejemplo(tmp_path):
    path = tmp_path / "ejemplo.fastq.gz"
    _escribir_fastq(path, ["ACGT", "ACGTACGT", "AC"])
    return path


def test_leer_longitudes(fastq_ejemplo):
    assert leer_longitudes(fastq_ejemplo) == [4, 8, 2]


def test_resumen_lecturas(fastq_ejemplo):
    resumen = resumen_lecturas(fastq_ejemplo)
    assert resumen["n_reads"] == 3
    assert resumen["longitud_min"] == 2
    assert resumen["longitud_max"] == 8
    assert resumen["longitud_promedio"] == pytest.approx((4 + 8 + 2) / 3)


def test_resumen_lecturas_archivo_vacio(tmp_path):
    path = tmp_path / "vacio.fastq.gz"
    _escribir_fastq(path, [])
    resumen = resumen_lecturas(path)
    assert resumen["n_reads"] == 0
