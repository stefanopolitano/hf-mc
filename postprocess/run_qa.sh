#!/bin/bash

# Bash script to run the Python script with specified arguments

# Define default parameters
TARGET_DIR="./inputs/"
OUTPUT_DIR="./outputs/"
INPUT_DIRS=("/alice/cern.ch/user/a/alihyperloop/outputs/0026/262556/39741")
SUFFIXES=("HF_LHC24g2_Small_2P3PDstar_60100_train262556")
FILES_TO_MERGE=("AnalysisResults")
CURRENT_DIR=$(pwd)

# Submit the Python script with the provided arguments
python3 download.py \
    --target_dir "$TARGET_DIR" \
    --input_dirs "${INPUT_DIRS[@]}" \
    --suffix "${SUFFIXES[@]}" \
    --file_to_merge "${FILES_TO_MERGE[@]}"

mkdir $OUTPUT_DIR/$SUFFIXES
OUTPUT_DIR="$OUTPUT_DIR/$SUFFIXES"

cp run_qa.sh $OUTPUT_DIR

# Run QA
python3 perform_qa_mc_val.py \
    "$CURRENT_DIR/inputs/AnalysisResults_$SUFFIXES.root" $OUTPUT_DIR "_$SUFFIXES"

# Clean pdf files older than 6 months
find "$OUTPUT_DIR" -name "*.pdf" -type f -mtime +180 -exec rm -f {} \;

# Clean root files older than 6 months
find "$TARGET_DIR" -name "*.root" -type f -mtime +180 -exec rm -f {} \;