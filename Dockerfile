# Imagen reproducible del pipeline ITS.
#
# Objetivo: que cualquier persona (revisor de una revista, colega de industria)
# pueda ejecutar exactamente el mismo entorno sin depender de su instalación
# local de Python/R. Sigue la misma filosofía de contenedores que nf-core
# (cada módulo corre en Docker/Singularity para garantizar reproducibilidad).
#
# Construir:  docker build -t its-pipeline .
# Ejecutar:   docker run --rm -it -v "$(pwd)/results:/app/results" its-pipeline
# Pruebas:    docker run --rm its-pipeline pytest -q

FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema mínimas para compilar dependencias científicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir jupyter nbconvert nbclient

COPY its_pipeline/ its_pipeline/
COPY tests/ tests/
COPY seqtab_nochim.csv .
COPY ITS_pipeline_notebook.ipynb .
COPY config.yaml .

# Verificación de que el paquete y sus pruebas quedan sanos en la imagen
RUN pytest -q

CMD ["jupyter", "nbconvert", "--to", "notebook", "--execute", \
     "--ExecutePreprocessor.timeout=180", "ITS_pipeline_notebook.ipynb", \
     "--output", "ITS_pipeline_notebook.ejecutado.ipynb"]
