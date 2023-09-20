"""
This script takes the loads determined in find_gov_punch and creates a RAM model 
with columns above slab at each point spring location and the governing loading. 
Note: Only geometry and elements are added. Column properties will be adjusted in 
"""

import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.insert(1, raw_path)

from ram_concept.concept import Concept
from ram_concept.model import Model
from ram_concept.column import Column
from ram_concept.column import DefaultColumn

import pandas as pd


RAM_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\punching_checks\punching_model_inverted_col_09-14-23.cpt"
csv_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\punching_checks\net_reactions_governing.csv"


concept = Concept.start_concept(headless=True)
concept.open_file(RAM_path)
model = Model(concept)
cad_manager = model.cad_manager
struct_layer = cad_manager.structure_layer

point_springs = struct_layer.point_springs

for spring in point_springs:
    struct_layer.add_column(spring.location)


# Access loads and coordinates in net_reactions csv
load_df = pd.read_csv(csv_path)
#convert keys back to x and y coordinates
def convert_key_to_coord(key):
    x_cord = float(key.split("_")[0])
    y_cord = float(key.split("_")[1])
    return x_cord, y_cord

load_df[["x_coord", "y_coord"]] = load_df["key"].apply(lambda key: convert_key_to_coord(key)).apply(pd.Series)

x = load_df["x_coord"].to_list()
y = load_df["y_coord"].to_list()
Fz = load_df["max_net_reaction[kip]"].to_list()
print(load_df.head().to_markdown())


#add loads to model
dead_ldg = cad_manager.force_loading_layer("Other Dead Loading")
dead_ldg.add_point_loads(x,y,Fz=Fz)

# # save updated file
model.save_file(r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\punching_checks\out_punching_model_inverted_col_09-14-23.cpt")

concept.shut_down()
