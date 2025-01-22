import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta


def create_df(filepaths):

    id = None
    search_string = "Asset Id"
    df = pd.DataFrame(columns=["asset", "date", "time", "area", "status"])
    pd.set_option('display.max_rows', None)  # Display all rows
    pd.set_option('display.max_columns', None)  # Display all columns

    for log in filepaths:
        if 'asset' in log.lower():
            with open(log, 'r') as file:
                for idx, line in enumerate(file):
                    if idx == 0:
                        column_list = line.split(':;')
                        if search_string in column_list:
                            id = column_list.index(search_string)
                    if idx == 1:
                        id = line.split(';')[id]
        else:
            with open(log) as file:
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
    print(len(a))
    for name, age in zip(sorted_df['time'], sorted_df['area']):
        print(name, age)
    for area in sorted_df['area']:
        print(area)
    sorted_df.to_csv('test.csv', index=False)
    return sorted_df


def create_area_animation(df, animation_duration, image_path, coords):
    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')

    total_time = (df['time'].iloc[-1] - df['time'].iloc[0]).total_seconds()
    scaled_two_minutes = (120 / total_time) * animation_duration

    df['normalized_time'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds() / total_time * animation_duration

    img = plt.imread(image_path)
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.imshow(img)
    ax.axis('off')

    df['coords'] = df['area'].map(coords)

    dot, = ax.plot([], [], 'o', color='green', markersize=12, alpha=0.7)

    last_area = None
    area_entry_time = 0

    def update(frame):
        nonlocal last_area, area_entry_time
        animation_time = frame / (animation_duration * 30) * animation_duration

        if animation_time > df['normalized_time'].iloc[-1]:
            return dot,

        # Find correct index for current time
        if animation_time <= df['normalized_time'].iloc[0]:
            current_index = 0
        else:
            mask = df['normalized_time'] <= animation_time
            current_index = mask.sum() - 1

        current_area = df['area'].iloc[current_index]
        print(current_area)
        x, y = df['coords'].iloc[current_index]

        if current_area != last_area:
            area_entry_time = animation_time
            last_area = current_area
            dot.set_color('green')
        else:
            time_in_area = animation_time - area_entry_time
            if time_in_area >= scaled_two_minutes:
                dot.set_color('red')

        dot.set_data([x], [y])
        return dot,

    ani = FuncAnimation(fig, update, frames=int(animation_duration * 30), interval=1000/30, blit=True)
    plt.show()

# def create_area_animation(df, animation_duration=180):
#     df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
#
#     unique_areas = df['area'].unique()
#     area_to_pos = {area: (i // 4, i % 4) for i, area in enumerate(unique_areas)}
#     df['grid_pos'] = df['area'].map(area_to_pos)
#
#     total_time = (df['time'].iloc[-1] - df['time'].iloc[0]).total_seconds()
#     scaled_two_minutes = (120 / total_time) * animation_duration
#
#     df['normalized_time'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds() / total_time * animation_duration
#
#     # Track area transitions
#     df['area_changed'] = df['area'] != df['area'].shift()
#
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.set_xlim(-0.25, 3.25)
#     ax.set_ylim(-0.25, 3.25)
#     ax.set_xticks(range(4))
#     ax.set_yticks(range(4))
#     ax.grid(True)
#
#     fig.subplots_adjust(right=0.8)
#     key_ax = fig.add_axes([0.85, 0.1, 0.1, 0.8])
#     key_ax.axis('off')
#     key_ax.set_title("Area Key", fontsize=10)
#     for i, area in enumerate(unique_areas):
#         key_ax.text(0, len(unique_areas) - i - 1, f"{i + 1}. {area}", fontsize=8)
#
#     dot, = ax.plot([], [], 'o', color='green', markersize=12)
#
#     last_area = None
#     area_entry_time = 0
#
#     def update(frame):
#         nonlocal last_area, area_entry_time
#         animation_time = frame / (animation_duration * 30) * animation_duration
#
#         if animation_time > df['normalized_time'].iloc[-1]:
#             return dot,
#
#         current_index = (df['normalized_time'] > animation_time).idxmax()
#         current_area = df['area'].iloc[current_index]
#         y, x = df['grid_pos'].iloc[current_index]
#
#         # Reset timer if entering new area
#         if current_area != last_area:
#             area_entry_time = animation_time
#             last_area = current_area
#             dot.set_color('green')
#         else:
#             # Check if we should change to red
#             time_in_area = animation_time - area_entry_time
#             if time_in_area >= scaled_two_minutes:
#                 dot.set_color('red')
#
#         dot.set_data([x], [y])
#         return dot,
#
#     ani = FuncAnimation(fig, update, frames=int(animation_duration * 30), interval=1000 / 30, blit=True)
#     plt.show()