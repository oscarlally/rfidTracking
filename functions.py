import os
import random
import matplotlib
import pandas as pd
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mapping_info import coords, roles
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation


def get_filepaths(data_dir):
    files = os.listdir(data_dir)
    filepaths = [f"{data_dir}/{x}" for x in files]
    return filepaths


def add_lists(list1, list2):
    combined_list = []
    for i, j in zip(list1, list2):
        combined_list.append(i + j)
    return combined_list


def create_df(filepaths):

    id = None
    search_string = "Asset Id"
    df = pd.DataFrame(columns=["asset", "date", "time", "area", "status"])
    pd.set_option('display.max_rows', None)  # Display all rows
    pd.set_option('display.max_columns', None)  # Display all columns

    log_asset = next((item for item in filepaths if 'asset' in item.lower()), None)
    log_event = next((item for item in filepaths if 'event' in item.lower()), None)
    if log_asset is not None:
        with open(log_asset, 'r') as file:
            for idx, line in enumerate(file):
                if idx == 0:
                    column_list = line.split(':;')
                    if search_string in column_list:
                        id_idx = column_list.index(search_string)
                if idx == 1:
                    id = line.split(';')[id_idx]
    if log_event is not None:
        with open(log_event) as file:
            for idx, line in enumerate(file):
                events_dict = {}
                if idx != 0:
                    components = line.split(';')
                    events_dict["asset"] = id
                    events_dict["date"] = components[0].split(' ')[0]
                    events_dict["time"] = components[0].split(' ')[1]
                    try:
                        events_dict["area"] = components[2].split('>')[1]
                    except IndexError:
                        events_dict["area"] = 'Out of bounds'
                    events_dict["status"] = components[3]
                    df = pd.concat([df, pd.DataFrame([events_dict])], ignore_index=True)

    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
    sorted_df = df.sort_values(by='time')
    a = list(set(df['area']))
    sorted_df.to_csv(f'{os.getcwd()}/Data/Misc/test_{id}.csv', index=False)
    return id, sorted_df


def create_animation(dfs, animation_duration, image_path, coords=coords, roles=roles, move=True, fr=5):

    # Combine time ranges from all DataFrames
    all_times = pd.concat([df['time'] for df in dfs])
    earliest_time = pd.to_datetime(all_times.min(), format='%H:%M:%S')
    latest_time = pd.to_datetime(all_times.max(), format='%H:%M:%S')
    total_time = (latest_time - earliest_time).total_seconds()

    # Normalize times for each DataFrame
    for df in dfs:
        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
        df['normalized_time'] = (df['time'] - earliest_time).dt.total_seconds() / total_time * animation_duration
        df['coords'] = df['area'].map(coords)  # Ensure this maps to tuples or lists

    # Load background image
    img = plt.imread(image_path)
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.imshow(img)
    ax.axis('off')

    # Marker styles for roles
    role_styles = {
        'staff': {'marker': 'x', 'color': 'blue', 'alpha': 0.7, 'markersize': 12},
        'patients': {'marker': 'o', 'color': 'green', 'alpha': 0.7, 'markersize': 12},
    }

    # Role-based legend handles
    legend_handles = []
    for role, style in role_styles.items():
        handle, = ax.plot([], [], style['marker'], color=style['color'],
                          alpha=style['alpha'], markersize=style['markersize'],
                          label=role)
        legend_handles.append(handle)

    # Unknown role handle
    unknown_handle, = ax.plot([], [], 'o', color='gray', alpha=0.5,
                              markersize=10, label='Unknown')
    legend_handles.append(unknown_handle)

    # Create markers for each DataFrame based on roles
    markers = []
    asset_legend_handles = []
    asset_legend_labels = []

    for df in dfs:
        df['role'] = df['asset'].apply(lambda x: next((role for role, ids in roles.items() if x in ids), 'unknown'))
        marker_group = {}

        # Create markers for roles
        for role, style in role_styles.items():
            marker_group[role], = ax.plot([], [], style['marker'],
                                          color=style['color'],
                                          alpha=style['alpha'],
                                          markersize=style['markersize'])

        # Add a default marker for unknown roles
        marker_group['unknown'], = ax.plot([], [], 'o', color='gray', alpha=0.5, markersize=10)

        markers.append(marker_group)

        # Create legend handles for unique assets
        for idx, row in df.iterrows():
            role = row['role']
            asset = row['asset']
            style = role_styles.get(role, {'marker': 'o', 'color': 'gray', 'markersize': 10})

            if asset not in asset_legend_labels:
                handle, = ax.plot([], [], style['marker'],
                                  color=style['color'],
                                  markersize=style['markersize'],
                                  alpha=0.7,
                                  label=asset)
                asset_legend_handles.append(handle)
                asset_legend_labels.append(asset)

    # Interpolation state for each marker
    states = [{'last_coords': None, 'start_coords': None, 'end_coords': None,
               'start_time': 0, 'end_time': 0} for _ in dfs]

    def update(frame):
        animation_time = frame / (animation_duration * fr) * animation_duration

        updated_markers = []
        for i, df in enumerate(dfs):
            state = states[i]
            marker_group = markers[i]

            if animation_time > df['normalized_time'].iloc[-1]:
                updated_markers.extend(marker_group.values())
                continue

            # Find the current and next index for the animation time
            if animation_time <= df['normalized_time'].iloc[0]:
                current_index = 0
            else:
                mask = df['normalized_time'] <= animation_time
                current_index = mask.sum() - 1

            if current_index == len(df) - 1:
                next_index = current_index
            else:
                next_index = current_index + 1

            # Determine the start and end coordinates and times
            if (state['start_coords'] is None or state['end_coords'] is None or
                    animation_time >= state['end_time'] or animation_time < state['start_time']):
                state['start_coords'] = add_lists(df['coords'].iloc[current_index],
                                                  [random.randint(-5, 5), random.randint(-5, 5)])
                state['end_coords'] = add_lists(df['coords'].iloc[next_index],
                                                [random.randint(-5, 5), random.randint(-5, 5)])
                state['start_time'] = df['normalized_time'].iloc[current_index]
                state['end_time'] = df['normalized_time'].iloc[next_index]

            # Ensure coords are tuples or lists
            if not isinstance(state['start_coords'], (list, tuple)) or not isinstance(state['end_coords'],
                                                                                      (list, tuple)):
                raise ValueError(
                    f"Coordinates must be lists or tuples. Got {state['start_coords']}, {state['end_coords']}")

            # Interpolate the position
            if move:
                t_ratio = (animation_time - state['start_time']) / (state['end_time'] - state['start_time']) if state[
                                                                                                                    'end_time'] > \
                                                                                                                state[
                                                                                                                    'start_time'] else 0
                interpolated_x = (1 - t_ratio) * state['start_coords'][0] + t_ratio * state['end_coords'][0]
                interpolated_y = (1 - t_ratio) * state['start_coords'][1] + t_ratio * state['end_coords'][1]
            else:
                # If move is False, instantly move to the next location
                interpolated_x = state['end_coords'][0]
                interpolated_y = state['end_coords'][1]

            # Update the appropriate marker for the role
            current_role = df['role'].iloc[current_index]
            marker = marker_group.get(current_role)

            if marker is None:
                raise ValueError(f"Marker for role '{current_role}' not found in marker_group.")

            # Change color if waiting time exceeds 2 minutes
            wait_time = animation_time - state['start_time']
            if wait_time > 2:  # Threshold in minutes
                marker.set_color('red')
            else:
                # Reset to default color
                marker.set_color(role_styles.get(current_role, {'color': 'gray'})['color'])

            # Update the marker's position
            marker.set_data([interpolated_x], [interpolated_y])
            updated_markers.append(marker)

        return updated_markers

    ani = FuncAnimation(fig, update, frames=int(animation_duration * fr), interval=1000 / fr, blit=True)
    plt.legend(handles=legend_handles, loc='upper left', title='Roles')
    plt.legend(handles=asset_legend_handles,
               labels=asset_legend_labels,
               loc='upper right',
               title='Asset IDs',
               bbox_to_anchor=(1.25, 1))
    plt.tight_layout()
    ani.save(f"{os.getcwd()}/Data/Misc/animation_tracker.mp4", writer='ffmpeg', fps=fr)
    plt.show()
