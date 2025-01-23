import pandas as pd


def get_waiting_info(events_df):

    # Combine 'date' and 'time' columns into a single datetime column
    events_df["time"] = events_df["time"].astype(str)
    events_df["datetime"] = pd.to_datetime(events_df["date"] + " " + events_df["time"])

    # Calculate the time difference between consecutive rows
    events_df["time_spent"] = events_df["datetime"].diff().shift(-1).dt.total_seconds()

    # Group by 'area' and sum the time spent in each area
    time_spent_by_area = events_df.groupby("area")["time_spent"].sum().reset_index()

    # Rename columns for clarity
    time_spent_by_area.columns = ["Area", "Time Spent (seconds)"]

    # Drop areas with NaN time (e.g., the last row's time difference)
    time_spent_by_area = time_spent_by_area.dropna()

    return time_spent_by_area


def get_scan_entry_time(events_df):

    # Get the entry time to the mri scanner
    filtered_gstt_df = events_df[events_df["area"] == "GSTT MRI"].copy()
    filtered_kcl_df = events_df[events_df["area"] == "KCL MRI"].copy()

    if len(filtered_kcl_df) != 0:
        filtered_kcl_df["time"] = filtered_kcl_df["time"].astype(str)
        filtered_kcl_df["datetime"] = pd.to_datetime(filtered_kcl_df["date"] + " " + filtered_kcl_df["time"])
        earliest_kcl_row = filtered_kcl_df.nsmallest(1, "datetime")
        return earliest_kcl_row[["asset", "date", "time", "area"]]

    if len(filtered_gstt_df) != 0:
        filtered_gstt_df["time"] = filtered_gstt_df["time"].astype(str)
        filtered_gstt_df["datetime"] = pd.to_datetime(filtered_gstt_df["date"] + " " + filtered_gstt_df["time"])
        earliest_gstt_row = filtered_gstt_df.nsmallest(1, "datetime")
        return earliest_gstt_row[["asset", "date", "time", "area"]]
