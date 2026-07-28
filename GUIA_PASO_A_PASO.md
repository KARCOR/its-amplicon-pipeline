# Guía completa: Pipeline de Análisis ITS desde Cero
**Para repetir el proyecto o enseñárselo a alguien — incluye los errores reales que aparecieron y cómo se resolvieron.**

---

## Objetivo del proyecto

Analizar datos reales de secuenciación ITS (hongos/levaduras) siguiendo el flujo estándar de la industria: control de calidad → recorte de primers → inferencia de ASVs (DADA2) → análisis de diversidad. Se usa Python para la parte de manejo de datos/visualización y R para DADA2 (porque DADA2 solo existe en R).

---

## Requisitos previos

| Programa | Para qué |
|---|---|
| Jupyter Notebook (viene con Anaconda) | Descarga de datos, control de calidad, recorte de primers, análisis de diversidad |
| RStudio | Inferencia de ASVs con DADA2 |
| Conexión a internet | Para descargar datos públicos y paquetes |

No necesitas conda/Anaconda Navigator para instalar DADA2 — de hecho, en Windows **no funciona** así (ver Error #1 abajo). RStudio normal es suficiente.

---

## PARTE A — Preparar el entorno de Python (Jupyter)

### A1. Crear la carpeta del proyecto
Crea una carpeta en tu computadora, por ejemplo `Portafolio_2026`, y dentro de ella guarda:
- `ITS_pipeline_notebook.ipynb`
- `dada2_pipeline.R`
- `README.md`

### A2. Instalar las librerías de Python
Abre el notebook en Jupyter y, en la **primera celda**, corre:
```python
!pip install cutadapt biopython pandas matplotlib seaborn nbformat multiqc
```

> ⚠️ **Vas a ver texto largo y advertencias en amarillo (`WARNING`) — son normales, ignóralas.** Solo preocúpate si ves la palabra `ERROR` en rojo relacionada con `cutadapt`, `biopython`, `pandas`, `matplotlib` o `seaborn` específicamente (un error de un paquete no relacionado, como `botocore`/`aiobotocore`, no afecta este proyecto).

### A3. Correr el notebook completo
Menú **Kernel → Restart Kernel and Run All Cells** (o "Run → Run All Cells" según tu versión de Jupyter).

Esto hace, en orden:
1. Descarga 3 archivos FASTQ reales (datos de prueba oficiales de nf-core/ampliseq) desde GitHub
2. Cuenta lecturas y muestra estadísticas de longitud
3. Recorta los primers ITS con `cutadapt`
4. Genera una gráfica comparando longitudes antes/después

### Verificación: confirma que sí funcionó
En una celda nueva:
```python
import os
for f in os.listdir("results/trimmed"):
    print(f, os.path.getsize(f"results/trimmed/{f}"), "bytes")
```
Debes ver 3 archivos `.trimmed.fastq.gz`, cada uno con tamaño mayor a 0 bytes.

---

> ### 🛑 Error común #1 — `FileNotFoundError` al correr cutadapt
> **Síntoma:** la celda de cutadapt falla con `FileNotFoundError`, aunque ya instalaste el paquete.
> **Causa real:** `pip install` instaló cutadapt en una carpeta que no está en el PATH de Windows. Python no encuentra el programa por su nombre.
> **Solución:** en la celda de cutadapt, cambia:
> ```python
> import subprocess, os
> ```
> por:
> ```python
> import subprocess, os, sys
> ```
> y cambia:
> ```python
> cmd = ["cutadapt", ...]
> ```
> por:
> ```python
> cmd = [sys.executable, "-m", "cutadapt", ...]
> ```
> Esto le dice a Python que use directamente su propio intérprete para llamar a cutadapt como módulo, sin depender del PATH del sistema.

---

## PARTE B — Preparar el entorno de R (RStudio + DADA2)

### B1. Verificar si tienes RStudio
Si no lo tienes, descárgalo de https://posit.co/download/rstudio-desktop/ (es gratis). Si ya lo tienes instalado, ábrelo directamente — **no necesitas Anaconda para esto**.

> ### 🛑 Error común #2 — intentar instalar DADA2 con conda
> **Síntoma:** `conda create -n bioinfo -c bioconda bioconductor-dada2` da `PackagesNotFoundInChannelsError`.
> **Causa real:** el canal `bioconda` no compila paquetes para Windows, solo para Linux/macOS. No es un problema de configuración, simplemente no existe esa opción en Windows.
> **Solución:** olvida conda para esto. Instala DADA2 directo desde R con Bioconductor (sí tiene binarios para Windows) — ver paso B2.

### B2. Instalar BiocManager y DADA2
En la consola de RStudio (no en CMD):
```r
if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install("dada2")
```

> ### 🛑 Error común #3 — advertencia de Rtools
> **Síntoma:** aparece `WARNING: Rtools is required to build R packages but is not currently installed.`
> **¿Es un problema?** No, en este caso. Bioconductor distribuye DADA2 ya compilado (binario) para Windows, así que no necesita Rtools para instalarse. La advertencia es genérica y se puede ignorar mientras la instalación termine con `package 'dada2' successfully unpacked`.

> ### 🛑 Pregunta recurrente — `Update all/some/none? [a/s/n]:`
> Esto va a aparecer varias veces durante las instalaciones. Significa que R detectó paquetes antiguos y pregunta si quieres actualizarlos.
> - Si estás a mitad de instalar algo nuevo y solo quieres terminar rápido: responde **`n`**
> - Si vas a actualizar paquetes específicos a propósito (ver Error #5): responde **`a`**
> **Importante:** si escribes un comando nuevo mientras esta pregunta sigue esperando respuesta, R lo va a interpretar como tu respuesta a la pregunta, no como un comando — por eso parece que "no pasa nada". Siempre resuelve la pregunta primero (`a`, `s`, o `n` + Enter) antes de escribir cualquier otra cosa.

### B3. Verificar que dada2 quedó instalado
```r
library(dada2)
```
Si no da ningún `Error` (puede mostrar `Cargando paquete requerido: Rcpp`, eso es normal), quedó listo.

### B4. Ubicar y configurar tu carpeta de trabajo
```r
getwd()
```
Esto te muestra dónde está parado R. Cambia a tu carpeta del proyecto:
```r
setwd("RUTA/COMPLETA/A/TU/CARPETA/Portafolio_2026")
```

> 💡 **Tip:** si tu ruta tiene espacios o acentos (ej. carpetas de OneDrive con nombres como "Universidad Autónoma de Chiriquí"), escribe la ruta completa entre comillas tal cual aparece — R la maneja bien siempre que esté entre `" "`. Para encontrar la ruta exacta: en el Explorador de Windows, entra a la carpeta, clic derecho → "Copiar como ruta de acceso", pega aquí y cambia las `\` por `/`.

---

## PARTE C — Correr el pipeline DADA2 paso a paso

**Regla de oro: nunca corras todo el script de un solo golpe la primera vez.** Selecciona y corre por bloques pequeños — así, si algo falla, sabes exactamente dónde.

### C1. Definir las rutas a tus archivos recortados
```r
path <- "results/trimmed"
fnFs <- sort(list.files(path, pattern = ".trimmed.fastq.gz", full.names = TRUE))
sample.names <- sapply(strsplit(basename(fnFs), ".trimmed"), `[`, 1)
fnFs
```
**Verifica:** `fnFs` debe mostrarte 3 rutas de archivo, no `character(0)`.

> ### 🛑 Error común #4 — `fnFs` está vacío (`character(0)`)
> **Síntoma:** el siguiente paso (`filterAndTrim`) da un error críptico como `invalid subscript type 'list'`.
> **Causa real:** no es un error de R en sí — es que no hay archivos en `results/trimmed/` todavía. Esto pasa si el notebook de Python mostraba resultados guardados de una ejecución anterior (de otra persona o de otra sesión), pero tú nunca lo corriste de verdad en tu propia máquina.
> **Cómo confirmarlo:** corre `list.files("results/trimmed")` desde R. Si sale vacío, ese es el problema.
> **Solución:** regresa a la Parte A, asegúrate de correr **Kernel → Restart Kernel and Run All Cells** en el notebook de Python, y confirma con `os.listdir("results/trimmed")` en Python que los 3 archivos sí existen con tamaño mayor a 0 antes de volver a R.

### C2. Filtrado por calidad
```r
filtFs <- file.path(path, "filtered", basename(fnFs))
names(filtFs) <- sample.names

out <- filterAndTrim(fnFs, filtFs,
                      maxEE = 5,
                      truncQ = 2,
                      minLen = 50,
                      rm.phix = TRUE,
                      compress = TRUE,
                      multithread = FALSE)
print(out)
```
**Resultado esperado:** una tabla con columnas `reads.in` y `reads.out` para cada muestra.

> 💡 **Nota sobre `multithread`:** en este script siempre usamos `FALSE`, porque el procesamiento paralelo de DADA2 no es totalmente estable en Windows. Con pocas muestras no se pierde velocidad real.

> ### 🛑 Error común #5 — `Permission denied` al actualizar paquetes
> **Síntoma:** al correr `install.packages(c("rlang", "withr", "Rcpp"))`, aparece `problema al copiar ... rlang.dll: Permission denied`.
> **Causa real:** Windows no permite sobrescribir un archivo `.dll` que está siendo usado activamente — y como ya habías cargado `library(dada2)` (que depende de `rlang`), el archivo estaba "en uso".
> **Solución:** cierra RStudio **completamente** (no solo "Restart R"), ábrelo de nuevo, y corre la actualización de paquetes **antes** de cargar cualquier `library(...)`.

### C3. Modelo de errores
```r
errF <- learnErrors(filtFs, multithread = FALSE)
plotErrors(errF, nominalQ = TRUE)
```
Esto tarda uno o dos minutos. Puede aparecer un gráfico con advertencias como `log-10 transformation introduced infinite values` — **son normales con pocas muestras/lecturas, no indican un error real.**

### C4. Inferencia de ASVs
```r
dadaFs <- dada(filtFs, err = errF, multithread = FALSE,
                HOMOPOLYMER_GAP_PENALTY = -1, BAND_SIZE = 32)
```
(`HOMOPOLYMER_GAP_PENALTY` y `BAND_SIZE` son ajustes específicos para datos de IonTorrent, que es propenso a errores en homopolímeros — no son necesarios si tus datos son de Illumina.)

### C5. Tabla de ASVs y remoción de quimeras
```r
seqtab <- makeSequenceTable(dadaFs)
cat("Dimensiones tabla ASV:", dim(seqtab), "\n")

seqtab.nochim <- removeBimeraDenovo(seqtab, method = "consensus",
                                     multithread = FALSE, verbose = TRUE)
cat("Porcentaje retenido tras quimeras:", sum(seqtab.nochim) / sum(seqtab) * 100, "%\n")
```

### C6. Exportar para usar en Python
```r
write.csv(seqtab.nochim, "seqtab_nochim.csv")
```

---

## PARTE D — Análisis de diversidad en Python

Regresa al notebook de Jupyter, sección de diversidad:

```python
import pandas as pd
import numpy as np

def shannon_index(counts):
    counts = counts[counts > 0]
    p = counts / counts.sum()
    return -np.sum(p * np.log(p))

def simpson_index(counts):
    counts = counts[counts > 0]
    p = counts / counts.sum()
    return 1 - np.sum(p**2)

asv_table = pd.read_csv("seqtab_nochim.csv", index_col=0)

diversidad = pd.DataFrame({
    "Shannon": asv_table.apply(shannon_index, axis=1),
    "Simpson": asv_table.apply(simpson_index, axis=1)
})
diversidad
```

> ### 🛑 Error común #6 — `NameError: name 'shannon_index' is not defined`
> **Causa real:** en Python, una función debe estar **definida antes** de usarse. Si pegas el código con `diversidad = pd.DataFrame(...)` antes de los `def shannon_index(...)` / `def simpson_index(...)`, va a fallar.
> **Solución:** siempre define las funciones primero, y úsalas después — como en el bloque de arriba, ya en el orden correcto.

**Resultado esperado:** una tabla con un índice Shannon y Simpson por muestra.

---

## Resumen visual del flujo completo

```
[Jupyter/Python]                          [RStudio/R]
1. Descargar FASTQ reales (GitHub)
2. Control de calidad (conteo, longitud)
3. cutadapt → recorte de primers   ──────▶  4. filterAndTrim (filtro por calidad)
                                             5. learnErrors (modelo de errores)
                                             6. dada() (inferencia de ASVs)
                                             7. makeSequenceTable
                                             8. removeBimeraDenovo (quitar quimeras)
                                             9. write.csv("seqtab_nochim.csv")
10. pd.read_csv(...) ◀──────────────────────┘
11. Shannon / Simpson (diversidad)
```

---

## Tabla rápida de errores (referencia exprés)

| Error | Causa real | Solución en 1 línea |
|---|---|---|
| `Rscript no se reconoce` en CMD | R no está en el PATH de Windows | Usa RStudio en vez de CMD |
| `bioconda` no tiene `dada2` para Windows | bioconda no soporta Windows | Instala con `BiocManager::install()`, no con conda |
| `FileNotFoundError` con cutadapt | Instalado fuera del PATH | Usa `sys.executable, "-m", "cutadapt"` |
| `invalid subscript type 'list'` en `filterAndTrim` | `fnFs` vacío — cutadapt nunca corrió de verdad | Verifica `list.files("results/trimmed")`, vuelve a correr el notebook completo |
| `Permission denied` al actualizar paquetes de R | DLL en uso por una sesión de R ya abierta | Cierra RStudio completo, reabre, actualiza antes de cargar librerías |
| `NameError` en Python con `shannon_index` | Función usada antes de ser definida | Define funciones primero, úsalas después |

---

**Con esta guía, cualquier persona (incluida tú en el futuro) puede repetir el proyecto desde cero sabiendo qué esperar en cada paso, sin necesitar ayuda externa para los errores ya documentados aquí.**
