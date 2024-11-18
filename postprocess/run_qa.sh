#!/bin/bash

# Bash script to run the Python script with specified arguments

# Define default parameters
TARGET_DIR="./inputs/"
OUTPUT_DIR="./outputs/"
INPUT_DIRS=("/alice/cern.ch/user/a/alihyperloop/outputs/0029/293900/49793")
SUFFIXES=("HF_LHC24h2_All_train293900")
FILES_TO_MERGE=("AnalysisResults")
CURRENT_DIR=$(pwd)
SYSTEM=pp
OLDER_MC="outputs/HF_LHC24h2_All_train293900/QA_output_HF_LHC24h2_All_train293900.root" # optional: one can provide a list of QA file to be compared
MC_LABLES="h2 h2" # optional: if OLDER_MC is provided, one has to provide a label for each MC and the first one must be the current one

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
    "$CURRENT_DIR/inputs/AnalysisResults_$SUFFIXES.root" $OUTPUT_DIR "_$SUFFIXES" "$SYSTEM"

# Clean pdf files older than 6 months
find "$OUTPUT_DIR" -name "*.pdf" -type f -mtime +180 -exec rm -f {} \;

# Clean root files older than 6 months
find "$TARGET_DIR" -name "*.root" -type f -mtime +180 -exec rm -f {} \;

# Merge all PDF files with "efficiency" in the filename into a single PDF
EFFICIENCY_PDFS=$(find "$OUTPUT_DIR" -name "*efficiency*.pdf" | sort)

if [ -n "$EFFICIENCY_PDFS" ]; then
    # Output merged PDF name
    MERGED_PDF="$OUTPUT_DIR/$SUFFIXES _efficiency.pdf"

    # Merge PDFs using pdfunite or gs
    pdfunite $EFFICIENCY_PDFS "$MERGED_PDF"

    echo "Merged efficiency PDFs into $MERGED_PDF"
else
    echo "No efficiency PDF files found to merge."
fi

# Merge all PDF files with "abundances" in the filename into a single PDF
ABUNDANCES_PDFS=$(find "$OUTPUT_DIR" -name "*abundances*.pdf" | sort)

if [ -n "$ABUNDANCES_PDFS" ]; then
    # Output merged PDF name
    MERGED_PDF="$OUTPUT_DIR/$SUFFIXES _abundances.pdf"

    # Merge PDFs using pdfunite or gs
    pdfunite $ABUNDANCES_PDFS "$MERGED_PDF"

    echo "Merged abundances PDFs into $MERGED_PDF"
else
    echo "No abundances PDF files found to merge."
fi

# Merge all PDF files with "collisions" in the filename into a single PDF
COLLISIONS_PDFS=$(find "$OUTPUT_DIR" -name "collision*.pdf" | sort)

if [ -n "$COLLISIONS_PDFS" ]; then
    # Output merged PDF name
    MERGED_PDF="$OUTPUT_DIR/$SUFFIXES _collision.pdf"

    # Merge PDFs using pdfunite or gs
    pdfunite $COLLISIONS_PDFS "$MERGED_PDF"

    echo "Merged collisions PDFs into $MERGED_PDF"
else
    echo "No collisions PDF files found to merge."
fi


if [ -n "$OLDER_MC" ]; then
    # Compare QA files
    echo "Compare QA files"
    python3 compare_qa_mc_val.py -i $OUTPUT_DIR/QA_output_$SUFFIXES.root $OLDER_MC -l $MC_LABLES -o $OUTPUT_DIR  
fi
