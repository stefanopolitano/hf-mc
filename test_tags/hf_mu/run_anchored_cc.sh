# make sure O2DPG + O2 is loaded
[ ! "${O2DPG_ROOT}" ] && echo "Error: This needs O2DPG loaded" && exit 1
[ ! "${O2_ROOT}" ] && echo "Error: This needs O2 loaded" && exit 1

export ALIEN_JDL_LPMANCHORPASSNAME=apass7
export ALIEN_JDL_MCANCHOR=apass7
export ALIEN_JDL_CPULIMIT=60 
export ALIEN_JDL_LPMPASSNAME=apass7
export ALIEN_JDL_LPMRUNNUMBER=528531
export ALIEN_JDL_LPMPRODUCTIONTYPE=MC
export ALIEN_JDL_LPMINTERACTIONTYPE=pp
export ALIEN_JDL_LPMPRODUCTIONTAG=LHC22o_anc_ported
export ALIEN_JDL_LPMANCHORRUN=528531
export ALIEN_JDL_LPMANCHORPRODUCTION=LHC22o
export ALIEN_JDL_LPMANCHORYEAR=2022

export NTIMEFRAMES=2
export NSIGEVENTS=1

export SPLITID=100
export PRODSPLIT=153
export CYCLE=0
export DISABLE_QC=1
export ALIEN_PROC_ID=2963436952 #?

export ALIEN_JDL_ANCHOR_SIM_OPTIONS="-gen external -ini ${O2DPG_ROOT}/MC/config/PWGHF/ini/GeneratorHF_mu_ccbar_gap5_Mode2_accSmall.ini --mft-assessment-full --fwdmatching-assessment-full"

${O2DPG_ROOT}/MC/run/ANCHOR/anchorMC.sh
 

