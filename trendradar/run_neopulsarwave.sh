#!/bin/bash

# Navigate to the script directory if not already there
cd "$(dirname "$0")"

# Define the current date in yymmdd format for the backup filename
current_date=$(date +%y%m%d)

echo "Starting Neopulsarwave processes..."

# Execute Python scripts in the required order
echo "Running Stage 1: Read Tweets"
python neopulsarwave_stage1.py

echo "Running Stage 2: Scoring Tweets"
python neopulsarwave_stage2.py

echo "Running Stage 3: Preparing Trend Radar Entry"
python neopulsarwave_stage3.py

echo "Running Stage 4: Weekly Analytics"
python neopulsarwave_stage4.py

echo "Running Stage 5: Gemini Ground using Google Search"
python neopulsarwave_stage5.py

echo "Running Stage 6: Web Scraping for Related Tweet URLs"
python neopulsarwave_stage6.py

# Backup the database
echo "Backing up the database..."
cp ../database/tweets.db "../database/tweets.db.$current_date"

# Copy the updated database to the main database directory
echo "Copying the updated database..."
cp tweets.db ../database/

echo "Neopulsarwave processes completed successfully."

