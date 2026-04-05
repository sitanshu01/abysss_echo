# Abyssal Echo - Acoustic Reconnaissance

A Python prototype for reconstructing the probable trajectory of a stealth submarine from noisy hydrophone acoustic observations. The system models sound speed, filters reflections, corrects hydrophone clock drift, derives Doppler velocity, reconstructs the path with multilateration, predicts the future route with a Kalman filter plus ocean-current drift, and exposes the results through a Streamlit dashboard.

## Features

- Simplified Mackenzie sound-speed calculation
- Echo removal by selecting the strongest arrival per `Packet_ID`
- Clock drift correction using a sync buoy at `(0, 0, 0)`
- Doppler-based submarine speed estimation in knots
- Trajectory reconstruction from corrected arrival times and sensor geometry
- Future path projection using velocity vector extrapolation
- Kalman-filter smoothing and forward prediction
- Ocean current drift compensation using a synthetic trench-current field
- Interception window analysis against tactical response assets
- Tactical ocean map for mission planning
- Synthetic demo data generator when CSV inputs are missing
- Plotly + Streamlit dashboard for exploration

## Project Structure

```text
Hackathon_iste/
├── abyssal_echo/
│   ├── __init__.py
│   ├── clock_sync.py
│   ├── dashboard.py
│   ├── data_loader.py
│   ├── doppler_velocity.py
│   ├── echo_filter.py
│   ├── future_prediction.py
│   ├── main.py
│   ├── sound_speed.py
│   └── triangulation.py
├── data/
├── outputs/
├── main.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10+
- `numpy`
- `pandas`
- `scipy`
- `plotly`
- `streamlit`

## Setup

macOS/Homebrew Python commonly blocks global `pip install` with the `externally-managed-environment` error. Use a virtual environment:

```bash
cd /Users/sitanshunayan/Documents/Hackathon_iste
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running the Pipeline

Run the full batch workflow:

```bash
python3 main.py
```

What happens:

- If the required input files do not exist, synthetic acoustic, engine, ocean-current, and tactical-asset datasets are generated automatically.
- The acoustic pipeline runs end to end.
- Output CSV files are written to `outputs/`.

## Launching the Dashboard

Run the pipeline and open the dashboard:

```bash
python3 main.py --dashboard
```

Or launch the dashboard separately after the outputs already exist:

```bash
streamlit run /Users/sitanshunayan/Documents/Hackathon_iste/abyssal_echo/dashboard.py -- outputs
```

Notes:

- Streamlit may ask for an email on first launch. This is optional; press `Enter` to skip.
- The email prompt comes from Streamlit, not from this project.

## Input Data Assumptions

### `acoustic_pings.csv`

Required columns:

- `Packet_ID`
- `Timestamp_ms`
- `Sensor_ID`
- `Received_Frequency_Hz`
- `Intensity_dB`
- `Temperature_C`
- `Salinity_PSU`
- `Depth_m`
- `X`
- `Y`
- `Z`

The prototype also uses:

- `Emission_Timestamp_ms`
- `Ping_Group`
- `Source_Label`

These extra fields are included automatically in the synthetic dataset and are used internally for synchronization and reconstruction.

### `engine_logs.csv`

Required columns:

- `Timestamp_ms`
- `RPM`
- `Blade_Count`

### `ocean_currents.csv`

Synthetic current-field dataset used for forward prediction.

Columns:

- `Timestamp_ms`
- `Depth_m`
- `Current_U_mps`
- `Current_V_mps`
- `Current_W_mps`

### `tactical_assets.csv`

Synthetic interceptor catalog used for interception-window analysis.

Columns:

- `Asset_ID`
- `Asset_Type`
- `Base_X_m`
- `Base_Y_m`
- `Base_Z_m`
- `Max_Speed_knots`
- `Launch_Delay_s`
- `Detection_Radius_m`

## Outputs

After a successful run, `outputs/` will contain:

- `cleaned_acoustic_pings.csv`
- `sensor_clock_drift.csv`
- `doppler_enriched_pings.csv`
- `doppler_speed_summary.csv`
- `reconstructed_trajectory.csv`
- `kalman_smoothed_trajectory.csv`
- `predicted_future_path.csv`
- `interception_windows.csv`
- `interception_summary.csv`
- `tactical_assets_snapshot.csv`

## Dashboard Views

- 3D trajectory comparison of raw vs corrected path
- Predicted path projection over the smoothed track
- 2D top-down path plot
- Environmental HUD for depth and sound speed
- Signal waterfall showing primary arrivals and discarded echoes
- Doppler speedometer in knots
- Interception window panel with best tactical response option
- Tactical ocean map with predicted projection and intercept markers

## Main Processing Steps

1. Compute sound speed from temperature and salinity.
2. Mark the highest-intensity return per packet as the primary signal.
3. Estimate hydrophone clock drift from sync buoy arrivals.
4. Correct timestamps using the per-sensor drift offset.
5. Align pings with engine logs and estimate submarine speed from Doppler shift.
6. Estimate ranges from travel time and reconstruct positions with least-squares multilateration.
7. Smooth the reconstructed track with a constant-velocity Kalman filter.
8. Extrapolate the velocity vector into the future while injecting ocean current drift.
9. Score interception windows for synthetic tactical assets.

## Troubleshooting

### `ModuleNotFoundError: No module named 'numpy'`

You are likely not inside the virtual environment:

```bash
source /Users/sitanshunayan/Documents/Hackathon_iste/.venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

### `externally-managed-environment`

Do not install packages globally. Use the `.venv` steps above.

## Entry Points

- Batch pipeline: [/Users/sitanshunayan/Documents/Hackathon_iste/main.py](/Users/sitanshunayan/Documents/Hackathon_iste/main.py)
- Dashboard: [/Users/sitanshunayan/Documents/Hackathon_iste/abyssal_echo/dashboard.py](/Users/sitanshunayan/Documents/Hackathon_iste/abyssal_echo/dashboard.py)
