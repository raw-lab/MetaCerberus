# TODO

## Jose

### text/paper related

- 1. Statistics and visualization
- 2. Add text for PCA and outputs
- 3. Figure for general output
- 4. **PATHVIEW**
- 5. Table for database size and download times
  - eggnog
  - microbeannotator
- 6. Statistics for resource and annotation experiments
- 7. Phage genomes from INPHARED?
- 8. Fix figure five
  - Fix <1e-15
- 9. Upload all genomes
- 10. accession list for all
- 11. upload genomes
- 12. Figure 2 stacked
- 13. All figures have A-Z labels

### code related

1. General rules are within the code
1 to 5 rules.
"1) if two HMM hits are non-overlapping from the same database both are counted as long as they are the within the default or user selected e-value/bitscores, 2) if two HMM hits are overlapping (>10 amino acids) from the same database the lowest resulting e-value and highest bitscore wins or the ‘top hit,’ or ‘winner take all,’ approach, 3) if both have the same equal value e-value and bitscore but are different accessions from the same database (e.g., KO1 and KO3) then both are reported, 4) no partial hits or fractions of hits are counted, and 5) if a hit is overlapping <10 amino acids both hits are counted due to the dual domain issue. "
2. Eggnog-mapper v2
- diamond
- hmmer
3. MicrobeAnnotator
- database issue
4. Add incremental PCA to MetaC
5. pVOG add look-up table
