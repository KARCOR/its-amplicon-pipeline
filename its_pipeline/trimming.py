"""Construcción y ejecución del comando cutadapt para recorte de primers ITS."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def comando_cutadapt(sample, in_file, out_file, fw_primer, rv_primer_rc, min_length=50):
    """Construye la lista de argumentos para invocar cutadapt como módulo de Python.

    Se usa `sys.executable -m cutadapt` en vez de invocar `cutadapt` directo
    porque en Windows pip puede instalar el ejecutable fuera del PATH
    (ver GUIA_PASO_A_PASO.md, Error común #1).
    """
    return [
        sys.executable, "-m", "cutadapt",
        "-g", fw_primer,
        "-a", rv_primer_rc,
        "--discard-untrimmed",
        "-m", str(min_length),
        "-o", str(out_file),
        str(in_file),
    ]


def ejecutar_cutadapt(sample, in_file, out_file, fw_primer, rv_primer_rc, min_length=50):
    """Corre cutadapt sobre una muestra y devuelve (sample, returncode, stdout)."""
    cmd = comando_cutadapt(sample, in_file, out_file, fw_primer, rv_primer_rc, min_length)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return sample, result.returncode, result.stdout


def ejecutar_cutadapt_paralelo(
    muestras, in_dir, out_dir, fw_primer, rv_primer_rc,
    min_length=50, max_workers=None, runner=None,
):
    """Corre cutadapt para varias muestras en paralelo (hilos).

    Cada muestra es un proceso `cutadapt` independiente — no hay ninguna
    razón para esperar a que termine una para empezar la siguiente. Con 3
    muestras esto no importa, pero con decenas o cientos (el caso real de
    NGS) correr todo en un solo hilo secuencial puede significar la
    diferencia entre minutos y horas.

    `subprocess.run` libera el GIL mientras espera al proceso externo, así
    que `ThreadPoolExecutor` (sin el overhead de `ProcessPoolExecutor`) es
    suficiente aquí: el paralelismo real ocurre a nivel de procesos del
    sistema operativo (los propios cutadapt), no de hilos de Python.

    Parameters
    ----------
    muestras : list[str]
        Nombres de muestra a procesar (típicamente de `discovery.descubrir_muestras`).
    in_dir, out_dir : str o Path
        Carpetas de entrada (FASTQ crudos) y salida (FASTQ recortados).
    max_workers : int, opcional
        Núm. de procesos cutadapt simultáneos. Por defecto, lo decide
        `ThreadPoolExecutor` (normalmente núm. de núcleos * 5); en la
        práctica conviene pasar `os.cpu_count()` explícitamente.
    runner : callable, opcional
        Función usada para procesar cada muestra individual, con la firma
        de `ejecutar_cutadapt`. Permite inyectar un doble de prueba en los
        tests sin invocar cutadapt de verdad (ver tests/test_trimming.py).

    Returns
    -------
    list[tuple]
        Una entrada (sample, returncode, stdout) por muestra, en el MISMO
        orden que `muestras` (no en orden de finalización).
    """
    runner = runner or ejecutar_cutadapt
    in_dir = Path(in_dir)
    out_dir = Path(out_dir)
    resultados = [None] * len(muestras)

    def _tarea(indice_muestra):
        indice, sample = indice_muestra
        in_file = in_dir / f"{sample}.fastq.gz"
        out_file = out_dir / f"{sample}.trimmed.fastq.gz"
        return indice, runner(sample, in_file, out_file, fw_primer, rv_primer_rc, min_length)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for indice, resultado in executor.map(_tarea, enumerate(muestras)):
            resultados[indice] = resultado

    return resultados
