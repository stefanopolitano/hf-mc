TAG="O2PDPSuite::async-async-v1-01-27-slc8-alidist-async-v1-01-05-1"
LABEL=test_anchor_anchor_pbpb_apass4
SCRIPT=run_pbpb_apass4.sh

${O2DPG_ROOT}/GRID/utils/grid_submit.sh --script $SCRIPT --jobname test_anchor_$LABEL --outputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --erroroutputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --packagespec $TAG --wait --fetch-output