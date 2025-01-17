#!/bin/bash

#
# A example workflow MC->RECO->AOD for a simple pp min bias
# production, targetting test beam conditions.

# make sure O2DPG + O2 is loaded
[ ! "${O2DPG_ROOT}" ] && echo "Error: This needs O2DPG loaded" && exit 1
[ ! "${O2_ROOT}" ] && echo "Error: This needs O2 loaded" && exit 1

# ----------- LOAD UTILITY FUNCTIONS --------------------------
. ${O2_ROOT}/share/scripts/jobutils.sh

# ----------- START ACTUAL JOB  -----------------------------
NWORKERS=${NWORKERS:-8}
CPU_LIMIT=${CPU_LIMIT:-32}
MODULES="--skipModules ZDC"
SIMENGINE=${SIMENGINE:-TGeant4}
NSIGEVENTS=${NSIGEVENTS:-100}
NTIMEFRAMES=${NTIMEFRAMES:-1}
[[ ${SPLITID} != "" ]] && SEED="-seed ${SPLITID}" || SEED=""

# Production of event pool bbar with OmegaC

${O2DPG_ROOT}/MC/bin/o2dpg_sim_workflow.py -j 8 -gen external -ini ${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_bbbar_Mode2_OmegaC.ini -tf 2 -ns 5 -eCM 13600 -interactionRate 500000 -seed 546 --make-evtpool -o evtpool --pregenCollContext
# Workflow runner
${O2DPG_ROOT}/MC/bin/o2dpg_workflow_runner.py -j 8 -f evtpool.json -tt pool