#!/bin/bash

echo "Rendering ..."
quarto render index.qmd

# Define the output filename
OUTPUT_ZIP="output.zip"

# Clean up any old zip file so we start fresh
if [ -f "$OUTPUT_ZIP" ]; then
    rm "$OUTPUT_ZIP"
    echo "Removed old zip file."
fi

# Zip all required exports
echo "Packaging files into $OUTPUT_ZIP..."
zip -r "$OUTPUT_ZIP" index.html index_files/ assets/ style.css

echo "Done! You can now safely share $OUTPUT_ZIP."
