#!/bin/bash

export ALIEN_JDL_CPULIMIT=8
export ALIEN_JDL_LPMANCHORPASSNAME="apass1"
export ALIEN_JDL_MCANCHOR="apass1"
export ALIEN_JDL_COLLISIONSYSTEM="pp"
export ALIEN_JDL_LPMPASSNAME="apass1"
export ALIEN_JDL_LPMRUNNUMBER="550367"
export ALIEN_JDL_LPMPRODUCTIONTYPE="MC"
export ALIEN_JDL_LPMINTERACTIONTYPE="pp"
export ALIEN_JDL_LPMPRODUCTIONTAG="LHC24aj_apass1_MC_test"
export ALIEN_JDL_LPMANCHORRUN="550367"
export ALIEN_JDL_LPMANCHORPRODUCTION="LHC24aj"
export ALIEN_JDL_LPMANCHORYEAR="2024"

# added export
export NTIMEFRAMES=5
export NSIGEVENTS=100 #100
export SPLITID=100
export PRODSPLIT=153
export CYCLE=5
#export ALIEN_PROC_ID=2963436952

# disable the QC
export DISABLE_QC=1

# modify ini file, to have external generator and/or config from a specific tag different from the one used for anchoring
ORIGINALINI=${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_D2H_ccbar_and_bbbar_gap5_Mode2.ini # original .ini file to be modified
MODIFIEDINI=GeneratorHF_D2H_ccbar_and_bbbar_gap5_Mode2_fromCVMFS.ini # output name for the modified .ini file

CFGTOREPLACE="\${O2DPG_MC_CONFIG_ROOT}/MC/config/PWGHF/pythia8/generator/pythia8_charmhadronic_with_decays_Mode2.cfg" # original config file name to be modified
CFGFROMCVMFS="/cvmfs/alice.cern.ch/el9-x86_64/Packages/O2DPG/daily-20241112-0000-1/MC/config/PWGHF/pythia8/generator/pythia8_charmhadronic_with_decays_Mode2.cfg" # new config file name to use

GENTOREPLACE="\${O2DPG_ROOT}/MC/config/PWGHF/external/generator/generator_pythia8_gaptriggered_hf.C" # original external generator file name to be modified
GENFROMCVMFS="/cvmfs/alice.cern.ch/el9-x86_64/Packages/O2DPG/daily-20241112-0000-1/MC/config/PWGHF/external/generator/generator_pythia8_gaptriggered_hf.C" # new external generator file name to use

if [ ! -f $MODIFIEDINI ]; then
    sed -e "s|$CFGTOREPLACE|$CFGFROMCVMFS|g" -e "s|$GENTOREPLACE|$GENFROMCVMFS|g" $ORIGINALINI > $MODIFIEDINI
fi

cat $MODIFIEDINI

MODIFIEDINI_PATH=$(readlink -f $MODIFIEDINI)

echo "Absolute path for MODIFIEDINI: $MODIFIEDINI_PATH"

#echo "Checking permissions for MODIFIEDINI:"
#ls -l $MODIFIEDINI
#chmod a+r $MODIFIEDINI
#ls -l $MODIFIEDINI

export ALIEN_JDL_ANCHOR_SIM_OPTIONS="-gen external -ini $MODIFIEDINI_PATH"

${O2DPG_ROOT}/MC/run/ANCHOR/anchorMC.sh