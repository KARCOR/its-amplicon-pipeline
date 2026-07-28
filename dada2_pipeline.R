# dada2_pipeline.R
# Pipeline DADA2 estándar (siguiendo nf-core/ampliseq) para inferencia de ASVs
# Ejecutar en tu máquina local con R + Bioconductor instalados

# --- 1. Instalación (correr una sola vez) ---
# if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager")
# BiocManager::install("dada2")

library(dada2)

# --- 2. Definir rutas ---
# Usa los archivos *.trimmed.fastq.gz generados en el notebook de Python (sección 2: cutadapt)
path <- "results/trimmed"
fnFs <- sort(list.files(path, pattern = ".trimmed.fastq.gz", full.names = TRUE))
sample.names <- sapply(strsplit(basename(fnFs), ".trimmed"), `[`, 1)

# --- 3. Filtrado y truncamiento ---
# IMPORTANTE: para ITS con IonTorrent (longitud muy variable) NO usamos truncLen fijo,
# solo filtramos por calidad y por máximo de errores esperados (maxEE),
# tal como especifica el perfil oficial test_iontorrent de nf-core/ampliseq (max_ee = 5)
filtFs <- file.path(path, "filtered", basename(fnFs))
names(filtFs) <- sample.names

out <- filterAndTrim(fnFs, filtFs,
                      maxEE = 5,        # valor oficial usado por nf-core/ampliseq para este dataset
                      truncQ = 2,
                      minLen = 50,
                      rm.phix = TRUE,
                      compress = TRUE,
                      multithread = FALSE)
print(out)

# --- 4. Modelo de errores (específico de IonTorrent) ---
errF <- learnErrors(filtFs, multithread = FALSE)
plotErrors(errF, nominalQ = TRUE)  # inspecciona visualmente antes de continuar

# --- 5. Inferencia de ASVs ---
# HOMOPOLYMER_GAP_PENALTY y BAND_SIZE son ajustes recomendados para IonTorrent
# (tecnología propensa a errores de homopolímeros, distinto de Illumina)
dadaFs <- dada(filtFs, err = errF, multithread = FALSE,
                HOMOPOLYMER_GAP_PENALTY = -1, BAND_SIZE = 32)

# --- 6. Tabla de secuencias (ASV table) ---
seqtab <- makeSequenceTable(dadaFs)
cat("Dimensiones tabla ASV:", dim(seqtab), "\n")

# --- 7. Remoción de quimeras (paso estándar, no opcional) ---
seqtab.nochim <- removeBimeraDenovo(seqtab, method = "consensus",
                                     multithread = FALSE, verbose = TRUE)
cat("Porcentaje de lecturas retenidas tras remover quimeras:",
    sum(seqtab.nochim) / sum(seqtab) * 100, "%\n")

# --- 8. Asignación taxonómica con UNITE (base estándar para hongos, NO usar SILVA) ---
# Descarga la base de datos UNITE más reciente desde: https://unite.ut.ee/repository.php
# taxa <- assignTaxonomy(seqtab.nochim, "sh_general_release_dynamic.fasta", multithread = FALSE)

# --- 9. Exportar para continuar el análisis de diversidad en Python ---
write.csv(seqtab.nochim, "seqtab_nochim.csv")
# write.csv(taxa, "taxonomia_unite.csv")

cat("\n¡Listo! Carga 'seqtab_nochim.csv' de vuelta en el notebook de Python, sección 4.\n")
