import os
from map_coords import coords
from functions import create_df, create_area_animation

"""Note the glaring inconsistencies with naming due to inadequate redundant naming of multiple areas (particularly 
zones 6 and 7)"""

data_dir = f"{os.getcwd()}/Data/Alina"
image_path = f"{os.getcwd()}/Data/Map.png"

files = os.listdir(data_dir)
filepaths = [f"{data_dir}/{x}" for x in files]

df = create_df(filepaths)

print('Dataframe Successfully Created.')

create_area_animation(df, 30, image_path, coords)



