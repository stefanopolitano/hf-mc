TAG="VO_ALICE@O2PDPSuite::async-async-v1-01-02a-slc9-alidist-async-v1-01-02-1 "
LABEL=22_apass7
${O2DPG_ROOT}/GRID/utils/grid_submit.sh --script run_anchor_22_apass7.sh --jobname test_anchor_$LABEL --outputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --erroroutputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --packagespec $TAG --wait --fetch-output
