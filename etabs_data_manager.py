import pandas as pd

##TO DO: Make manager robust against units -> have user specify initialy and then assert equal and return errors if not 
class ETABS_DataManager:
    def __init__(self):
        self.data_frames = {}

    def read_ETABS(self,file_path):
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        for sheet_name in sheet_names:
            sheet_df = pd.read_excel(xls, sheet_name, header=None, skiprows=1)
            headers = sheet_df.iloc[0].tolist()
            units = sheet_df.iloc[1].tolist()

            headers = [header.replace(" ","") if " " in header else header for header in headers] #remove spaces from headers for consistent format
            headers_w_units = [f"{header}_ETABS[{unit}]" if not pd.isna(unit) else f"{header}_ETABS" for header, unit in zip(headers, units)]

            sheet_df.columns = headers_w_units
            sheet_df = sheet_df.iloc[2:]  # Skip the first two rows (headers and units)
            self.data_frames[sheet_name.replace(" ","_")] = sheet_df.reset_index(drop=True)

        #convert types to float
        if "Joint_Reactions" in self.data_frames.keys():
            cols_to_float = ["FX_ETABS[kip]", "FY_ETABS[kip]", "FZ_ETABS[kip]", "MX_ETABS[kip-ft]", "MY_ETABS[kip-ft]", "MZ_ETABS[kip-ft]"]
            self.data_frames["Joint_Reactions"][cols_to_float] = self.data_frames["Joint_Reactions"][cols_to_float].astype("float")
            #self.data_frames["Joint_Reactions"].rename({"Unique Name_ETABS": "UniqueName_ETABS"}, axis =1, inplace=True) #rename joint reactions so it is same format as joint coordinates for possible future merge
        
        if "Point_Object_Connectivity" in self.data_frames.keys():
            cols_to_float = ["X_ETABS[ft]", "Y_ETABS[ft]", "Z_ETABS[ft]"]
            self.data_frames["Point_Object_Connectivity"][cols_to_float] = self.data_frames["Point_Object_Connectivity"][cols_to_float].astype("float")
    

    def calibrate_ETABS_to_RAM(self,ETABS_coord: list, RAM_coord:list):
        """
        this function takes the same point in ETABs coordinates and in RAM coordinates and creates 
        delta values to adjust coordinates of ETABs loads for proper location into RAM concept

        Assumes coordinates are given in form [x_cord, y_cord, z_cord]
        """
        assert len(ETABS_coord)== len(RAM_coord), "Input 'ETABS_coord' and 'RAM_coord' lists are different lengths"
        assert "Point_Object_Connectivity" in self.data_frames ,"Key 'Point_Object_Connectivity' not found in data_frames"

        location_delta = [RAM_coord[i]-ETABS_coord[i] for i in range(len(ETABS_coord))]
        self.data_frames["Point_Object_Connectivity"]
        self.data_frames["Point_Object_Connectivity"]["X_RAM[ft]"] = self.data_frames["Point_Object_Connectivity"]["X_ETABS[ft]"]+location_delta[0]
        self.data_frames["Point_Object_Connectivity"]["Y_RAM[ft]"] = self.data_frames["Point_Object_Connectivity"]["Y_ETABS[ft]"]+location_delta[1]
        self.data_frames["Point_Object_Connectivity"]["Z_RAM[ft]"] = self.data_frames["Point_Object_Connectivity"]["Z_ETABS[ft]"]+location_delta[2]

    def create_load_df(self):
        cols_to_include = ["FX_ETABS[kip]",
                           "FY_ETABS[kip]",
                           "FZ_ETABS[kip]",
                           "MX_ETABS[kip-ft]",
                           "MY_ETABS[kip-ft]",
                           "MZ_ETABS[kip-ft]",
                           "OutputCase_ETABS",
                           "X_ETABS[ft]",
                           "Y_ETABS[ft]",
                           "Z_ETABS[ft]",
                           "X_RAM[ft]",
                           "Y_RAM[ft]",
                           "Z_RAM[ft]"
                           ]
        load_df = pd.merge(self.data_frames["Point_Object_Connectivity"], self.data_frames["Joint_Reactions"], on="UniqueName_ETABS")
        return load_df[cols_to_include]

    



        