TAG="VO_ALICE@O2PDPSuite::async-async-v1-01-04-slc9-alidist-async-v1-01-01-1","VO_ALICE@jq::v1.6-alice1-3"
LABEL=anchor_24apass1_aj
SCRIPT=run_anchor_24aj.sh

${O2DPG_ROOT}/GRID/utils/grid_submit.sh --script $SCRIPT --jobname test_anchor_$LABEL --outputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --erroroutputspec '"*log*@disk=1","tf*/*log*@disk=1","AO2D.root@disk=2","tf*/AO2D.root@disk=2"' --packagespec $TAG --wait --fetch-output