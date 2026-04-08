import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# =========================================================
# FILE PATHS
# =========================================================
base_path = Path(r"C:\Users\Admin\Documents\GitHub\PM-Mesh-Design-Reliability-Test\data\processed")

files = {
    "closed_nextpm": base_path / "Closed_02_April_2026.csv",
    "closed_fidas": base_path / "Fidas_Closed_02_April_2026.txt",
    "open_nextpm": base_path / "Open_05__April_2026.csv",
    "open_fidas": base_path / "Fidas_Open_05__April_2026.txt",
}

output_dir = base_path / "validation_results"
output_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# FUNCTIONS
# =========================================================
def load_nextpm(file_path):
    df = pd.read_csv(file_path, dtype=str)
    df.columns = df.columns.str.strip()

    df["timestamp"] = df["timestamp"].astype(str).str.strip()
    df["timestamp"] = df["timestamp"].str.replace(r"^026-", "2026-", regex=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(subset=["timestamp"])
    df["timestamp"] = df["timestamp"].dt.floor("min")

    cols = [
        "sensor1_PM1mass", "sensor1_PM2_5mass", "sensor1_PM10mass",
        "sensor2_PM1mass", "sensor2_PM2_5mass", "sensor2_PM10mass",
    ]

    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[["timestamp"] + cols]
    df = df.groupby("timestamp", as_index=False).mean()

    df["PM1_sensor1"] = df["sensor1_PM1mass"]
    df["PM2_5_sensor1"] = df["sensor1_PM2_5mass"]
    df["PM10_sensor1"] = df["sensor1_PM10mass"]

    df["PM1_sensor2"] = df["sensor2_PM1mass"]
    df["PM2_5_sensor2"] = df["sensor2_PM2_5mass"]
    df["PM10_sensor2"] = df["sensor2_PM10mass"]

    df["PM1_sensor_avg"] = df[["sensor1_PM1mass", "sensor2_PM1mass"]].mean(axis=1)
    df["PM2_5_sensor_avg"] = df[["sensor1_PM2_5mass", "sensor2_PM2_5mass"]].mean(axis=1)
    df["PM10_sensor_avg"] = df[["sensor1_PM10mass", "sensor2_PM10mass"]].mean(axis=1)

    return df[[
        "timestamp",
        "PM1_sensor1", "PM2_5_sensor1", "PM10_sensor1",
        "PM1_sensor2", "PM2_5_sensor2", "PM10_sensor2",
        "PM1_sensor_avg", "PM2_5_sensor_avg", "PM10_sensor_avg"
    ]]


def load_fidas(file_path):
    df = pd.read_csv(file_path, sep="\t", dtype=str)
    df.columns = df.columns.str.strip()

    df["timestamp"] = pd.to_datetime(
        df["date"].astype(str).str.strip() + " " + df["time"].astype(str).str.strip(),
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp"])
    df["timestamp"] = df["timestamp"].dt.floor("min")

    df = df.rename(columns={
        "PM1": "PM1_fidas",
        "PM2.5": "PM2_5_fidas",
        "PM10": "PM10_fidas",
    })

    for col in ["PM1_fidas", "PM2_5_fidas", "PM10_fidas"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[["timestamp", "PM1_fidas", "PM2_5_fidas", "PM10_fidas"]]
    df = df.groupby("timestamp", as_index=False).mean()

    return df


def merge_data(nextpm_df, fidas_df):
    df = pd.merge(nextpm_df, fidas_df, on="timestamp", how="inner")
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_metrics(df, sensor_col, fidas_col):
    temp = df[[sensor_col, fidas_col]].dropna().copy()

    if len(temp) < 2:
        return np.nan, np.nan, np.nan, np.nan, 0

    y_pred = temp[sensor_col]
    y_true = temp[fidas_col]

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    bias = (y_pred - y_true).mean()

    return rmse, mae, r2, bias, len(temp)


def plot_timeseries(df, metric, condition_name):
    plt.figure(figsize=(14, 6))
    plt.plot(df["timestamp"], df[f"{metric}_sensor1"], label="Next PM Sensor 1")
    plt.plot(df["timestamp"], df[f"{metric}_sensor2"], label="Next PM Sensor 2")
    plt.plot(df["timestamp"], df[f"{metric}_sensor_avg"], label="Next PM Average")
    plt.plot(df["timestamp"], df[f"{metric}_fidas"], label="Fidas 200")
    plt.xlabel("Time")
    plt.ylabel(f"{metric.replace('_', '.')} (ug/m3)")
    plt.title(f"{metric.replace('_', '.')} Time Series Comparison - {condition_name}")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / f"{condition_name}_{metric}_timeseries.png", dpi=300)
    plt.close()


def plot_scatter(df, metric, condition_name):
    temp = df[[f"{metric}_sensor_avg", f"{metric}_fidas"]].dropna().copy()
    if temp.empty:
        return

    plt.figure(figsize=(6, 6))
    plt.scatter(temp[f"{metric}_fidas"], temp[f"{metric}_sensor_avg"])
    min_val = min(temp[f"{metric}_fidas"].min(), temp[f"{metric}_sensor_avg"].min())
    max_val = max(temp[f"{metric}_fidas"].max(), temp[f"{metric}_sensor_avg"].max())
    plt.plot([min_val, max_val], [min_val, max_val], linestyle="--")
    plt.xlabel("Fidas 200 (ug/m3)")
    plt.ylabel("Next PM Average (ug/m3)")
    plt.title(f"{metric.replace('_', '.')} Scatter Plot - {condition_name}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_dir / f"{condition_name}_{metric}_scatter.png", dpi=300)
    plt.close()


def analyze_condition(condition_name, nextpm_path, fidas_path):
    nextpm_df = load_nextpm(nextpm_path)
    fidas_df = load_fidas(fidas_path)
    merged_df = merge_data(nextpm_df, fidas_df)

    merged_df.to_csv(output_dir / f"{condition_name}_merged_data.csv", index=False)

    results = []
    metrics = ["PM1", "PM2_5", "PM10"]
    sensor_versions = ["sensor1", "sensor2", "sensor_avg"]

    for metric in metrics:
        plot_timeseries(merged_df, metric, condition_name)
        plot_scatter(merged_df, metric, condition_name)

        for sensor_version in sensor_versions:
            sensor_col = f"{metric}_{sensor_version}"
            fidas_col = f"{metric}_fidas"

            rmse, mae, r2, bias, n = compute_metrics(merged_df, sensor_col, fidas_col)

            results.append({
                "Condition": condition_name,
                "Metric": metric.replace("_", "."),
                "Sensor": sensor_version,
                "Samples": n,
                "RMSE": rmse,
                "MAE": mae,
                "R2": r2,
                "Bias": bias
            })

    return merged_df, pd.DataFrame(results)


# =========================================================
# RUN ANALYSIS
# =========================================================
closed_df, closed_results = analyze_condition(
    "Mesh",
    files["closed_nextpm"],
    files["closed_fidas"]
)

open_df, open_results = analyze_condition(
    "No_Mesh",
    files["open_nextpm"],
    files["open_fidas"]
)

all_results = pd.concat([closed_results, open_results], ignore_index=True)
all_results.to_csv(output_dir / "validation_summary.csv", index=False)

print("\n=== VALIDATION RESULTS ===")
print(all_results.to_string(index=False))

# =========================================================
# SIMPLE COMPARISON TABLE USING AVERAGE OF BOTH SENSORS
# =========================================================
avg_only = all_results[all_results["Sensor"] == "sensor_avg"].copy()
avg_only.to_csv(output_dir / "validation_summary_sensor_average.csv", index=False)

print("\n=== SENSOR AVERAGE COMPARISON ===")
print(avg_only.to_string(index=False))

# =========================================================
# BASIC INTERPRETATION
# =========================================================
print("\n=== INTERPRETATION GUIDE ===")
print("Lower RMSE and MAE = better agreement with Fidas")
print("Bias > 0 = Next PM overestimates")
print("Bias < 0 = Next PM underestimates")
print("R2 closer to 1 = better correlation")
print(f"\nResults saved in: {output_dir}")