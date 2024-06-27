DESeq2 and Edge2 Type I errors
==================================

Both edgeR and DeSeq2 R have the highest sensitivity when compared to other algorithms that control type-I error when the FDR was at or below 0.1. EdgeR and DESeq2 all perform fairly well in simulation and via data splitting (so no parametric assumptions). Typical benchmarks will show limma having stronger FDR control across all types of datasets (it’s hard to beat the moderated t-test), and edgeR and DESeq2 having higher sensitivity for low counts (makes sense as limma has to filter these out / down-weight them to use the normal model on log counts). Further information about type I errors are present from Mike Love's vignette `here`_.

.. _here: https://bioconductor.org/packages/devel/bioc/vignettes/DESeq2/inst/doc/DESeq2.html#multi-factor-designs
