#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
    print("Usage: pathview-metacerberus.R <counts.tsv> <class.tsv>")
    quit()
}

# Load libraries
is_quiet <- TRUE

if (!require("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager", quiet = TRUE)
    library(BiocManager)
}

if (!require("pathview.2", quietly = TRUE)) {
    # pathview.2 dependencies
    if (!require("DESeq2", quietly = TRUE))
        BiocManager::install("DESeq2", quiet = is_quiet)

    if (!require("edgeR", quietly = TRUE))
        BiocManager::install("edgeR", quiet = is_quiet)

    if (!require("limma", quietly = TRUE))
        BiocManager::install("limma", quiet = is_quiet)

    if (!require("gage", quietly = TRUE))
        BiocManager::install("gage", quiet = is_quiet)

    if (!require("gageData", quietly=TRUE))
        BiocManager::install("gageData", quiet = is_quiet)

    if (!require("pathview", quietly = TRUE))
        BiocManager::install("pathview", quiet = is_quiet)

    #Install pathview from github
    if (!require("devtools", quietly = TRUE)) {
        install.packages("devtools", quiet = is_quiet)
        library(devtools)
    }
    devtools::install_github("Elizaddh/pathview", quiet = is_quiet)
}

library(stringr)
#library(gage)
#library(pathview.2)

# Load Data
options(stringsAsFactors = TRUE)
gene.data <- read.table(file = args[1], sep = "\t", header  = T, quote = "", row.names = 1)
colnames(gene.data) <- sapply(str_split(colnames(gene.data), "_", n = 2), "[[", 2)
rg <- args[2]
coldata <- read.table(rg, sep = "\t", header = T, row.names = 1)
levels(coldata[, 1])[1]
print(coldata)
reference_indx <- which(coldata[, 1] ==  levels(coldata[, 1])[1])
samp_indx <- which(coldata[, 1] ==  levels(coldata[, 1])[2])
print("the treatment and reference are ")
samp_indx
reference_indx
library(pathview.2)
kegg.ortho.path <-  kegg.gsets(species = "ko", id.type = "kegg", check.new = FALSE)
kegg.gs <- kegg.ortho.path$kg.sets[kegg.ortho.path$sigmet.idx]
gene.data <- as.matrix(na.omit(gene.data))

outname <-  paste0(dirname(args[1]), "/", "img", "/", str_split(basename(args[1]), pattern = "_")[[1]][1], "_")

#sanity check
all(rownames(coldata) %in% colnames(gene.data))
all(rownames(coldata) == colnames(gene.data))
gene.data <- gene.data[, rownames(coldata)]
all(rownames(coldata) == colnames(gene.data))

#running pathview
pathview.2(run = "complete",
    both.dirs = list(gene = T, cpd = T),
    diff.tool = "deseq2",
    gene.data = gene.data,
    ref = reference_indx,
    samp = samp_indx,
    pathway.id = NULL,
    gsets = kegg.gs,
    plot.gene.data = T,
    outname = outname,
    compare = "unpaired")

pathview.2(run = "complete",
    both.dirs = list(gene = T, cpd = T),
    diff.tool = "edgeR",
    gene.data= gene.data,
    ref = reference_indx,
    samp=samp_indx,
    pathway.id = NULL,
    gsets = kegg.gs,
    plot.gene.data = T,
    outname = outname,
    compare = "unpaired")
