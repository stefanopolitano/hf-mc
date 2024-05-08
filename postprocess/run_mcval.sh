o2-analysis-timestamp -b --configuration json://config_mcval.json  |\
o2-analysis-event-selection -b --configuration json://config_mcval.json |\
o2-analysis-trackselection -b --configuration json://config_mcval.json  |\
o2-analysis-centrality-table -b --configuration json://config_mcval.json |\
o2-analysis-multiplicity-table -b --configuration json://config_mcval.json |\
#o2-analysis-bc-converter -b --configuration json://config_mcval.json |\
#o2-analysis-tracks-extra-converter -b --configuration json://config_mcval.json |\
o2-analysis-ft0-corrected-table -b --configuration json://config_mcval.json |\
o2-analysis-track-to-collision-associator -b --configuration json://config_mcval.json  |\
o2-analysis-hf-track-index-skim-creator -b --configuration json://config_mcval.json |\
o2-analysis-hf-candidate-creator-2prong -b --configuration json://config_mcval.json  |\
o2-analysis-hf-candidate-creator-3prong -b --configuration json://config_mcval.json |\
o2-analysis-track-propagation -b --configuration json://config_mcval.json --aod-file @input_data.txt
#o2-analysis-hf-task-mc-validation -b --configuration json://config_mcval.json --aod-file @input_data.txt