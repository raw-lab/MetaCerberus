#!/usr/bin/env Rscript

# Load libraries
is_quiet <- TRUE

if (!require("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager", quiet = TRUE)
  library(BiocManager)
}

if (!require("DESeq2", quietly = TRUE))
  BiocManager::install("DESeq2", quiet = is_quiet)

if (!require("edgeR", quietly = TRUE))
  BiocManager::install("edgeR", quiet = is_quiet)

if (!require("limma", quietly = TRUE))
  BiocManager::install("limma", quiet = is_quiet)

if (!require("EnhancedVolcano", quietly = TRUE))
  BiocManager::install("EnhancedVolcano", quiet = is_quiet)

if (!require("gage", quietly = TRUE))
  BiocManager::install("gage", quiet = is_quiet)

if (!require("gageData", quietly=TRUE))
  BiocManager::install("gageData", quiet = is_quiet)

if (!require("pathview", quietly = TRUE))
  BiocManager::install("pathview", quiet = is_quiet)



args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  print("Usage: pathview-metacerberus.R <counts.tsv> <class.tsv>")
  quit()
}

#' This is the function to run pathway analysis
#'
run_path_analysis <- function(lf.c, gsets, ref = ref, samp = samp, compare) {
  suppressMessages(library(gage, quietly = TRUE))
  fc.kegg.p <- gage::gage(exprs = lf.c, gsets = gsets, ref = NULL, samp = NULL, compare = compare)
  return(fc.kegg.p)
}


#' this is a function to run different diff expression analysis tools
#'
rundifftool <- function(diff.tool, gene.data, ref, samp, outname) {
  grp.idx <- NULL
  grp.idx[ref] <- "reference"
  grp.idx[samp] <- "sample"
  
  suppressMessages(library(EnhancedVolcano, quietly = TRUE))
  
  if (diff.tool == "deseq2") {
    suppressMessages(library(DESeq2, quietly = TRUE))
    coldat <- DataFrame(grp = factor(grp.idx))
    
    print("Deseq2 is running")
    dds <- DESeq2::DESeqDataSetFromMatrix(gene.data, colData = coldat, design = ~grp)
    dds <- estimateSizeFactors(dds)
    # dds <- estimateDispersions(dds)
    
    dds <- estimateDispersionsGeneEst(dds)
    dispersions(dds) <- mcols(dds)$dispGeneEst
    dds <-  nbinomWaldTest(dds)
    #dds <- DESeq2::DESeq(dds)
    deseq2.res <- results(dds)
    # direction of fc, depends on levels(coldat$grp), the first level
    # taken as reference (or control) and the second one as experiment.
    deseq2.fc <- deseq2.res$log2FoldChange
    names(deseq2.fc) <- rownames(deseq2.res)
    exp.fc <- deseq2.fc
    #pdf("Volcano_deseq2.pdf", width = 14,height= 14)
    jpeg("Volcano_deseq2.jpg", units = "in", width = 15, height = 15, res = 300)
    plot(EnhancedVolcano::EnhancedVolcano(deseq2.res, x = "log2FoldChange", y = "pvalue",
                                          lab = rownames(deseq2.res)))
    #plot(x = 1:10, y = 1:10)
    dev.off()
  }
  else if (diff.tool == "edgeR") {
    suppressMessages(library(edgeR, quietly = TRUE))
    dgel <- edgeR::DGEList(counts = gene.data, group = factor(grp.idx))
    dgel <- edgeR::calcNormFactors(dgel)
    dgel <- edgeR::estimateCommonDisp(dgel)
    dgel <- edgeR::estimateTagwiseDisp(dgel)
    et <- edgeR::exactTest(dgel)
    edger.fc <- et$table$logFC
    names(edger.fc) <- rownames(et$table)
    exp.fc <- edger.fc
    jpeg("Volcano_edgeR.jpg", units = "in", width = 15, height = 15, res = 300)
    plot(EnhancedVolcano::EnhancedVolcano(et$table, x = "logFC", y = "PValue", lab = rownames(et$table)))
    dev.off()
  }
  else if (diff.tool == "limma") {
    suppressMessages(library(limma, quietly = TRUE))
    dgel2 <- edgeR::DGEList(counts = gene.data, group = factor(grp.idx))
    dgel2 <- edgeR::calcNormFactors(dgel2)
    design <- limma::model.matrix(~grp.idx)
    log2.cpm <- limma::voom(dgel2, design)
    fit <- limma::lmFit(log2.cpm, design)
    fit <- limma::eBayes(fit)
    limma.res <- limma::topTable(fit, coef = 2, n = Inf, sort = "p")
    limma.fc <- limma.res$logFC
    
    names(limma.fc) <- limma.res$ID
    exp.fc <- limma.fc
  }
  else {
    print("The diff tool is not avaliable")
  }
  return(exp.fc)
}


#' this is a function to run pathview.2 function
#'
pathview.2 <- function(run, diff.tool, gene.data, ref, samp, outname, gsets, compare,
                       both.dirs = list(gene = T, cpd = T), pathway.id = NULL, species, plot.gene.data = T) {
  
  if (is.null(pathway.id) == FALSE) {
    pathview::pathview(gene.data = gene.data, pathway.id = pathway.id, out.suffix = outname, plot.gene.data)
  }
  else {
    if (run == "complete") {
      logfoldchange <- rundifftool(diff.tool, gene.data, ref, samp, outname)
      print("diff tool run successful")
      fc.kegg.p <- run_path_analysis(logfoldchange, gsets, ref = NULL, samp = NULL, compare = compare)
      #, gene.data = gene.data, ref, samp, plot.gene.data = T )
      print("gage run successful")
      
      print("now pathview")
      path.ids.2 <- rownames(fc.kegg.p$greater)[fc.kegg.p$greater[, "q.val"] < 0.1 &
                                                  + !is.na(fc.kegg.p$greater[, "q.val"])]
      
      if (length(fc.kegg.p) > 2) {
        print(length(fc.kegg.p))
        path.ids.l <- rownames(fc.kegg.p$less)[
          fc.kegg.p$less[, "q.val"] < 0.1 & + !is.na(fc.kegg.p$less[, "q.val"])]
        path.ids.2 <- c(path.ids.2[1:3], path.ids.l[1:3])
        path.ids.2 <- gsub("[^0-9.-]", "", sapply(stringr::str_split(path.ids.2, " ", 2), "[[", 1))
      }
      print(c("Visualize Pathway", na.omit(path.ids.2[1:6])))
      for (pid in na.omit(path.ids.2[1:6])) {
        print(c("Processing", paste0('k', pid)))
        tryCatch(
          expr = {
            pathview::pathview(
              gene.data = logfoldchange,
              pathway.id = pid,
              species = species,
              out.suffix = diff.tool,
              plot.gene.data = T
              #kegg.native = T,
            )
          },
          error = function(e) {
            print(c("ERROR: Pathview failed on", pid))
          }
        )
      }
      print("Finished Pathview")
    }
    else {
      fc.kegg.p <- run_path_analysis(gene.data, gsets, ref = ref, samp = samp, compare = compare)
      #, gene.data = gene.data, ref, samp, plot.gene.data = T  )
      print("now pathview")
      path.ids.2 <- rownames(fc.kegg.p$greater)[fc.kegg.p$greater[, "q.val"] < 0.1 &
                                                  + !is.na(fc.kegg.p$greater[, "q.val"])]
      
      if (length(fc.kegg.p) > 2) {
        path.ids.l <- rownames(fc.kegg.p$less)[fc.kegg.p$less[, "q.val"] < 0.1 &
                                                 + !is.na(fc.kegg.p$less[, "q.val"])]
        path.ids.2 <- c(path.ids.2[1:3], path.ids.l[1:3])
        path.ids.2 <- gsub("[^0-9.-]", "", sapply(stringr::str_split(path.ids.2, " ", 2), "[[", 1))
        
        #visualize pathway
        pv.out.list <- sapply(na.omit(path.ids.2[1:6]), function(pid) pathview::pathview(gene.data =  gene.data,
                                                                                         pathway.id = pid, out.suffix = diff.tool, species, plot.gene.data = T))
      }
    }
  }
  
  suppressMessages(library(plotly, quietly = TRUE))
  
  print("Plotting Pathview Data")
  if (plot.gene.data == T) { #& is.null(pathway.id))  ) {
    gs <- unique(unlist(gsets[rownames(fc.kegg.p$greater)[1:3]]))
    essData <- gage::essGene(gs, gene.data, ref = ref, samp = samp, compare = compare)
    for (gs in rownames(fc.kegg.p$greater)[1:3]) {
      outname <- paste(gsub(" |:|/", "_", substr(gs, 9, 100)), "greater", sep="_")
      gage::geneData(genes = gsets[[gs]], exprs = essData, ref = ref,
                     samp = samp, outname = outname, txt = T, heatmap = T,
                     Colv = F, Rowv = F, dendrogram = "none", limit = 3, scatterplot = T, pdf.size = c(7, 7))
    }
    #print("PLOTTING HEATMAPS PLOTLY")
    #print(getwd())
    #for (file_tsv in list.files(pattern = "\\.txt$", ignore.case = TRUE)) {
    #    file_name = basename(file_tsv)
    #    file_tsv <- read.csv(file_tsv, sep = '\t', stringsAsFactors = TRUE)
    #    p <- ggplot(file_tsv,
    #                x = "Samples",
    #                y = "KO IDs",
    #                fill = "KO Pathway\nRegulation")
    #    pltHeatmap <- plotly::ggplotly(p)
    #    print(paste0("SAVING: ", file_name, ".html"))
    #    htmlwidgets::saveWidget(pltHeatmap, paste0(file_name, ".html"))
    #}
    
    if (length(fc.kegg.p) > 2) {
      gs <- unique(unlist(gsets[rownames(fc.kegg.p$lesser)[1:3]]))
      essData <- gage::essGene(gs, gene.data, ref = ref, samp = samp, compare = compare)
      for (gs in rownames(fc.kegg.p$lesser)[1:3]) {
        outname <- paste(gsub(" |:|/", "_", substr(gs, 10, 100)), "lesser", sep="_")
        gage::geneData(genes = gsets[[gs]], exprs = essData, ref = ref,
                       samp = samp, outname = outname, txt = T, heatmap = T,
                       Colv = F, Rowv = F, dendrogram = "none", limit = 3, scatterplot = T, pdf.size = c(7, 7))
      }
    }
  }
}


library(stringr, quietly = TRUE)
library(gage, quietly = TRUE)
library(pathview, quietly = TRUE)
#source("pathview.2.R")

print("Loading Data")
#options(stringsAsFactors = TRUE) #TODO: DEPRECATED

gene_data <- read.table(file =args[1], sep = "\t", header  = T, quote = "", row.names = 1, stringsAsFactors = TRUE)
coldata <- read.table(args[2], sep = "\t", header = T, row.names = 1, stringsAsFactors = TRUE)

print("Levels")
levels(coldata[, 1])[1]
print("Coldata")
print(head(coldata))
reference_indx <- which(coldata[, 1] ==  levels(coldata[, 1])[1])
samp_indx <- which(coldata[, 1] ==  levels(coldata[, 1])[2])
print("the treatment and reference are ")
print("Sample Index")
samp_indx
print("Reference Index")
reference_indx

kegg.ortho.path <-  kegg.gsets(species = "ko", id.type = "kegg", check.new = FALSE)
kegg.gs <- kegg.ortho.path$kg.sets[kegg.ortho.path$sigmet.idx]
gene.data <- as.matrix(na.omit(gene_data))

outname <-  paste0(dirname(args[1]), "/", "img", "/", str_split(basename(args[1]), pattern = "_")[[1]][1], "_")

#sanity check
print("Sanity Check")
all(rownames(coldata) %in% colnames(gene.data))
all(colnames(gene.data) %in% rownames(coldata))
all(rownames(coldata) == colnames(gene.data))
gene.data <- gene.data[, rownames(coldata)]
all(rownames(coldata) == colnames(gene.data))

print("Running pathview")

dir.create("deseq2", showWarnings = FALSE)
setwd("deseq2")
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
           compare = "unpaired",
           species = "ko")
setwd("..")

dir.create("edgeR", showWarnings = FALSE)
setwd("edgeR")
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
           compare = "unpaired",
           species = "ko")
setwd("..")
