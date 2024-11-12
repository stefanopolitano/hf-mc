TAG="O2PDPSuite::async-async-v1-01-02d-slc9-alidist-async-v1-01-02-1" # same tag of 24af
LABEL=anchor_24apass1_ag
SCRIPT=run_anchor_24ag.sh

${O2DPG_ROOT}/GRID/utils/grid_submit.sh --script $SCRIPT --jobname test_anchor_$LABEL --outputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --erroroutputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --packagespec $TAG --wait --fetch-output