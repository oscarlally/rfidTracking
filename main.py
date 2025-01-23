import os
from functions import get_filepaths, \
                      create_df, \
                      create_animation

"""Note the glaring inconsistencies with naming due to inadequate 
redundant naming of multiple areas (particularly zones 6 and 7)"""

data_dir = f"{os.getcwd()}/Data/Alina"
data_dir_2 = f"{os.getcwd()}/Data/Ryan"
image_path = f"{os.getcwd()}/Data/Map.png"

dir_1_paths = get_filepaths(data_dir)
dir_2_paths = get_filepaths(data_dir_2)

id_1, df_1 = create_df(dir_1_paths)
id_2, df_2 = create_df(dir_2_paths)

print('Dataframe(s) Successfully Created.')

create_animation([df_1, df_2], 60, image_path, move=True)



