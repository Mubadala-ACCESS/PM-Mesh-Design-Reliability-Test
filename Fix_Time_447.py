#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
import sys
import os


def generate_output_filename(input_file):
    base, ext = os.path.splitext(input_file)
    return f"{base}_updated{ext}"


def process_csv(input_file, hours=3, max_lines=447):
    output_file = generate_output_filename(input_file)

    with open(input_file, "r", newline="") as infile, \
         open(output_file, "w", newline="") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for i, row in enumerate(reader):
            # Header (keep as-is)
            if i == 0:
                writer.writerow(row)
                continue

            # Apply time shift only up to max_lines
            if i < max_lines:
                if row:
                    try:
                        timestamp = datetime.fromisoformat(row[0])
                        new_timestamp = timestamp + timedelta(hours=hours)
                        row[0] = new_timestamp.isoformat()
                    except Exception as e:
                        print(f"[WARNING] Row {i} skipped: {e}")

            # After line 447 → write unchanged
            writer.writerow(row)

    print(f"[DONE] Output saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py input.csv")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)

    process_csv(input_file)


if __name__ == "__main__":
    main()