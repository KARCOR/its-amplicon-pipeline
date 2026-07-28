"""Configuración centralizada del pipeline ITS.

Todos los parámetros que antes vivían sueltos en celdas del notebook están
aquí, en un solo lugar. Espejo legible en `config.yaml` para quien prefiera
no leer Python. Cambiar un primer o una muestra se hace en un solo sitio,
no buscando en 11 celdas.
"""

from pathlib import Path

# --- Rutas ---
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
TRIMMED_DIR = RESULTS_DIR / "trimmed"

# --- Muestras del dataset de DEMOSTRACIÓN (nf-core/test-datasets, branch ampliseq) ---
# Estas 3 muestras solo se usan para poblar data/ la primera vez que se corre
# el notebook, si data/ está vacío. El análisis real (QC, cutadapt,
# diversidad) usa `its_pipeline.discovery.descubrir_muestras()`, que detecta
# automáticamente lo que haya en data/ — 3 muestras o 300, sin editar código.
DEMO_SAMPLES = ["it-its_1", "it-its_2", "it-its_3"]
BASE_URL = "https://github.com/nf-core/test-datasets/raw/ampliseq/testdata/"

# --- Primers ITS (perfil oficial test_iontorrent de nf-core/ampliseq) ---
# Ajustar aquí si tus propios datos usan primers distintos.
FW_PRIMER = "GTGARTCATCGARTCTTTG"
# Reverse complement del primer reverse TCCTCSSCTTATTGATATGC
RV_PRIMER_RC = "GCATATCAATAAGSSGAGGA"

# --- Parámetros de cutadapt ---
CUTADAPT_MIN_LENGTH = 50

# --- Umbral de legibilidad visual ---
# Por encima de esta cantidad de muestras, los gráficos dejan de mostrar
# leyendas/etiquetas por muestra individual (se vuelven ilegibles) y en su
# lugar muestran solo un resumen agregado.
LIMITE_MUESTRAS_PARA_ETIQUETAS = 20
