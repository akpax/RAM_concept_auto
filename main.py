"""
Add reactions from ETABS output file utilizing ETABS_DataManager class
"""


import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.insert(1, raw_path)

from ram_concept.concept import Concept
from ram_concept.model import Model
from ram_concept.model import StructureType
from ram_concept.force_loading_layer import ForceLoadingLayer
from ram_concept.point_load import PointLoad
from ram_concept.point_2D import Point2D
from etabs_data_manager import ETABS_DataManager

# user specified values
ETABS_output_file_path = r"Y:\Private\austin.paxton\Python_test\Reactions 1_Post VE.xlsx"
model_path = r"Y:\Private\austin.paxton\Python_test\21035_Mat Slab_08182023_cracked_t34_all_loads_noDewater_blank.cpt"
ETABS_coord = [45.667,214.5,-26]  #[ft]
RAM_coord = [45.64,-12.25,0]    #[ft]


# use ETABS_DataManager to read and process ETABS output
data_manager = ETABS_DataManager()
data_manager.read_ETABS(ETABS_output_file_path)
data_manager.calibrate_ETABS_to_RAM(ETABS_coord, RAM_coord)
load_df = data_manager.create_load_df()

#start concept and initialize model and cad_manager
concept = Concept.start_concept(headless=True)
concept.open_file(model_path)
model = Model(concept)
cad_manager = model.cad_manager

#initialize force loading layers
other_dead_ldg = cad_manager.force_loading_layer("Other Dead Loading")
live_ldg = cad_manager.force_loading_layer("Live (Unreducible) Loading")
roof_live_ldg = cad_manager.force_loading_layer("Live (Roof) Loading")

#subset data by load case and add point loads to specific force loading layer
dead_df = load_df[load_df["OutputCase_ETABS"]=="SIDL"]
other_dead_ldg.add_point_loads(dead_df["X_RAM[ft]"].tolist(),
                                dead_df["Y_RAM[ft]"].tolist(),
                                dead_df["Z_RAM[ft]"].tolist(),
                                dead_df["FX_ETABS[kip]"].tolist(),
                                dead_df["FY_ETABS[kip]"].tolist(),
                                dead_df["FZ_ETABS[kip]"].tolist(),
                                dead_df["MX_ETABS[kip-ft]"].tolist(),
                                dead_df["MY_ETABS[kip-ft]"].tolist(),
                                )

live_df = load_df[load_df["OutputCase_ETABS"]=="Live"]
live_ldg.add_point_loads(live_df["X_RAM[ft]"].tolist(),
                                live_df["Y_RAM[ft]"].tolist(),
                                live_df["Z_RAM[ft]"].tolist(),
                                live_df["FX_ETABS[kip]"].tolist(),
                                live_df["FY_ETABS[kip]"].tolist(),
                                live_df["FZ_ETABS[kip]"].tolist(),
                                live_df["MX_ETABS[kip-ft]"].tolist(),
                                live_df["MY_ETABS[kip-ft]"].tolist(),
                                )

roof_live_df = load_df[load_df["OutputCase_ETABS"]=="Roof Live"]
roof_live_ldg.add_point_loads(roof_live_df["X_RAM[ft]"].tolist(),
                                roof_live_df["Y_RAM[ft]"].tolist(),
                                roof_live_df["Z_RAM[ft]"].tolist(),
                                roof_live_df["FX_ETABS[kip]"].tolist(),
                                roof_live_df["FY_ETABS[kip]"].tolist(),
                                roof_live_df["FZ_ETABS[kip]"].tolist(),
                                roof_live_df["MX_ETABS[kip-ft]"].tolist(),
                                roof_live_df["MY_ETABS[kip-ft]"].tolist(),
                                )

# save updated file
model.save_file(r"Y:\Private\austin.paxton\Python_test\21035_Mat Slab_08182023_cracked_t34_all_loads_noDewater.cpt")
concept.shut_down()

# create a for loop that loops through a list and adds 3
