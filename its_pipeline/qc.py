"""Funciones de control de calidad: lectura y estadísticas de archivos FASTQ."""

import gzip


def leer_longitudes(fastq_path):
    """Devuelve la lista de longitudes de todas las lecturas de un FASTQ.gz.

    Lee línea por línea (streaming) en vez de `readlines()` completo: con
    3 muestras de 1,000 lecturas la diferencia es irrelevante, pero con
    datos NGS reales (millones de lecturas por muestra, cientos de
    muestras) cargar cada archivo entero en memoria antes de procesarlo deja
    de ser trivial. Este enfoque solo mantiene en memoria las longitudes
    (enteros), no las secuencias ni las calidades completas.

    Parameters
    ----------
    fastq_path : str o Path
        Ruta a un archivo FASTQ comprimido (.fastq.gz).

    Returns
    -------
    list[int]
        Longitud de cada lectura, en el orden en que aparecen en el archivo.
    """
    lengths = []
    with gzip.open(fastq_path, "rt") as f:
        for i, line in enumerate(f):
            if i % 4 == 1:  # línea 2 de cada registro FASTQ = secuencia
                lengths.append(len(line.strip()))
    return lengths


def resumen_lecturas(fastq_path):
    """Resume número de lecturas y estadísticas de longitud de un FASTQ.gz.

    Returns
    -------
    dict con claves: n_reads, longitud_min, longitud_max, longitud_promedio
    """
    lengths = leer_longitudes(fastq_path)
    if not lengths:
        return {"n_reads": 0, "longitud_min": 0, "longitud_max": 0, "longitud_promedio": 0.0}
    return {
        "n_reads": len(lengths),
        "longitud_min": min(lengths),
        "longitud_max": max(lengths),
        "longitud_promedio": sum(lengths) / len(lengths),
    }
