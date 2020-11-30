#!/usr/bin/env python
# coding: utf-8
# C++ Crop Model Interface

import cppyy
from cppyy import ll

# Cope with running under relative path as module
import os.path
my_path = os.path.abspath(os.path.dirname(__file__))

MODEL_HEADER_H = os.path.join(my_path, 'TGRAINS.h')
MODEL_LIBRARY_SO = os.path.join(my_path, 'libTGRAINS.so')

cppyy.include(MODEL_HEADER_H)
cppyy.load_library(MODEL_LIBRARY_SO)
# Need to call this with cppyy.ll cppyy.ll.signals_as_exception
cppyy.ll.set_signals_as_exception(True)

# Define a convenience shim in C++.
# Dynamically compiled at runtime by cppyy using the cling interpreter:
SHIM_FUNCTION = """
    #include "{header}"

    typedef struct tgrainsData
    {{
        int myUniqueLandscapeID;
        double maxCropArea;
        double maxUplandArea;
        std::vector<double> cropAreas;
        std::vector<double> livestockAreas;

        double greenhouseGasEmissions;
        double nLeach;
        double profit;
        double production;

        std::vector<double> pesticideImpacts;
        std::vector<double> nutritionaldelivery;
        std::vector<double> healthRiskFactors;
        int errorFlag;
    }} tgrainsData;

    tgrainsData initialiseTGRAINS_RLM_2(int myUniqueLandscapeID) 
    {{
        tgrainsData d = {{
            myUniqueLandscapeID, 
            0.0,
            0.0,
            std::vector<double>(),
            std::vector<double>(),

            0.0,
            0.0,
            0.0,
            0.0,

            std::vector<double>(5,0),
            std::vector<double>(),
            std::vector<double>(),
            0
        }};

        initialise(
            d.myUniqueLandscapeID,
            d.maxCropArea,
            d.maxUplandArea,
            d.cropAreas,
            d.livestockAreas,
            d.errorFlag
        );

        return d;
    }};

    void runTGRAINS_RLM_2(tgrainsData& myData) 
    {{
        run(
            myData.cropAreas,
            myData.livestockAreas,
            myData.greenhouseGasEmissions, 
            myData.nLeach,
            myData.pesticideImpacts,
            myData.profit,
            myData.production,
            myData.nutritionaldelivery,
            myData.healthRiskFactors,
            myData.errorFlag
        );
    }};
"""
SHIM_FUNCTION = SHIM_FUNCTION.format(header=os.path.join(my_path,"TGRAINS.h"))

cppyy.cppdef(SHIM_FUNCTION)

# For Exception Handling:
class CropModelException(Exception):
    """Base class for exceptions in this module."""
    pass

class CropModelInitException(CropModelException):
    """Subclass for initialisation exceptions in this module."""
    pass


##
# Wrapper around C++ library functions
class CropModel:

    # Initialise all variables to sensible defaults
    def __init__(self):

        # Globals
        self.data = None

        self.cropAreas = None
        self.livestockAreas = None

        self.landscapeIDs = list(cppyy.gbl.getLandscapeIDs())
        self.landscape = self.landscapeIDs[0]

        self.initialised = False


    ##
    # Pretty print internal state
    def __str__(self):
        return str("\n".join(["{0}:\n\t{1}".format(k,v) for k,v in self.to_dict().items()]))


    def to_dict(self):
        c = {k: v for k, v in vars(cppyy.gbl.tgrainsData).items() if not k.startswith('_')}
        c = {x: getattr(self.data, x) for x in c.keys()}
        for k in c.keys():
            if type(c[k]) == cppyy.gbl.std.vector['double'] or \
                    type(c[k]) == cppyy.gbl.std.vector['int']:
                c[k] = list(c[k])
        return c


    ##  Initialise TGRAINS Model
    #
    # Call C++ Function with the following definition:
    #
    # cropData initialiseTGRAINS_RLM_2(int myUniqueLandscapeID)
    def initialise_model(self):

        # Initialise Model
        self.data = cppyy.gbl.initialiseTGRAINS_RLM_2(self.landscape)
        self.landscapeIDs = list(cppyy.gbl.getLandscapeIDs())

        if self.data.errorFlag != 0:
            raise CropModelException("Model initialisation failed")

        self.cropAreas = self.data.cropAreas
        self.livestockAreas = self.data.livestockAreas

        self.initialised = True


    ## Run TGRAINS Model
    #
    # Call C++ Function with the following definition:
    #
    # void RunTGRAINS_RLM(cropData& myCropData)
    def run_model(self):

        if not self.initialised:
            raise CropModelInitException("Model not initialised")

        # Run model
        cppyy.gbl.runTGRAINS_RLM_2(self.data)

        if self.data.errorFlag != 0:
            raise CropModelException("Model run failed")

        return self.data

    ##
    # Get built-in landscape string identifiers
    def get_landscape_string(self, index):

        if not self.initialised:
            raise CropModelInitException("Model not initialised")

        return cppyy.gbl.getLandscapeString(index)

    ##
    # Get built-in crop string identifiers
    def get_crop_string(self, index):

        if not self.initialised:
            raise CropModelInitException("Model not initialised")

        return cppyy.gbl.getCropString(index)

    ##
    # Get built-in livestock identifiers
    def get_livestock_string(self, index):

        if not self.initialised:
            raise CropModelInitException("Model not initialised")

        return cppyy.gbl.getLiveStockString(index)

    ##
    # Get built-in food group identifiers
    def get_food_group_string(self, index):

        if not self.initialised:
            raise CropModelInitException("Model not initialised")

        return cppyy.gbl.getFoodGroupString(index)

    ##
    # Set the landscape ID to operate on
    def set_landscape_id(self, landscape_id):

        if landscape_id not in self.landscapeIDs:
            raise CropModelException("{} is not a valid Landscape ID".format(landscape_id))

        self.landscape = landscape_id
        self.initialised = False

    ##
    # Set Crop Areas
    def set_crop_areas(self, crop_areas):

        if type(crop_areas) is not list:
            raise CropModelException("Crop Areas must be a list of floating-point numbers!")
        if len(crop_areas) != len(self.data.cropAreas):
            raise CropModelException("Crop Areas must be {0} items in length!".format(len(self.data.cropAreas)))
        for c in crop_areas:
            if type(c) is not float:
                raise CropModelException("Crop Areas must be numeric!")

        self.data.cropAreas = crop_areas

    ##
    # Set Livestock Areas
    def set_livestock_areas(self, livestock_areas):

        if type(livestock_areas) is not list:
            raise CropModelException("Livestock Areas must be a list of floating-point numbers!")
        if len(livestock_areas) != len(self.data.livestockAreas):
            raise CropModelException("Livestock Areas must be {0} items in length!".format(len(self.data.livestockAreas)))
        for c in livestock_areas:
            if type(c) is not float:
                raise CropModelException("Livestock Areas must be numeric!")

        self.data.livestockAreas = livestock_areas



def test():
    print("Running Crop Model Tests...")
    model = CropModel()

    print("Initialising Model...")
    model.initialise_model()
    print(model)

    print("Running Model...")
    model.run_model()
    print(model)

    # Mutate the state a bit
    from cppyy.gbl.std import vector
    total_crop_area = 0
    for d in model.cropAreas:
        total_crop_area = total_crop_area + d

    crop_props = vector['double']((0.1, 0.05, 0.1, 0.075, 0.125, 0.07, 0.06, 0.05, 0.05, 0.025, 0.05))
    for i in range(model.cropAreas.size()):
        model.cropAreas[i] = total_crop_area * crop_props[i]

    print("Running Model after mutations...")
    model.run_model()
    print(model)

    print("\n=== STRINGS ===")

    print(model.get_landscape_string(model.landscapeIDs[0]))

    print([model.get_crop_string(i) for i in range(model.cropAreas.size())])
    print([model.get_food_group_string(i) for i in range(model.data.nutritionaldelivery.size())])
    print([model.get_livestock_string(i) for i in range(model.data.livestockAreas.size())])

    print("Success!")
    return 0


if __name__ == "__main__":
    test()
