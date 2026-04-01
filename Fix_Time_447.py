#!/usr/bin/env python3
#Fix Timing until 447
import csv
from datetime import datetime, timedelta
import sys
import os

def add_hours_to_csv(input_file, output_file, hours=3, max_lines=447):
    """
    Adds specified hours to the timestamp in the first column of a CSV file.
    
    - Skips the first line (header)
    - Processes up to max_lines
    - Writes updated data to output_file
    """

    with open(input_file, "r", newline="") as infile, \
         open(output_file, "w", newline="") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for i, row in enumerate(reader):
            # Write header as-is
            if i == 0:
                writer.writerow(row)
                continue

            # Stop after max_lines (line count includes header)
            if i >= max_lines:
                break

            if not row:
                writer.writerow(row)
                continue

            try:
                # Parse ISO timestamp from first column
                timestamp = datetime.fromisoformat(row[0])

                # Add hours
                new_timestamp = timestamp + timedelta(hours=hours)

                # Replace timestamp
                row[0] = new_timestamp.isoformat()

            except Exception as e:
                print(f"[WARNING] Skipping row {i} due to error: {e}")

            writer.writerow(row)

    print(f"[DONE] Output saved to: {output_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python add_3_hours.py input.csv output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        sys.exit(1)

    add_hours_to_csv(input_file, output_file, hours=3, max_lines=447)


if __name__ == "__main__":
    main()