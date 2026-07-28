"""Pruebas unitarias de detección automática de muestras (its_pipeline.discovery)."""

from its_pipeline.discovery import descubrir_muestras


def _crear_fastq_vacio(path):
    path.write_bytes(b"")


def test_descubre_las_muestras_presentes(tmp_path):
    _crear_fastq_vacio(tmp_path / "muestra_b.fastq.gz")
    _crear_fastq_vacio(tmp_path / "muestra_a.fastq.gz")
    _crear_fastq_vacio(tmp_path / "muestra_c.fastq.gz")

    assert descubrir_muestras(tmp_path) == ["muestra_a", "muestra_b", "muestra_c"]


def test_escala_a_muchas_muestras():
    """El mismo mecanismo debe funcionar igual con 3 o con 300 muestras."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        data_dir = Path(d)
        for i in range(300):
            (data_dir / f"muestra_{i:03d}.fastq.gz").write_bytes(b"")

        muestras = descubrir_muestras(data_dir)

        assert len(muestras) == 300
        assert muestras[0] == "muestra_000"
        assert muestras[-1] == "muestra_299"


def test_ignora_archivos_con_otro_sufijo(tmp_path):
    _crear_fastq_vacio(tmp_path / "muestra_1.fastq.gz")
    (tmp_path / "notas.txt").write_text("no es un fastq")
    (tmp_path / "muestra_1.fastq.gz.md5").write_text("checksum")

    assert descubrir_muestras(tmp_path) == ["muestra_1"]


def test_ignora_subcarpetas(tmp_path):
    _crear_fastq_vacio(tmp_path / "muestra_1.fastq.gz")
    subcarpeta = tmp_path / "trimmed"
    subcarpeta.mkdir()
    _crear_fastq_vacio(subcarpeta / "muestra_1.trimmed.fastq.gz")

    assert descubrir_muestras(tmp_path) == ["muestra_1"]


def test_directorio_inexistente_devuelve_lista_vacia(tmp_path):
    assert descubrir_muestras(tmp_path / "no_existe") == []


def test_directorio_vacio_devuelve_lista_vacia(tmp_path):
    assert descubrir_muestras(tmp_path) == []
