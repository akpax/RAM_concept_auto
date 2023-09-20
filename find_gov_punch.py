"""
This script combines factored columns loads with point spring loads on a load case basis and then find the governing punching force for each load case. 
"""

import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.insert(1, raw_path)

from ram_concept.concept import Concept
from ram_concept.model import Model
from ram_concept.model import StructureType
from ram_concept.force_loading_layer import ForceLoadingLayer
from ram_concept.element_layer import ElementLayer
from ram_concept.point_load import PointLoad
from ram_concept.point_2D import Point2D
from ram_concept.result_layers import ReactionContext


import pandas as pd
import re

from element_finder import ElementFinder
from etabs_data_manager import ETABS_DataManager

def create_key(x_cord: float, y_cord: float):
    # create keys for load combo dataframes
    return f"{round(x_cord,2)}_{round(y_cord,2)}"

def consolidate_rename(df):
    df = df[["key","FZ_ETABS[kip]","OutputCase_ETABS"]]
    df.rename(columns={"FZ_ETABS[kip]": f'FZ_{df["OutputCase_ETABS"].iloc[0]}[kip]'}, inplace=True)
    df=df.drop(["OutputCase_ETABS"],axis=1)
    return df

def merge_dfs_in_dict(dict, merge_cols: list):
    #merge loads based on key
    for i,df in enumerate(dict.values()):
        if i==0:
            merged_df=df
        else:
            merged_df = pd.merge(merged_df,df, on=merge_cols, how="inner")
    return merged_df


# load up point spring reactions from .xlsx file 
excel_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\point_spring_reactions_09-07-23\tension_strength\tension_point_springs_strength.xlsx"
ps_dict = {}  #initialize dict to store all the point spreing(ps) dataframes

xls = pd.ExcelFile(excel_path)
sheet_names = xls.sheet_names

for sheet_name in sheet_names:
    sheet_df = pd.read_excel(xls, sheet_name, header=0)
    sheet_df.columns = [col.strip() for col in sheet_df.columns]   #remove leading and trailing whitespace from column headers
    ps_dict[sheet_name] = sheet_df  #add ps means point spring


# acquire point spring locations and IDs and merge to point springs dfs
RAM_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\21035_Mat Slab_09062023_cracked_t34_all_loads_noDewater.cpt"
#start concept and open model
concept = Concept.start_concept(headless=True)
concept.open_file(RAM_path)
RAM_model = Model(concept)

element_finder = ElementFinder(RAM_model)
RAM_spring_locations = element_finder.find_point_springs(return_df=True)


#merge point spring locations to point spring_forces for each dataframe in ps_dict
for key,ps_df in ps_dict.items(): #ps = point spring
    ps_merged_df =  pd.merge(ps_df, RAM_spring_locations, on="ID")
    ps_dict[key] = ps_merged_df

#reformat ps_dict so that it is ready for merging  create key and remove columnbs so only key, ID, and force+LC remain
for key,df in ps_dict.items():
    df["x_cord"] = df["x_cord"].apply(lambda x: round(x,2))
    df["y_cord"] = df["y_cord"].apply(lambda x: round(x,2))
    df["key"] = df.apply(lambda row: create_key(row["x_cord"], row["y_cord"]), axis=1)
    df["Std. Fz (Kips)"] = df["Std. Fz (Kips)"]*-1    # inverse spring reactions so they have same sign convention as loads (downwards is positive)
    df.rename({"Std. Fz (Kips)": key+"_ps"},axis=1, inplace=True)
    df = df[["key", "ID", key+"_ps"]]
    ps_dict[key] = df


#convert updated dict to ps_df
ps_df = merge_dfs_in_dict(ps_dict, merge_cols=["ID", "key"])
print(ps_df.head().to_markdown())


# load ETABS loads and create factored loads
ETABS_output_phase1 = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\Self-weight reactions_Post VE.xlsx" #phase 1 is self-dead
ETABS_output_phase2 = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\Reactions 1_Post VE.xlsx"  #phase 2 is super dead, live , roof live
#provide ETABS coordinate and RAM coordinate at same structure location for calibration
ETABS_coord = [45.667,214.5,-26]  #[ft] 
RAM_coord = [45.64,-12.25,0]    #[ft]

etabs_data_manager = ETABS_DataManager()
#read phase 2 loads
etabs_data_manager.read_ETABS(ETABS_output_phase2)
etabs_data_manager.calibrate_ETABS_to_RAM(ETABS_coord, RAM_coord)
load_df = etabs_data_manager.create_load_df()

#read phase 1 loads (self-dead)
etabs_data_manager.read_ETABS(ETABS_output_phase1)
etabs_data_manager.calibrate_ETABS_to_RAM(ETABS_coord, RAM_coord)
SIDL_df = etabs_data_manager.create_load_df()


load_df_dict = {}
load_df_dict["self_dead_df"] = SIDL_df
load_df_dict["super_dead_df"] = load_df[load_df["OutputCase_ETABS"]=="SIDL"]
load_df_dict["live_df"] = load_df[load_df["OutputCase_ETABS"]=="Live"]
load_df_dict["roof_live_df"] = load_df[load_df["OutputCase_ETABS"]=="Roof Live"]



#apply create key fucntion to each df in load_dict
load_df_dict = {dict_key: df.assign(key=df.apply(lambda row: create_key(row['X_RAM[ft]'],row['Y_RAM[ft]']), axis=1)) for dict_key,df in load_df_dict.items()}
 
load_df_dict = {key: consolidate_rename(df) for key,df in load_df_dict.items()}



loads_df = merge_dfs_in_dict(load_df_dict, merge_cols="key")

#combine self wieght and SIDL into cummulative dead load
loads_df["FZ_dead[kip]"] = loads_df.apply(lambda row: row["FZ_Self-weight[kip]"]+row["FZ_SIDL[kip]"], axis=1 )
print(loads_df.head().to_markdown())

#create load combos and add factored loads to loads df
loads_df["0 64D+Ehx+Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D+Ehx-Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D-Ehx+Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D-Ehx-Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D-Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D-Ehx+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D+Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D+Ehx+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 4D+1 6H_load"] = loads_df.apply(lambda row: 1.4*row["FZ_dead[kip]"], axis=1)
loads_df["1 2D+L+1 6Lr+1 6H_load"] = loads_df.apply(lambda row: 1.2*row["FZ_dead[kip]"]+row["FZ_Live[kip]"]+1.6*row["FZ_Roof Live[kip]"], axis=1)
loads_df["1 2D+1 6L+0 5Lr+1 6H_load"] = loads_df.apply(lambda row: 1.2*row["FZ_dead[kip]"]+1.6*row["FZ_Live[kip]"]+0.5*row["FZ_Roof Live[kip]"], axis=1)
loads_df["0 64D-Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D-Ehx+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D+Ehy+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["0 64D+Ehx+1 6H_load"] = loads_df.apply(lambda row: 0.64*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D+Ehx+Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D+Ehx-Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D-Ehx-Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)
loads_df["1 464D-Ehx+Ehy+0 9H_load"] = loads_df.apply(lambda row: 1.464*row["FZ_dead[kip]"], axis=1)

print(loads_df.head().to_markdown())

print(loads_df["key"].head(20))
print(ps_df["key"].head(20))

#merge loads_df and ps_df
load_ps_df = pd.merge(ps_df,loads_df, how="left", on="key")

#sum matching load cases
summed_df = load_ps_df[['key', 'ID']].copy()

for column in load_ps_df.columns:
    if column.endswith("_ps") or column.endswith("_load"):
        prefix = column.rsplit("_", 1)[0]  # Extract the prefix (e.g., '0 64D+Ehx+Ehy+1 6H')
        matching_columns = [col for col in load_ps_df.columns if col.startswith(prefix)]
        # print(load_ps_df[matching_columns].head(3))
        # print(load_ps_df[matching_columns].sum(axis=1).head(3))
        summed_df[prefix+"_sum"] = load_ps_df[matching_columns].sum(axis=1)  #notes that point springs reactions have been inversesed so tehy go in same direction as loads.. 
    

# find maximum and minimum summed reactions and add to df
summed_df["max_net_reaction[kip]"] = summed_df.filter(like="_sum").max(axis=1)
summed_df["min_net_reaction[kip]"] = summed_df.filter(like="_sum").min(axis=1)

# Find the maximum and minimum values and their corresponding prefix
max_cols = summed_df.filter(like='_sum').idxmax(axis=1)
min_cols = summed_df.filter(like='_sum').idxmin(axis=1)

# Extract the prefixes from the column names
summed_df['max_LC'] = max_cols.str.extract(r'(.+)_sum')
summed_df['min_LC'] = min_cols.str.extract(r'(.+)_sum')

export_df = summed_df[["key", "ID", "max_net_reaction[kip]", "min_net_reaction[kip]", "max_LC", "min_LC"]]

print(export_df.head().to_markdown())

#export results to .csv
export_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\point_spring_reactions_09-07-23\net_forces_(pile+load)"
export_df.to_csv(export_path + r"\net_reactions_governing.csv", index=False)
