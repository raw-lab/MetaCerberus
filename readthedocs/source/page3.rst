Annotation
===========

.. image:: https://raw.githubusercontent.com/raw-lab/metacerberus/main/img/Rules.jpg
   :width: 600 

- **Rule 1** is for finding high quality matches across databases. It is a score pre-filtering module for pORFs thresholds: which states that each pORF match to an HMM is recorded by default or a user-selected cut-off (i.e.,  e-value/bit scores) per database independently, or across all default databases (e.g, finding best hit), or per user specification of the selected database.
- **Rule 2** is to avoid missing genes encoding proteins with dual domains that are not overlapping. It is imputed for non-overlapping dual domain module pORF threshold: if two HMM hits are non-overlapping from the same database, both are counted as long as they are within the default or user selected score (i.e., e-value/bit scores).
- **Rule 3** is to ensure overlapping dual domains are not missed. This is the dual independent overlapping domain module for convergent binary domain pORFs. If two domains within a pORF are overlapping <10 amino acids (e.g, COG1 and COG4) then both domains are counted and reported due to the dual domain issue within a single pORF. If a function hits multiple pathways within an accession, both are counted, in pathway roll-up, as many proteins function in multiple pathways.
- **Rule 4** is the equal match counter to avoid missing high quality matches within the same protein. This is an independent accession module for a single pORF: if both hits within the same database have equal values for both e-value and bit score but are different accessions from the same database (e.g., KO1 and KO3) then both are reported.
- **Rule 5** is the ‘winner take all’ match rule for providing the best match. It is computed as the winner takes all module for overlapping pORFs: if two HMM hits are overlapping (>10 amino acids) from the same database the lowest resulting e-value and highest bit score wins.
- **Rule 6** is to avoid partial or fractional hits being counted. This ensures that only whole discrete integer counting (e.g., 0, 1, 2 to n) are computed and that partial or fractional counting is excluded. 
