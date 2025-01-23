import os
from waiting_information import get_scan_entry_time, \
                                get_waiting_info
from functions import get_filepaths, \
                      create_df, \
                      create_animation

"""Note the glaring inconsistencies with naming due to inadequate 
redundant naming of multiple areas (particularly zones 6 and 7)"""

data_dir = f"{os.getcwd()}/Data/Alina"
data_dir_2 = f"{os.getcwd()}/Data/Ryan"
image_path = f"{os.getcwd()}/Data/Misc/Map.png"

dir_1_paths = get_filepaths(data_dir)
dir_2_paths = get_filepaths(data_dir_2)

id_1, df_1 = create_df(dir_1_paths)
id_2, df_2 = create_df(dir_2_paths)

print('Dataframe(s) Successfully Created.')

scan_entry_time_1, scan_entry_time_2 = get_scan_entry_time(df_1), get_scan_entry_time(df_2)
waiting_info_1, waiting_info_2 = get_waiting_info(df_1), get_waiting_info(df_2)

# print(scan_entry_time_1)
# print(scan_entry_time_2)
# print()
# print(waiting_info_1)
# print(waiting_info_2)


create_animation([df_1, df_2], 60, image_path, move=True)



