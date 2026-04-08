import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# File paths
# =========================================================
fidas_file = r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\Fidas_Closed_03_April_2026.txt"
nextpm_file = r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\Closed_03_April_2026.csv"

output_dir = Path(r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\plots")
output_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# Load Next PM CSV
# =========================================================
nextpm_df = pd.read_csv(nextpm_file, dtype=str)
nextpm_df.columns = nextpm_df.columns.str.strip()

# Clean timestamp
nextpm_df["timestamp"] = nextpm_df["timestamp"].astype(str).str.strip()

# Fix malformed year if needed
nextpm_df["timestamp"] = nextpm_df["timestamp"].str.replace(r"^026-", "2026-", regex=True)

print("Raw Next PM timestamps:")
print(nextpm_df["timestamp"].head())

# Parse timestamp
nextpm_df["timestamp"] = pd.to_datetime(
    nextpm_df["timestamp"],
    format="%Y-%m-%dT%H:%M:%S.%f",
    errors="coerce"
)

# Drop invalid rows
nextpm_df = nextpm_df.dropna(subset=["timestamp"])

# Remove seconds by flooring to minute
nextpm_df["timestamp"] = nextpm_df["timestamp"].dt.floor("min")

# Required Next PM columns
nextpm_cols = [
    "sensor1_PM1mass",
    "sensor1_PM2_5mass",
    "sensor1_PM10mass",
    "sensor2_PM1mass",
    "sensor2_PM2_5mass",
    "sensor2_PM10mass",
]

# Convert to numeric
for col in nextpm_cols:
    nextpm_df[col] = pd.to_numeric(nextpm_df[col], errors="coerce")

# Keep only needed columns
nextpm_df = nextpm_df[["timestamp"] + nextpm_cols]

# Average by minute
nextpm_df = nextpm_df.groupby("timestamp", as_index=False).mean()

# =========================================================
# Load Fidas TXT
# =========================================================
fidas_df = pd.read_csv(fidas_file, sep="\t", dtype=str)
fidas_df.columns = fidas_df.columns.str.strip()

# Build timestamp from date + time
fidas_df["timestamp"] = pd.to_datetime(
    fidas_df["date"].astype(str).str.strip() + " " + fidas_df["time"].astype(str).str.strip(),
    format="%m/%d/%Y %I:%M:%S %p",
    errors="coerce"
)

# Drop invalid rows
fidas_df = fidas_df.dropna(subset=["timestamp"])

# Remove seconds by flooring to minute
fidas_df["timestamp"] = fidas_df["timestamp"].dt.floor("min")

# Rename PM columns
fidas_df = fidas_df.rename(
    columns={
        "PM1": "Fidas_PM1",
        "PM2.5": "Fidas_PM2_5",
        "PM10": "Fidas_PM10",
    }
)

fidas_cols = ["Fidas_PM1", "Fidas_PM2_5", "Fidas_PM10"]

# Convert to numeric
for col in fidas_cols:
    fidas_df[col] = pd.to_numeric(fidas_df[col], errors="coerce")

# Keep only needed columns
fidas_df = fidas_df[["timestamp"] + fidas_cols]

# Average by minute
fidas_df = fidas_df.groupby("timestamp", as_index=False).mean()

# =========================================================
# Merge data on timestamp
# =========================================================
merged_df = pd.merge(
    nextpm_df,
    fidas_df,
    on="timestamp",
    how="inner"
)

print("\nMerged data preview:")
print(merged_df.head())

# =========================================================
# Plot function
# =========================================================
def plot_pm(metric_name, sensor1_col, sensor2_col, fidas_col, output_filename):
    plt.figure(figsize=(14, 6))

    plt.plot(merged_df["timestamp"], merged_df[sensor1_col], label="Next PM Sensor 1")
    plt.plot(merged_df["timestamp"], merged_df[sensor2_col], label="Next PM Sensor 2")
    plt.plot(merged_df["timestamp"], merged_df[fidas_col], label="Fidas 200")

    plt.xlabel("Time (Minute Resolution)")
    plt.ylabel(f"{metric_name} (ug/m3)")
    plt.title(f"{metric_name} Comparison: Next PM vs Fidas 200")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    save_path = output_dir / output_filename
    plt.savefig(save_path, dpi=300)
    plt.show()

# =========================================================
# Generate plots
# =========================================================
plot_pm("PM1", "sensor1_PM1mass", "sensor2_PM1mass", "Fidas_PM1", "PM1_comparison.png")
plot_pm("PM2.5", "sensor1_PM2_5mass", "sensor2_PM2_5mass", "Fidas_PM2_5", "PM2_5_comparison.png")
plot_pm("PM10", "sensor1_PM10mass", "sensor2_PM10mass", "Fidas_PM10", "PM10_comparison.png")

print(f"\nPlots saved in: {output_dir}")