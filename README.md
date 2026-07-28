# Pipeline de Análisis de Amplicón ITS — Comunidades Fúngicas / Levaduras

**Pregunta:** ¿un pipeline de bioinformática puede recuperar correctamente variantes de secuencia (ASVs) fúngicas a partir de datos NGS reales, de principio a fin, sin intervención manual y sin QIIME2?

**Resultado en una frase:** 100% de las lecturas contienen el primer esperado en las 3 muestras, tabla de ASVs sin quimeras generada con DADA2, y diversidad alfa/beta calculada — plantilla lista para correr con datos NGS propios.

Pipeline reproducible de bioinformática para análisis de secuenciación de amplicón ITS (región fúngica), siguiendo los estándares actuales de la industria (**nf-core/ampliseq**, **DADA2**, **QIIME2**).

> Flujo de trabajo end-to-end: control de calidad → recorte de primers → inferencia de variantes de secuencia (ASVs) → remoción de quimeras → diversidad alfa y beta → composición, aplicado a datos reales de secuenciación.

**Por qué este proyecto:** aplica metodología directamente relacionada con análisis de comunidades fúngicas en procesos de fermentación (café, cacao) — el mismo tipo de datos que se generan en investigación de fermentación espontánea con levaduras, área en la que tengo experiencia previa como investigadora.

---

## Dataset

Datos reales de secuenciación IonTorrent single-end, región ITS fúngica, mantenidos oficialmente como dataset de prueba del pipeline `nf-core/ampliseq`.

| | |
|---|---|
| Fuente | [nf-core/test-datasets](https://github.com/nf-core/test-datasets/tree/ampliseq) (branch `ampliseq`) |
| Muestras | `it-its_1`, `it-its_2`, `it-its_3` |
| Reads por muestra | 1,000 |
| Tecnología | IonTorrent, single-end |
| Primer forward | `GTGARTCATCGARTCTTTG` |
| Primer reverse | `TCCTCSSCTTATTGATATGC` |

Primers extraídos directamente de la configuración oficial [`test_iontorrent.config`](https://github.com/nf-core/ampliseq) del pipeline — no son parámetros inventados ni genéricos.

---

## Estado del pipeline

| Paso | Herramienta | Estado |
|---|---|---|
| 1. Control de calidad | Python (conteo/longitud) | ✅ Completo — ver notebook |
| 2. Recorte de primers | cutadapt | ✅ Completo — ejecutado, log real en el notebook |
| 3. Inferencia de ASVs | DADA2 (R/Bioconductor) | ✅ Completo — corrido localmente, ver `dada2_pipeline.R` y `seqtab_nochim.csv` |
| 4. Remoción de quimeras | DADA2 (`removeBimeraDenovo`) | ✅ Completo |
| 5. Diversidad alfa (Shannon, Simpson, riqueza) | Python (pandas/numpy) | ✅ Completo — con datos reales |
| 6. Diversidad beta (Bray-Curtis + PCoA) | Python (`scikit-bio`) | ✅ Completo — sin necesitar QIIME2 |
| 7. Asignación taxonómica (UNITE) | DADA2 `assignTaxonomy()` | ⏳ Código listo, comentado en `dada2_pipeline.R` — pendiente de descargar la base UNITE localmente |

**Nota técnica clave:** se usan **ASVs** (Amplicon Sequence Variants vía DADA2), no OTUs por clustering — es el estándar desde 2016 por su mayor resolución y reproducibilidad entre estudios. La taxonomía se asigna contra la base **UNITE** (estándar para hongos), no SILVA (que es para 16S/18S bacteriano).

Dado que esta es tecnología IonTorrent (no Illumina), el filtrado usa `maxEE` (máximo de errores esperados = 5, valor oficial de nf-core/ampliseq) en lugar de un corte de longitud fijo (`truncLen`), porque la longitud de lectura es naturalmente muy variable en esta plataforma.

---

## Resultados

- 100% de las lecturas contenían el primer esperado en las 3 muestras (confirma que los primers usados son correctos para este dataset)
- ~97-98.5% de las lecturas pasaron el filtro de longitud mínima tras el recorte
- Tabla de ASVs generada y sin quimeras (`seqtab_nochim.csv`)
- Diversidad alfa (Shannon, Simpson, riqueza observada) calculada por muestra — `results/alpha_diversity.png`
- Diversidad beta (PCoA sobre Bray-Curtis) — `results/beta_diversity_pcoa.png`
- Composición de ASVs dominantes por muestra — `results/taxonomic_composition.png`

---

## Estructura del repositorio

```
01_Pipeline_ITS_Amplicon_Fungico/
├── README.md
├── requirements.txt                 # Dependencias Python (pip install -r requirements.txt)
├── config.yaml                      # Parámetros del pipeline en formato legible (espejo de its_pipeline/config.py)
├── Dockerfile                       # Entorno reproducible (build + pytest + ejecución del notebook)
├── ITS_pipeline_notebook.ipynb      # Notebook principal: orquesta QC, cutadapt, diversidad alfa/beta, composición
├── its_pipeline/                    # Paquete Python con la lógica extraída y testeada del notebook
│   ├── __init__.py
│   ├── config.py                    # Rutas, primers, parámetros de cutadapt, umbrales visuales
│   ├── discovery.py                 # Detección automática de muestras en data/ (no hardcodeadas)
│   ├── plotting.py                  # Paleta de colores automática para N muestras
│   ├── qc.py                        # Lectura de longitudes / resumen de FASTQ (streaming)
│   ├── trimming.py                  # Comando cutadapt + ejecución en paralelo entre muestras
│   └── diversity.py                 # Shannon, Simpson, riqueza observada
├── tests/                           # Pruebas unitarias (pytest) de its_pipeline/
│   ├── test_qc.py
│   ├── test_discovery.py
│   ├── test_plotting.py
│   ├── test_trimming.py
│   └── test_diversity.py
├── dada2_pipeline.R                 # Script de R — inferencia de ASVs (correr localmente)
├── GUIA_PASO_A_PASO.md              # Guía completa, incluye errores reales y cómo se resolvieron
├── estandares_industria_ITS.md      # Referencia de estándares de la industria (nf-core/ampliseq, DADA2, QIIME2)
├── data/                            # FASTQ crudos (descargados automáticamente por el notebook)
├── seqtab_nochim.csv                # Tabla de ASVs × muestras (salida real de DADA2)
└── results/
    ├── trimmed/                     # FASTQ con primers recortados (salida de cutadapt)
    ├── length_distribution.png
    ├── alpha_diversity.png
    ├── beta_diversity_pcoa.png
    └── taxonomic_composition.png
```

**Por qué `its_pipeline/` separado del notebook:** siguiendo el patrón `src/` de [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) y la separación código/orquestación de nf-core, las funciones que antes vivían como `def` dentro de celdas (QC, construcción del comando cutadapt, índices de diversidad) ahora son un paquete importable con pruebas automáticas. El notebook sigue siendo el punto de entrada narrativo — solo orquesta y visualiza — pero la lógica que puede romperse silenciosamente al editar ahora está cubierta por `pytest`.

```bash
cd 01_Pipeline_ITS_Amplicon_Fungico
pip install -r requirements.txt
pytest -q          # 28 pruebas — QC, descubrimiento de muestras, paleta, cutadapt (comando y paralelo), diversidad
```

---

## Escalabilidad: de 3 muestras a N muestras

El notebook **detecta automáticamente** las muestras presentes en `data/` — no depende de una lista de 3 nombres escrita a mano. Esto significa que reemplazar los 3 FASTQ de demostración por 300 FASTQ propios **no requiere editar ningún archivo de código**: basta con poner los archivos en `data/` y correr el notebook.

Qué cambia concretamente al escalar:

- **Detección de muestras** (`its_pipeline/discovery.py`): escanea `data/*.fastq.gz` y arma la lista de trabajo; si `data/` ya tiene archivos, el notebook no descarga el dataset de demostración (evita mezclar datos propios con los 3 de prueba).
- **Recorte de primers en paralelo** (`its_pipeline/trimming.ejecutar_cutadapt_paralelo`): cada muestra es un proceso `cutadapt` independiente, así que se procesan varias en simultáneo (hasta `os.cpu_count()` a la vez) en vez de una por una. Verificado con una prueba sintética de 24 muestras: paralelo ~2× más rápido que secuencial en una máquina de 2 núcleos — la ganancia crece con más núcleos disponibles.
- **Lectura de FASTQ en streaming** (`its_pipeline/qc.py`): en vez de cargar el archivo completo en memoria (`readlines()`), lee línea por línea — relevante cuando las lecturas son millones por muestra, no miles.
- **Gráficos que no se rompen con muchas muestras**: la paleta de colores se genera automáticamente para cualquier cantidad de muestras (antes era un diccionario fijo para exactamente 3, que fallaba con `KeyError` frente a un nombre distinto). Por encima de `its_pipeline.config.LIMITE_MUESTRAS_PARA_ETIQUETAS` (20 por defecto), las leyendas y anotaciones individuales por muestra se ocultan automáticamente — con 200 muestras, una leyenda de 200 entradas o 200 etiquetas anotadas sobre un scatter no aporta nada, solo satura el gráfico.

**Límite honesto de este enfoque:** esto hace que el notebook escale razonablemente a decenas o unos pocos cientos de muestras en una sola máquina. No reemplaza a un orquestador real como **Nextflow** (lo que usa `nf-core/ampliseq` internamente) para producción a gran escala: Nextflow reintenta automáticamente solo las tareas que fallan sin repetir las que ya terminaron, reparte el trabajo entre los núcleos de un clúster completo (no solo los de una máquina), y lleva un registro de qué pasos ya se ejecutaron. Un notebook con paralelismo a nivel de hilos es una mejora real y suficiente para un pipeline de portafolio o un laboratorio pequeño — no es lo mismo que un pipeline de producción de cientos de muestras corriendo en un clúster institucional.

---

## Cómo reproducir con tus propios datos (plantilla lista para usar)

**Parte Python (notebook):**
```bash
pip install -r requirements.txt
jupyter notebook ITS_pipeline_notebook.ipynb
```
Coloca tus FASTQ (cualquier cantidad) en `data/` — se detectan automáticamente, no hace falta editar código para los nombres de muestra. Ajusta los primers en `its_pipeline/config.py` (o su espejo legible `config.yaml`) si son distintos a los de este dataset.

**Con Docker (entorno reproducible, sin instalar nada localmente):**
```bash
docker build -t its-pipeline .
docker run --rm -it -v "$(pwd)/results:/app/results" its-pipeline
```
La imagen corre las 15 pruebas unitarias durante el build (falla si algo se rompió) y luego ejecuta el notebook completo con `nbconvert`.

**Parte R (DADA2 — requiere instalación local):**
```r
if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install("dada2")
```
Corre `dada2_pipeline.R` sobre los archivos generados en `results/trimmed/` por el notebook. Esto genera un nuevo `seqtab_nochim.csv`.

**Volver al notebook:** recarga `seqtab_nochim.csv` en la Sección 4 y corre el resto — diversidad alfa, beta y composición se recalculan automáticamente con tus datos.

Base de datos de referencia UNITE (taxonomía fúngica): https://unite.ut.ee/repository.php — necesaria solo para el paso 7 (asignación taxonómica). Versión vigente: **UNITE v10.0** (lanzada en 2025, actualizada periódicamente ~4 veces/año).

---

## Referencias y estándares seguidos

Cada decisión de diseño del pipeline sigue un estándar publicado, no una elección arbitraria:

- **Por qué cutadapt + maxEE en vez de truncLen** (y no solo la config de nf-core): es la recomendación oficial del propio equipo de DADA2 para ITS, no solo de nf-core — ver el [DADA2 ITS Pipeline Workflow](https://benjjneb.github.io/dada2/ITS_workflow.html) (Callahan, B., mantenido por el autor de DADA2). La región ITS varía naturalmente en longitud (200–600 pb), por lo que truncar a una longitud fija elimina variantes reales; `maxEE` filtra por errores esperados, no por longitud.
- Callahan, B.J. et al. (2016). *DADA2: High-resolution sample inference from Illumina amplicon data.* Nature Methods, 13, 581–583. [10.1038/nmeth.3869](https://doi.org/10.1038/nmeth.3869)
- Callahan, B.J., McMurdie, P.J. & Holmes, S.P. (2017). *Exact sequence variants should replace operational taxonomic units in marker-gene data analysis.* ISME Journal, 11, 2639–2643. [10.1038/ismej.2017.119](https://doi.org/10.1038/ismej.2017.119) — fundamento de por qué se usan ASVs (DADA2) y no OTUs por clustering.
- Martin, M. (2011). *Cutadapt removes adapter sequences from high-throughput sequencing reads.* EMBnet.journal, 17(1), 10–12. [10.14806/ej.17.1.200](https://doi.org/10.14806/ej.17.1.200)
- Ewels, P. et al. (2020). *The nf-core framework for community-curated bioinformatics pipelines.* Nature Biotechnology, 38, 276–278. [10.1038/s41587-020-0439-x](https://doi.org/10.1038/s41587-020-0439-x)
- Base de datos taxonómica UNITE — versión actual y documentación: [unite.ut.ee](https://unite.ut.ee/)
- Pipeline de referencia: [nf-core/ampliseq](https://github.com/nf-core/ampliseq) (v2.18.0, 2026)

---

## Próximos pasos

- [ ] Descargar la base UNITE y correr `assignTaxonomy()` (código ya listo en `dada2_pipeline.R`)
- [ ] Aplicar el mismo pipeline a datos públicos de fermentación de café (ej. BioProject PRJNA616237) para conectar directamente con mi experiencia en fermentación con levaduras
- [ ] (Roadmap) Migrar a QIIME2 completo para visualizaciones interactivas — ver `_trabajo_futuro/QIIME2_roadmap/`

---

## Autora

**Karina Correa** — Bióloga en transición a Análisis de Datos
David, Chiriquí, Panamá · [LinkedIn](https://linkedin.com/in/karina-correa-aparicio) · [GitHub](https://github.com/KARCOR)
