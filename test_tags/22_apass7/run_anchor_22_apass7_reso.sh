#!/bin/bash

#
# An example steering script for anchored MC simulations, pp
#

# example anchoring
# taken from https://its.cern.ch/jira/browse/O2-4586

export ALIEN_JDL_CPULIMIT=8
export ALIEN_JDL_LPMPRODUCTIONTYPE=MC
export ALIEN_JDL_LPMINTERACTIONTYPE=pp
export ALIEN_JDL_LPMPRODUCTIONTAG=LHC24f

# 2022 apass7
export ALIEN_JDL_LPMANCHORPASSNAME=apass7
export ALIEN_JDL_MCANCHOR=apass7
export ALIEN_JDL_LPMRUNNUMBER=523779
export ALIEN_JDL_LPMANCHORRUN=523779
export ALIEN_JDL_LPMANCHORPRODUCTION=LHC22m
export ALIEN_JDL_LPMANCHORYEAR=2022

# 2023 apass4
# export ALIEN_JDL_LPMANCHORPASSNAME=apass4
# export ALIEN_JDL_MCANCHOR=apass4
# export ALIEN_JDL_LPMRUNNUMBER=539908
# export ALIEN_JDL_LPMANCHORRUN=539908
# export ALIEN_JDL_LPMANCHORPRODUCTION=LHC23zt
# export ALIEN_JDL_LPMANCHORYEAR=2023

# export ALIEN_JDL_SIM_OPTIONS="-gen external -ini ${O2DPG_ROOT}/MC/
# config/PWGHF/ini/GeneratorHF_D2H_ccbar_and_bbbar_gap5_DReso.ini"
export ALIEN_JDL_SIM_OPTIONS="-gen external -ini ${O2DPG_ROOT}/MC/
config/PWGHF/ini/GeneratorHF_D2H_ccbar_and_bbbar_gap5_DReso.ini"

export NTIMEFRAMES=4
export NSIGEVENTS=500
export SPLITID=100
export PRODSPLIT=153
export CYCLE=0
# export ALIEN_PROC_ID=2963436952

${O2DPG_ROOT}/MC/run/ANCHOR/anchorMC.sh


