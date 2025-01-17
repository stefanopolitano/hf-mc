#!/bin/bash

# Production of event pool bbbar with XiC

${O2DPG_ROOT}/MC/bin/o2dpg_sim_workflow.py -j 8 -gen external -ini ${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_bbbar_Mode2_XiC0_XiCplus.ini -tf 8 -ns 100 -eCM 13600 -interactionRate 500000 -seed 546 -productionTag "CaroTest_evtpool_bbbar_XiC" --make-evtpool -o evtpool --pregenCollContext
# Workflow runner
${O2DPG_ROOT}/MC/bin/o2dpg_workflow_runner.py -j 8 -f evtpool.json -tt pool