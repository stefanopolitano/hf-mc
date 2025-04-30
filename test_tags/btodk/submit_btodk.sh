LABEL=apass1_btodk
SCRIPT=run_btodk.sh
PACKAGE=O2sim::v20250430-1
${O2DPG_ROOT}/GRID/utils/grid_submit.sh --script $SCRIPT --jobname test_anchor_$LABEL --packagespec $PACKAGE --outputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --erroroutputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --wait --fetch-output