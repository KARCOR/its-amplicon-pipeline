"""Pruebas unitarias de construcción del comando cutadapt (its_pipeline.trimming).

No ejecuta cutadapt de verdad (eso lo cubre la ejecución end-to-end del
notebook) — solo verifica que el comando se arma con los argumentos
correctos, que es lo que realmente puede romperse silenciosamente al
editar el código.
"""

import sys
import time

from its_pipeline.trimming import comando_cutadapt, ejecutar_cutadapt_paralelo


def test_comando_incluye_python_actual():
    cmd = comando_cutadapt("s1", "in.fastq.gz", "out.fastq.gz", "GTGA", "GCAT")
    assert cmd[0] == sys.executable
    assert cmd[1:3] == ["-m", "cutadapt"]


def test_comando_incluye_primers_correctos():
    cmd = comando_cutadapt("s1", "in.fastq.gz", "out.fastq.gz", "GTGA", "GCAT")
    assert "-g" in cmd and cmd[cmd.index("-g") + 1] == "GTGA"
    assert "-a" in cmd and cmd[cmd.index("-a") + 1] == "GCAT"


def test_comando_incluye_min_length_por_defecto():
    # Ojo: cmd.index("-m") encontraría el "-m" de `python -m cutadapt`, no el
    # de longitud mínima de cutadapt — se usa rindex (última ocurrencia).
    cmd = comando_cutadapt("s1", "in.fastq.gz", "out.fastq.gz", "GTGA", "GCAT")
    assert cmd[len(cmd) - 1 - cmd[::-1].index("-m") + 1] == "50"


def test_comando_respeta_min_length_custom():
    cmd = comando_cutadapt("s1", "in.fastq.gz", "out.fastq.gz", "GTGA", "GCAT", min_length=75)
    assert cmd[len(cmd) - 1 - cmd[::-1].index("-m") + 1] == "75"


def test_comando_incluye_discard_untrimmed():
    cmd = comando_cutadapt("s1", "in.fastq.gz", "out.fastq.gz", "GTGA", "GCAT")
    assert "--discard-untrimmed" in cmd


def _runner_falso(sample, in_file, out_file, fw_primer, rv_primer_rc, min_length=50):
    """Doble de prueba: no invoca cutadapt de verdad, solo simula el resultado.

    Duerme un poco para que una ejecución realmente secuencial sea medible
    frente a una paralela (ver test_ejecutar_cutadapt_paralelo_es_mas_rapido_que_secuencial).
    """
    time.sleep(0.05)
    return sample, 0, f"log falso de {sample}"


def test_ejecutar_cutadapt_paralelo_devuelve_un_resultado_por_muestra(tmp_path):
    muestras = ["s1", "s2", "s3", "s4"]
    resultados = ejecutar_cutadapt_paralelo(
        muestras, tmp_path, tmp_path, "GTGA", "GCAT",
        max_workers=4, runner=_runner_falso,
    )

    assert len(resultados) == 4
    assert [r[0] for r in resultados] == muestras  # mismo orden que la entrada
    assert all(r[1] == 0 for r in resultados)


def test_ejecutar_cutadapt_paralelo_preserva_orden_aunque_terminen_desordenadas(tmp_path):
    """Aunque las tareas terminen en distinto orden, el resultado debe
    devolverse en el orden de `muestras`, no en orden de finalización."""
    def runner_con_velocidad_variable(sample, in_file, out_file, fw, rv, min_length=50):
        # La primera muestra tarda más — si el código no preservara el
        # orden por índice, terminaría última en la lista de resultados.
        time.sleep(0.1 if sample == "lenta" else 0.01)
        return sample, 0, ""

    muestras = ["lenta", "rapida_1", "rapida_2"]
    resultados = ejecutar_cutadapt_paralelo(
        muestras, tmp_path, tmp_path, "GTGA", "GCAT",
        max_workers=3, runner=runner_con_velocidad_variable,
    )

    assert [r[0] for r in resultados] == muestras


def test_ejecutar_cutadapt_paralelo_es_mas_rapido_que_secuencial(tmp_path):
    """Con 8 muestras de 0.05s cada una: en paralelo debe tardar bastante
    menos que 8 * 0.05s = 0.4s (lo que tardaría en secuencial)."""
    muestras = [f"s{i}" for i in range(8)]

    inicio = time.perf_counter()
    ejecutar_cutadapt_paralelo(
        muestras, tmp_path, tmp_path, "GTGA", "GCAT",
        max_workers=8, runner=_runner_falso,
    )
    duracion = time.perf_counter() - inicio

    assert duracion < 0.3  # con paralelismo real, debería tardar ~0.05-0.1s
