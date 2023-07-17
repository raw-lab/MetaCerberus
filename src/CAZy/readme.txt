# dbCAN HMMdb release 11.0
# 08/09/2022
# total 699 CAZyme HMMs (452 family HMMs + 3 cellulosome HMMs + 244 subfamily HMMs)
# data based on CAZyDB released on 08/07/2022
# New family models (total 7): CBM89, CBM90, CBM91, GH172, GH173, CE20, GT115 
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com


** if you want to run dbCAN CAZyme annotation on your local linux computer, do the following:
** 1. download dbCAN-fam-HMMs.txt, hmmscan-parser.sh 
** 2. download HMMER 3.0 package [hmmer.org] and install it properly
** 3. format HMM db: hmmpress dbCAN-fam-HMMs.txt
** 4. run: hmmscan --domtblout yourfile.out.dm dbCAN-fam-HMMs.txt yourfile > yourfile.out
** 5. run: sh hmmscan-parser.sh yourfile.out.dm > yourfile.out.dm.ps (if alignment > 80aa, use E-value < 1e-5, otherwise use E-value < 1e-3; covered fraction of HMM > 0.3)
** 6. run: cat yourfile.out.dm.ps | awk '$5<1e-15&&$10>0.35' > yourfile.out.dm.ps.stringent (this allows you to get the same result as what is produced in our dbCAN2 webpage)
Cols in yourfile.out.dm.ps:
1. Family HMM
2. HMM length
3. Query ID
4. Query length
5. E-value (how similar to the family HMM)
6. HMM start
7. HMM end
8. Query start
9. Query end
10. Coverage
** About what E-value and Coverage cutoff thresholds you should use (in order to further parse yourfile.out.dm.ps file), we have done some evaluation analyses using arabidopsis, rice, Aspergillus nidulans FGSC A4, Saccharomyces cerevisiae S288c and Escherichia coli K-12 MG1655, Clostridium thermocellum ATCC 27405 and Anaerocellum thermophilum DSM 6725. Our suggestion is that for plants, use E-value < 1e-23 and coverage > 0.2; for bacteria, use E-value < 1e-18 and coverage > 0.35; and for fungi, use E-value < 1e-17 and coverage > 0.45.
** We have also performed evaluation for the five CAZyme classes separately, which suggests that the best threshold varies for different CAZyme classes (please see http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4132414/ for details). Basically to annotate GH proteins, one should use a very relax coverage cutoff or the sensitivity will be low (Supplementary Tables S4 and S9); (ii) to annotate CE families a very stringent E-value cutoff and coverage cutoff should be used; otherwise the precision will be very low due to a very high false positive rate (Supplementary Tables S5 and S10)
** On our dbCAN2 website, we use E-value < 1e-15 and coverage > 0.35, which is more stringent than the default ones in hmmscan-parser.sh


# dbCAN HMMdb release 10.0
# 10/03/2021
# fixed the problem with the diamond db file (GT2 and a few other families were missing in the release on 07/26/2021).
# 08/17/2021
# total 692 CAZyme HMMs (445 family HMMs + 3 cellulosome HMMs + 244 subfamily HMMs)
# data based on CAZyDB released on 07/26/2021
# New family models (total 12): CBM88, GH169, GH170, GH171, GT112, GT113, GT114, PL41, PL42 (replace GH145), CE19, AA17, GT100
# Deleted: GH145
# Updated: AA1, AA8, CBM30, CBM44, CBM72, CBM82, CBM84, GH109, GH27, GH48, GT105, GT61
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 9.0
# 08/04/2020
# total 681 CAZyme HMMs (434 family HMMs + 3 cellulosome HMMs + 244 subfamily HMMs)
# data based on CAZyDB released on 07/30/2020
# New family models (total 15): CBM86, CBM87, GH166, GH167, GH168, GT108, GT109, GT110, GT111, PL38, PL39, PL40, CE17, CE18, CBM35inCE17 (CBM35 co-exist with CE17, classic CBM35 model can't find the CBM in CE17 proteins or find with very marginal e-value, may deserve a new CBM fam number) 
# New subfamily models (total 27): GH16_10, GH16_11, GH16_12, GH16_13, GH16_14, GH16_15, GH16_16, GH16_17, GH16_18, GH16_19, GH16_1, GH16_20, GH16_21, GH16_22, GH16_23, GH16_24, GH16_25, GH16_26, GH16_27, GH16_2, GH16_3, GH16_4, GH16_5, GH16_6, GH16_7, GH16_8, GH16_9
# Deleted: CE10, GT46
# Updated: CBM35
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 8.0
# 08/08/2019
# total 641 CAZyme HMMs (421 family HMMs + 3 cellulosome HMMs + 217 subfamily HMMs)
# data based on CAZyDB released on 07/26/2019
# New family models (total 24): AA16, CBM84, CBM85, GH154, GH156, GH157, GH158, GH159, GH160, GH161, GH162, GH163, GH164, GH165, GT107, PL29, PL30, PL31, PL32, PL33, PL34, PL35, PL36, PL37
# New subfamily models (total 10): GH30_9, GH5_54, GH5_55, GH5_56, PL1_13, PL33_1, PL33_2, PL36_1, PL36_2, PL8_4
# All the 217 subfamily HMMs were updated with most current CAZy data
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 7.0
# 08/25/2018
# total 607 CAZyme HMMs
# data based on CAZyDB released on 07/31/2018
# New family models (total 15): AA14, AA15, CBM82, CBM83, GH146, GH147, GH148, GH149, GH150, GH151, GH152, GH153, GT105, GT106, PL28
# GT2 family HMM now is replaced with 8 Pfam HMMs (in light of http://www.mdpi.com/2309-608X/4/1/6/htm)
# (GT2_Chitin_synth_1, GT2_Chitin_synth_2, GT2_Glycos_transf_2, GT2_Glyco_tranf_2_2, GT2_Glyco_tranf_2_3, GT2_Glyco_tranf_2_4, GT2_Glyco_tranf_2_5, GT2_Glyco_trans_2_3)
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 6.0
# 09/12/2017
# total 585 CAZyme HMMs
# data based on CAZyDB released on 07/20/2017
# New family models (total 18): CBM81, GH136, GH137, GH138, GH139, GH140, GH141, GH142, GH143, GH144, GH145, GT101, GT102, GT103, GT104, PL25, PL26, PL27
# Also newly created CAZyme subfamily models for all existing CAZy subfamilies (total 207): 
# AA1_1, AA1_2, AA1_3, AA3_1, AA3_2, AA3_3, AA3_4, AA5_1, AA5_2, GH13_10,
# GH13_11, GH13_12, GH13_13, GH13_14, GH13_15, GH13_16, GH13_17, GH13_18,
# GH13_19, GH13_1, GH13_20, GH13_21, GH13_22, GH13_23, GH13_24, GH13_25,
# GH13_26, GH13_27, GH13_28, GH13_29, GH13_2, GH13_30, GH13_31, GH13_32,
# GH13_33, GH13_34, GH13_35, GH13_36, GH13_37, GH13_38, GH13_39, GH13_3,
# GH13_40, GH13_41, GH13_42, GH13_4, GH13_5, GH13_6, GH13_7, GH13_8, GH13_9,
# GH30_1, GH30_2, GH30_3, GH30_4, GH30_5, GH30_6, GH30_7, GH30_8, GH43_10,
# GH43_11, GH43_12, GH43_13, GH43_14, GH43_15, GH43_16, GH43_17, GH43_18,
# GH43_19, GH43_1, GH43_20, GH43_21, GH43_22, GH43_23, GH43_24, GH43_25,
# GH43_26, GH43_27, GH43_28, GH43_29, GH43_2, GH43_30, GH43_31, GH43_32,
# GH43_33, GH43_34, GH43_35, GH43_36, GH43_37, GH43_3, GH43_4, GH43_5, GH43_6,
# GH43_7, GH43_8, GH43_9, GH5_10, GH5_11, GH5_12, GH5_13, GH5_14, GH5_15,
# GH5_16, GH5_17, GH5_18, GH5_19, GH5_1, GH5_20, GH5_21, GH5_22, GH5_23,
# GH5_24, GH5_25, GH5_26, GH5_27, GH5_28, GH5_29, GH5_2, GH5_30, GH5_31,
# GH5_32, GH5_33, GH5_34, GH5_35, GH5_36, GH5_37, GH5_38, GH5_39, GH5_40,
# GH5_41, GH5_42, GH5_43, GH5_44, GH5_45, GH5_46, GH5_47, GH5_48, GH5_49,
# GH5_4, GH5_50, GH5_51, GH5_52, GH5_53, GH5_5, GH5_7, GH5_8, GH5_9, PL10_1,
# PL10_2, PL10_3, PL1_10, PL1_11, PL11_1, PL1_12, PL11_2, PL1_1, PL12_1,
# PL12_2, PL12_3, PL1_2, PL1_3, PL14_1, PL14_2, PL14_3, PL14_4, PL14_5, PL1_4,
# PL15_1, PL15_2, PL1_5, PL1_6, PL17_1, PL17_2, PL1_7, PL1_8, PL1_9, PL21_1,
# PL2_1, PL22_1, PL22_2, PL2_2, PL3_1, PL3_2, PL3_3, PL3_4, PL3_5, PL4_1,
# PL4_2, PL4_3, PL4_4, PL4_5, PL5_1, PL6_1, PL6_2, PL6_3, PL7_1, PL7_2, PL7_3,
# PL7_4, PL7_5, PL8_1, PL8_2, PL8_3, PL9_1, PL9_2, PL9_3, PL9_4
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 5.0
# 07/24/2016
# total 360 CAZyme HMMs
# data based on CAZyDB released on 07/15/2016
# New family models: CBM72, CBM73, CBM74, CBM75, CBM76, CBM77, CBM78, CBM79,
# CBM80, GH134, GH135, GT98, GT99, PL24, GT2_Cellulose_synt
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 4.0
# 07/20/2015
# total 345 CAZyme HMMs
# data based on CAZyDB released on 03/17/2015
# New family models: CBM68, CBM69, CBM70, CBM71, GH133, GT95, GT96, GT97, PL23, AA11, AA12, AA13
# questions/comments to Yanbin Yin: yanbin.yin@gmail.com

# dbCAN HMMdb release 3.0
# 05/11/2013
# total 333 CAZyme HMMs
# data based on CAZyDB released on 03/22/2013
# New family models in v3 compared with v2: CBM65, CBM66, CBM67, GH131, GH132, AA1, AA2, AA3, AA4, AA5, AA6, AA7, AA8, AA9, AA10
# Removed family models in v3: GH61 (now become AA9), CBM33 (now become AA10)

# dbCAN HMMdb release 2.0
# 06/06/2012
# total 320 CAZyme HMMs
# data based on CAZyDB released on 01/09/2012
# New family models in v2 compared with v1: CBM63, CBM64, GT93, GT94, GH126, GH127, GH128, GH129, GH130
# Updated family model in v2: GH101

# dbCAN HMMdb release 1.0
# 08/23/2011
# data based on CAZyDB released on 03/22/2011





