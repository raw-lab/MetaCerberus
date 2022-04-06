#!/apps/pkg/R/4.0.3/bin/Rscript

args = commandArgs(trailingOnly=TRUE)

# Load libraries
library(stringr)
library(gage)
library(pathview.2)

# Load Data
options(stringsAsFactors=TRUE)
gene.data = read.table(file = args[1], sep = "\t", header  = T, quote = "", row.names = 1)
colnames(gene.data)<- sapply(str_split(colnames(gene.data), "_", n = 2), "[[", 2) 
rg = args[2]
coldata <- read.table(rg, sep = "\t", header = T, row.names = 1)
levels(coldata[,1])[1]
print(coldata)
reference_indx<- which( coldata[,1] ==  levels(coldata[,1])[1] )
samp_indx<- which( coldata[,1] ==  levels(coldata[,1])[2] )
print("the treatment and reference are ")
samp_indx
reference_indx
library(pathview.2)
kegg.ortho.path <-  kegg.gsets(species = "ko", id.type = "kegg", check.new = FALSE)
kegg.gs <- kegg.ortho.path$kg.sets[kegg.ortho.path$sigmet.idx]
gene.data <- as.matrix(na.omit(gene.data))

outname <-  paste0( dirname(args[1]),"/","img", "/", str_split(basename(args[1]), pattern = "_")[[1]][1] , "_" )

#sanity check
all(rownames(coldata) %in% colnames(gene.data))
all(rownames(coldata) == colnames(gene.data))
gene.data <- gene.data[, rownames(coldata)]
all(rownames(coldata) == colnames(gene.data))

#running pathview
pathview.2(run = "complete"  , both.dirs = list(gene = T, cpd = T), diff.tool = "deseq2", gene.data= gene.data, ref = reference_indx, samp=samp_indx, pathway.id = NULL, gsets = kegg.gs, plot.gene.data = T, outname = outname, compare = "unpaired" )
pathview.2(run = "complete"  , both.dirs = list(gene = T, cpd = T), diff.tool = "edgeR", gene.data= gene.data, ref = reference_indx, samp=samp_indx, pathway.id = NULL, gsets = kegg.gs, plot.gene.data = T, outname = outname, compare = "unpaired" )
