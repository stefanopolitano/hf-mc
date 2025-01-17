#!/bin/bash

# Production of event pool bbar with OmegaC with Sandro's update

# the ini file is the only thing that should be given
${O2DPG_ROOT}/MC/bin/o2_hybrid_gen.py --iniFile "${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_bbar_Mode2_OmegaC.ini" --clone 8 --mode parallel --output foo.json

# nothing needs to be changed here; it's some standard configs
${O2DPG_ROOT}/MC/bin/o2dpg_sim_workflow.py -gen hybrid -eCM 1.0 -tf 1 -ns 10 --make-evtpool -confKey "GeneratorHybrid.configFile=${PWD}/foo.json;GeneratorHybrid.num_workers=8" -interactionRate 1000000 -seed ${ALIEN_PROC_ID:-11} -run 300100

${O2DPG_ROOT}/MC/bin/o2dpg_workflow_runner.py -f workflow.json -tt pool
