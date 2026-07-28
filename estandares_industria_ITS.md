# Estándares de la industria para análisis de amplicón ITS (hongos/levaduras)
Referencia de trabajo — basada en nf-core/ampliseq v2.18.0 (2026), QIIME2 y DADA2. Verificada contra la documentación oficial vigente (ver Fuentes al final).

---

## El pipeline de referencia: nf-core/ampliseq

Es el estándar curado por la comunidad científica (citado en *Nature Biotechnology*, 2020), usado por institutos de investigación reales. Combina DADA2 + QIIME2 en un solo flujo reproducible.

- Repositorio: https://github.com/nf-core/ampliseq
- Documentación: https://nf-co.re/ampliseq
- Soporta ITS específicamente, con base de datos de referencia **UNITE** (la base estándar mundial para identificación taxonómica de hongos)

No necesitas correr Nextflow completo para practicar — pero sí debes **seguir su misma secuencia lógica de pasos** en tu notebook de Python, que es lo que importa para mostrar que conoces el estándar.

---

## Secuencia estándar de pasos (lo que hace cualquier pipeline serio)

### 1. Control de calidad inicial
- Herramienta estándar: **FastQC** (por muestra) + **MultiQC** (resumen agregado de todas las muestras)
- Qué revisar: calidad por posición (Phred score), contenido de adaptadores, duplicación de secuencias

### 2. Recorte de primers y adaptadores
- Herramienta estándar: **Cutadapt** (Martin, 2011)
- Para ITS específicamente: nf-core/ampliseq recomienda el parámetro **`--illumina_pe_its`** para datos Illumina paired-end, que desactiva el truncado a longitud fija — porque ITS tiene longitud muy variable (a diferencia de 16S, que es uniforme). También puede ser necesario subir `--truncq` (default 2) si DADA2 descarta una proporción alta de lecturas. Fuente: [docs/usage.md de nf-core/ampliseq](https://github.com/nf-core/ampliseq/blob/master/docs/usage.md#regions-of-variable-length-eg-its) — este es un detalle que demuestra que entiendes la diferencia entre marcadores

### 3. Inferencia de variantes de secuencia (denoising)
- Herramienta estándar: **DADA2** (no OTUs por clustering tradicional — ASVs es el estándar actual desde ~2016)
- Parámetros típicos a documentar y justificar en tu notebook:
  - `truncLen` (longitud de corte) — justifica según tus curvas de calidad, no copies un valor genérico
  - `maxEE` (errores esperados máximos)
  - Para ITS: dado que la longitud varía mucho, muchos pipelines omiten `truncLen` fijo y usan filtrado por calidad únicamente

### 4. Remoción de quimeras
- DADA2 lo hace internamente (`removeBimeraDenovo`) — siempre menciona este paso explícitamente, es common que se olvide en notebooks de práctica

### 5. Asignación taxonómica
- Base de datos estándar para ITS fúngico: **UNITE** (v10.0 vigente). No confundir con SILVA (16S rRNA de bacterias/arqueas) ni con PR2 (18S rRNA de eucariotas) — cada marcador genético tiene su propia base de referencia curada, usar la equivocada es un error común
- Método: clasificador Naive Bayes entrenado en QIIME2, o asignación directa vía DADA2 `assignTaxonomy()`

### 6. Análisis de diversidad
- **Alfa diversidad:** riqueza observada, Shannon, Simpson — siempre acompañados de curvas de rarefacción (demuestra que validaste profundidad de muestreo suficiente)
- **Cuidado con Chao1/ACE en datos de ASVs:** un artículo de 2024 en *The ISME Journal* (Deng, Umbach & Neufeld) advierte que estos estimadores **no deben calcularse sobre ASVs** cuando el pipeline elimina singletons por defecto (el caso de DADA2 en R y obligatorio en la versión de QIIME2) — el estimador depende matemáticamente de contar singletons/doubletons, y si se eliminan, el resultado no tiene sentido ecológico. Con ASVs, usar en su lugar riqueza observada, Shannon o Simpson. Chao1 sigue siendo válido sobre tablas de **OTUs** clásicas (97% de similitud) que conservan taxones raros.
- **Beta diversidad:** PCoA o NMDS sobre distancias Bray-Curtis o UniFrac
- Visualización estándar: barplots de composición taxonómica relativa por muestra/grupo

### 7. Reproducibilidad (esto es lo que distingue un análisis "amateur" de uno "profesional")
- Fija la semilla aleatoria (`set.seed()` / `np.random.seed()`)
- Documenta versión exacta de cada herramienta y base de datos usada
- Incluye un archivo de entorno (`requirements.txt` o `environment.yml`) para que cualquiera pueda reproducir tu análisis exactamente

---

## Cómo replicar el método exacto de un paper publicado

Cuando uses uno de los datasets públicos (ej. PRJNA616237), abre la sección **"Methods"** del paper original y anota:
- Qué primers usaron (ej. ITS1F/ITS2 vs ITS3/ITS4 — son regiones distintas)
- Qué parámetros de DADA2/QIIME2 reportaron
- Qué base de datos de referencia y qué versión usaron

Replicar exactamente esos parámetros y luego comparar tu resultado contra la Figura/Tabla publicada es la forma más rigurosa de validar que tu pipeline funciona correctamente — y es literalmente lo que hace un revisor de control de calidad en un laboratorio real.

---

## Diferencia clave que debes mencionar siempre: ASV vs OTU
Los referentes actuales (DADA2, QIIME2) ya no usan OTUs (agrupación por % de similitud, ej. 97%) — usan **ASVs (Amplicon Sequence Variants)**, que resuelven a nivel de variante exacta de secuencia. Si alguien te pregunta en una entrevista "¿por qué DADA2 y no OTUs?", esa es la respuesta esperada: mayor resolución, reproducibilidad entre estudios, y es el estándar desde ~2016.

---

## Fuentes consultadas (verificadas directamente, julio 2026)

- [nf-core/ampliseq — releases](https://github.com/nf-core/ampliseq/releases) (versión vigente: 2.18.0, 2026-06-17)
- [nf-core/ampliseq — docs/usage.md](https://github.com/nf-core/ampliseq/blob/master/docs/usage.md) (parámetros reales, incl. `--illumina_pe_its`, `--truncq`, tabla de bases de datos por marcador genético)
- [DADA2 ITS Pipeline Workflow](https://benjjneb.github.io/dada2/ITS_workflow.html) (Callahan, B., mantenedor oficial de DADA2)
- Callahan, B.J. et al. (2016). *DADA2: High-resolution sample inference from Illumina amplicon data.* Nat Methods 13, 581–583. [10.1038/nmeth.3869](https://doi.org/10.1038/nmeth.3869)
- Callahan, B.J., McMurdie, P.J. & Holmes, S.P. (2017). *Exact sequence variants should replace OTUs.* ISME J 11, 2639–2643. [10.1038/ismej.2017.119](https://doi.org/10.1038/ismej.2017.119)
- Martin, M. (2011). *Cutadapt removes adapter sequences...* EMBnet.journal 17(1), 10–12. [10.14806/ej.17.1.200](https://doi.org/10.14806/ej.17.1.200)
- Deng, Y., Umbach, A.K. & Neufeld, J.D. (2024). *Nonparametric richness estimators Chao1 and ACE must not be used with amplicon sequence variant data.* ISME J 18, wrae106. [10.1093/ismejo/wrae106](https://doi.org/10.1093/ismejo/wrae106)
- Ewels, P. et al. (2020). *The nf-core framework...* Nat Biotechnol 38, 276–278. [10.1038/s41587-020-0439-x](https://doi.org/10.1038/s41587-020-0439-x)
- [UNITE database](https://unite.ut.ee/) — versión vigente 10.0
