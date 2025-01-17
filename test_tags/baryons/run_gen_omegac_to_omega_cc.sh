#!/bin/bash

# Production of event pool bbar with OmegaC

${O2DPG_ROOT}/MC/bin/o2dpg_sim_workflow.py -j 8 -gen external -ini ${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_ccbar_Mode2_OmegaC_to_Omega.ini -tf 8 -ns 100 -eCM 13600 -interactionRate 500000 -seed 546 --make-evtpool -o evtpool --pregenCollContext
# Workflow runner
${O2DPG_ROOT}/MC/bin/o2dpg_workflow_runner.py -j 8 -f evtpool.json -tt pool