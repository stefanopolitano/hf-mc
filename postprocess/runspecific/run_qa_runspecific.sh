#!/bin/bash

# Bash script to download, process, and save all outputs in a single folder with a specific suffix in parallel

# Define default parameters
TARGET_DIR="./inputs/"
OUTPUT_BASE_DIR="./outputs"
INPUT_FILE="input_dirs.txt"  # Text file containing input directories (one per line)
OUTPUT_LIST_FILE="input_data.txt"  # File to store paths of AnalysisResults files
FILES_TO_MERGE=("AnalysisResults")
CURRENT_DIR=$(pwd)
SYSTEM="pp"
MAX_JOBS=4  # Limit the number of concurrent jobs

# Read INPUT_DIRS from the text file
if [[ -f "$INPUT_FILE" ]]; then
    mapfile -t INPUT_DIRS < "$INPUT_FILE"
else
    echo "Error: Input file $INPUT_FILE not found."
    exit 1
fi

# Create or clear the output list file
> "$OUTPUT_LIST_FILE"

# Create a single output directory with the specific suffix
mkdir -p "$OUTPUT_BASE_DIR"

# Function to process each input directory
process_input_dir() {
    input_dir=$1
    # Extract the last 6 characters for the suffix
    suffix="${input_dir: -6}"

    # Step 1: Download the file for the current input directory
    python3 download.py \
        --target_dir "$TARGET_DIR" \
        --input_dirs "$input_dir" \
        --suffix "$suffix" \
        --file_to_merge "${FILES_TO_MERGE[@]}"

    # Path to the downloaded AnalysisResults file
    analysis_results_path="$CURRENT_DIR/inputs/AnalysisResults_${suffix}.root"

    # Step 2: Run the QA validation script and store output in the single directory
    python3 store_hist.py \
        "$analysis_results_path"
    mv hGenEv.root "$CURRENT_DIR/outputs/hGenEv_${suffix}.root"

    # Step 3: Delete the original AnalysisResults file after use
    # rm "$analysis_results_path"
    echo "Processed and saved output for suffix $suffix."
}

# Loop through each entry in INPUT_DIRS and run each in background
for input_dir in "${INPUT_DIRS[@]}"; do
    process_input_dir "$input_dir" &  # Start the job in the background

    # Limit the number of concurrent jobs
    while (( $(jobs -r -p | wc -l) >= MAX_JOBS )); do
        sleep 1  # Wait for jobs to finish
    done
done

# Wait for all background jobs to finish
wait

echo "All outputs saved in $OUTPUT_BASE_DIR."
echo "Paths to AnalysisResults files saved in $OUTPUT_LIST_FILE."
