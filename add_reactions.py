import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.insert(1, raw_path)

import pandas as pd
from ram_concept.concept import Concept
from ram_concept.model import Model
from ram_concept.model import StructureType
from ram_concept.force_loading_layer import ForceLoadingLayer
from ram_concept.point_load import PointLoad
from ram_concept.point_2D import Point2D

def calibrate_ETABS_to_RAM(ETABs_coord: list, RAM_coord:list):
    """
    this function takes the same point in ETABs coordinates and in RAM coordinates and creates 
    delta values to adjust coordinates of ETABs loads for proper location into RAM concept

    Assumes coordinates are given in form [x_cord, y_cord]
    """
    location_delta = [RAM_coord[0]-ETABs_coord[0],RAM_coord[1]-ETABs_coord[1]]
    return location_delta

ETABs_data_path = r"C:\Users\austin.paxton\OneDrive - Mar Structural Design\Documents\API Testing\test_data\Self-weight reactions_Post VE.xlsx"
model_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\21035_Mat Slab_08112023_finished_finalized.cpt"
#import reactions and cordinate sheets
reactions_df = pd.read_excel(ETABs_data_path,sheet_name=0, header=1)
reactions_df = reactions_df.rename({"Unique Name": "UniqueName"}, axis =1)
coordinate_df = pd.read_excel(ETABs_data_path,sheet_name=1, header=1)


# ToDo: create function to import sheets and add units from second row instead of droping those rows entirely
reactions_df.drop(reactions_df.index[0], inplace=True)
coordinate_df.drop(coordinate_df.index[0], inplace=True)

# #check outputs
# print(reactions_df.head)
# print("_____________________________________________\n_________________________________")
# print(coordinate_df.head)

# merge reactions and cordinate sheets 
df = pd.merge(reactions_df, coordinate_df, on="UniqueName")

#create forces_df converted to floats
forces_df = df[["FX","FY","FZ","MX","MY","MZ","X","Y","Z"]].astype("float")
# print(df.describe())
# print(df.head)

#create a list of of tuples in form (Fz, x,y)
#ETABs_forces = forces_df[["FZ","X","Y"]].apply(tuple,axis=1).tolist()
FZ = forces_df["FZ"].tolist() #[kip]
X_ETABs = forces_df["X"].tolist()  #[ft]
Y_ETABs = forces_df["Y"].tolist()  #[ft]



ETABs_coord = [45.667,214.5]  #[ft]
RAM_coord = [45.64,-12.25]    #[ft]
#Note: These coordinates were taken by going into both ETABs and RAM models and finding the same point

location_delta = calibrate_ETABS_to_RAM(ETABs_coord,RAM_coord)
print(f"Location Delta: {location_delta}")

#convert ETABs locations to RAM locations
X_RAM = [X+location_delta[0] for X in X_ETABs]
Y_RAM = [Y+location_delta[1] for Y in Y_ETABs]


#######

concept = Concept.start_concept(headless=False)
concept.open_file(model_path)

model = Model(concept)
cad_manager = model.cad_manager

dead_ldg = cad_manager.force_loading_layer("Self-Dead Loading") #initialize dead loading layer

#elevation 
elevation = [0]*len(FZ)
dead_point_load = dead_ldg.add_point_loads(X_RAM, Y_RAM, elevation, Fz=FZ )


# save updated file
model.save_file(
    r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\21035_Mat Slab_08162023_finished_finalized.cpt")

concept.shut_down()
