#!/bin/bash

export ALIEN_JDL_CPULIMIT=8
export ALIEN_JDL_LPMANCHORPASSNAME="apass4"
export ALIEN_JDL_MCANCHOR="apass4"
export ALIEN_JDL_COLLISIONSYSTEM="pp"
export ALIEN_JDL_LPMPASSNAME="apass1"
export ALIEN_JDL_LPMRUNNUMBER="536340"
export ALIEN_JDL_LPMPRODUCTIONTYPE="MC"
export ALIEN_JDL_LPMINTERACTIONTYPE="pp"
export ALIEN_JDL_LPMPRODUCTIONTAG="2tags_corrbkg"
export ALIEN_JDL_LPMANCHORRUN="536340"
export ALIEN_JDL_LPMANCHORPRODUCTION="LHC23n"
export ALIEN_JDL_LPMANCHORYEAR="2022"

# added export
export NTIMEFRAMES=4
export NSIGEVENTS=200

export SPLITID=100
export PRODSPLIT=153
export CYCLE=5

# disable the QC
export DISABLE_QC=1

export ALIEN_JDL_O2DPG_ASYNC_RECO_TAG="O2PDPSuite::async-async-20240229.pp.2b-slc9-alidist-O2PDPSuite-daily-20231208-0100-async1-1" # async tag

INI_PATH=${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_ccbar_and_bbbar_gap5_Mode2_corrBkg.ini # .ini file path

export ALIEN_JDL_ANCHOR_SIM_OPTIONS="-gen external -ini $INI_PATH"

${O2DPG_ROOT}/MC/run/ANCHOR/anchorMC.sh