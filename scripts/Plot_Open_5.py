import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# File paths
fidas_file = r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\Fidas_Open_05__April_2026.txt"
nextpm_file = r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\Open_05__April_2026.csv"

# Output folder
output_dir = Path(r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed\plots")
output_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load Next PM CSV data safely
# -----------------------------
nextpm_df = pd.read_csv(nextpm_file, dtype=str)

# Clean column names
nextpm_df.columns = nextpm_df.columns.str.strip()

# Clean timestamp text
nextpm_df["timestamp"] = nextpm_df["timestamp"].astype(str).str.strip()

# Optional: print first few raw timestamps for debugging
print("Raw Next PM timestamps:")
print(nextpm_df["timestamp"].head())

# Convert timestamp safely
nextpm_df["timestamp"] = pd.to_datetime(
    nextpm_df["timestamp"],
    format="%Y-%m-%dT%H:%M:%S.%f",
    errors="coerce"
)

# Drop bad rows
nextpm_df = nextpm_df.dropna(subset=["timestamp"])

# Remove seconds
nextpm_df["timestamp"] = nextpm_df["timestamp"].dt.floor("min")

# Convert numeric columns
nextpm_numeric_cols = [
    "sensor1_PM1mass",
    "sensor1_PM2_5mass",
    "sensor1_PM10mass",
    "sensor2_PM1mass",
    "sensor2_PM2_5mass",
    "sensor2_PM10mass",
]

for col in nextpm_numeric_cols:
    nextpm_df[col] = pd.to_numeric(nextpm_df[col], errors="coerce")

# Keep required columns
nextpm_df = nextpm_df[["timestamp"] + nextpm_numeric_cols]

# Group by minute
nextpm_df = nextpm_df.groupby("timestamp").mean().reset_index()

# -----------------------------
# Load Fidas TXT data
# -----------------------------
fidas_df = pd.read_csv(fidas_file, sep="\t", dtype=str)
fidas_df.columns = fidas_df.columns.str.strip()

fidas_df["timestamp"] = pd.to_datetime(
    fidas_df["date"].astype(str).str.strip() + " " + fidas_df["time"].astype(str).str.strip(),
    errors="coerce"
)

fidas_df["timestamp"] = fidas_df["timestamp"].dt.floor("min")

fidas_df = fidas_df.rename(
    columns={
        "PM1": "Fidas_PM1",
        "PM2.5": "Fidas_PM2_5",
        "PM10": "Fidas_PM10",
    }
)

fidas_cols = ["Fidas_PM1", "Fidas_PM2_5", "Fidas_PM10"]
for col in fidas_cols:
    fidas_df[col] = pd.to_numeric(fidas_df[col], errors="coerce")

fidas_df = fidas_df[["timestamp"] + fidas_cols]
fidas_df = fidas_df.dropna(subset=["timestamp"])
fidas_df = fidas_df.groupby("timestamp").mean().reset_index()

# -----------------------------
# Plot function
# -----------------------------
def plot_pm(metric_name, s1, s2, fidas_col, filename):
    plt.figure(figsize=(14, 6))
    plt.plot(nextpm_df["timestamp"], nextpm_df[s1], label="Next PM Sensor 1")
    plt.plot(nextpm_df["timestamp"], nextpm_df[s2], label="Next PM Sensor 2")
    plt.plot(fidas_df["timestamp"], fidas_df[fidas_col], label="Fidas 200")
    plt.xlabel("Time (Minute Resolution)")
    plt.ylabel(f"{metric_name} (ug/m3)")
    plt.title(f"{metric_name} Comparison")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300)
    plt.show()

# -----------------------------
# Generate plots
# -----------------------------
plot_pm("PM1", "sensor1_PM1mass", "sensor2_PM1mass", "Fidas_PM1", "PM1_minute.png")
plot_pm("PM2.5", "sensor1_PM2_5mass", "sensor2_PM2_5mass", "Fidas_PM2_5", "PM2_5_minute.png")
plot_pm("PM10", "sensor1_PM10mass", "sensor2_PM10mass", "Fidas_PM10", "PM10_minute.png")

print("Plots generated successfully.")