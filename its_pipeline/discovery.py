"""Detección automática de muestras a partir de los archivos presentes en data/.

Existe para que el pipeline no dependa de una lista de nombres escrita a mano
(`config.DEMO_SAMPLES` solo se usa para el dataset de demostración). Con
esto, reemplazar los 3 FASTQ de prueba por 300 FASTQ propios no requiere
tocar ningún archivo de código — el notebook detecta lo que haya.
"""

from pathlib import Path


def descubrir_muestras(data_dir, sufijo=".fastq.gz"):
    """Detecta las muestras presentes en un directorio a partir de sus archivos FASTQ.

    Parameters
    ----------
    data_dir : str o Path
        Carpeta donde están los FASTQ crudos (no busca en subcarpetas, para
        no confundir `data/trimmed/` u otras salidas con datos de entrada).
    sufijo : str
        Extensión/sufijo del archivo a considerar (por defecto ".fastq.gz").

    Returns
    -------
    list[str]
        Nombres de muestra (nombre de archivo sin el sufijo), ordenados
        alfabéticamente para que el orden sea reproducible entre corridas.
    """
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []
    archivos = sorted(
        p for p in data_dir.iterdir()
        if p.is_file() and p.name.endswith(sufijo)
    )
    return [p.name[: -len(sufijo)] for p in archivos]
