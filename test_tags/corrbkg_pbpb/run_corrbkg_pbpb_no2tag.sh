#!/bin/bash

export ALIEN_JDL_CPULIMIT=8
export ALIEN_JDL_LPMANCHORPASSNAME="apass4"
export ALIEN_JDL_MCANCHOR="apass4"
export ALIEN_JDL_COLLISIONSYSTEM="PbPb"
export ALIEN_JDL_LPMPASSNAME="apass4"
export ALIEN_JDL_LPMRUNNUMBER="544013"
export ALIEN_JDL_LPMPRODUCTIONTYPE="MC"
export ALIEN_JDL_LPMINTERACTIONTYPE="PbPb"
export ALIEN_JDL_LPMPRODUCTIONTAG="LHC23zzh_apass4_pbpb_MC_test"
export ALIEN_JDL_LPMANCHORRUN="544013"
export ALIEN_JDL_LPMANCHORPRODUCTION="LHC23zzh"
export ALIEN_JDL_LPMANCHORYEAR="2023"

# added export
export NTIMEFRAMES=4
export NSIGEVENTS=25 #100
export SPLITID=100
export PRODSPLIT=153
export CYCLE=0
#export ALIEN_PROC_ID=2963436952

# disable the QC
export DISABLE_QC=1

#export ALIEN_JDL_O2DPG_ASYNC_RECO_TAG="O2PDPSuite::async-async-v1-01-27-slc8-alidist-async-v1-01-05-1" # async tag

export O2DPG_MC_CONFIG_ROOT="/cvmfs/alice.cern.ch/el9-x86_64/Packages/O2DPG/daily-20250507-0000-1"
INI_PATH=${O2DPG_MC_CONFIG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_ccbar_and_bbbar_PbPb_corrBkg.ini # .ini file path

export ALIEN_JDL_ANCHOR_SIM_OPTIONS="-gen external -ini $INI_PATH -genBkg pythia8 -procBkg heavy_ion --embedding --embeddPattern @0:e2"

${O2DPG_ROOT}/MC/run/ANCHOR/anchorMC.sh