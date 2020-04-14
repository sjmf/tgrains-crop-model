#!/usr/bin/env python
# coding: utf-8
# C++ Crop Model Interface

import cppyy
from cppyy import ll

MODEL_HEADER_H = 'model/Landscape2019_LinuxSO.h'
MODEL_LIBRARY_SO = './model/libLandscape2019_LinuxSO.so'

cppyy.include(MODEL_HEADER_H)
cppyy.load_library(MODEL_LIBRARY_SO)
# Need to call this with cppyy.ll cppyy.ll.signals_as_exception
cppyy.ll.set_signals_as_exception(True)

# TO REMOVE WHEN LIBRARY UPDATED:
# Define a shim in C++. Dynamically compiled at runtime by cppyy using the cling interpreter:
cppyy.cppdef("""
    #include "model/Landscape2019_LinuxSO.h"

    typedef struct cropData
    {
        int myUniqueLandscapeID;
        double maxCropArea;
        std::vector<double> cropAreas;
        std::vector<int> livestockNumbers;

        double greenhouseGasEmissions;
        double nLeach;
        double profit;
        double production;

        std::vector<double> pesticideImpacts;
        std::vector<double> nutritionaldelivery;
        std::vector<double> healthRiskFactors;
        int errorFlag;
    } cropData;

    cropData initialiseTGRAINS_RLM_2(int myUniqueLandscapeID) 
    {
        cropData d = {
            myUniqueLandscapeID, 
            0.0,
            std::vector<double>(),
            std::vector<int>(),

            0.0,
            0.0,
            0.0,
            0.0,

            std::vector<double>(),
            std::vector<double>(),
            std::vector<double>(),
            0
        };

        initialiseTGRAINS_RLM(
            d.myUniqueLandscapeID,
            d.maxCropArea,
            d.cropAreas,
            d.livestockNumbers,
            d.errorFlag
        );

        return d;
    };

    void runTGRAINS_RLM_2(cropData& myCropData) 
    {
        runTGRAINS_RLM(
            myCropData.cropAreas,
            myCropData.livestockNumbers,
            myCropData.greenhouseGasEmissions, 
            myCropData.nLeach,
            myCropData.pesticideImpacts,
            myCropData.profit,
            myCropData.production,
            myCropData.nutritionaldelivery,
            myCropData.healthRiskFactors,
            myCropData.errorFlag
        );
    };
""")


# For Exception Handling:
class CropModelException(Exception):
    """Base class for exceptions in this module."""
    pass

class CropModelInitException(Exception):
    """Subclass for initialisation exceptions in this module."""
    pass


##
# Wrapper around C++ library functions
class CropModel:

    # Initialise all variables to sensible defaults
    def __init__(self):

        # Globals
        self.cropData = None

        self.cropAreasBAU = None
        self.livestockNumbersBAU = None

        self.landscapeIDs = list(cppyy.gbl.getLandscapeIDs())
        self.landscape = self.landscapeIDs[0]

        self.initialised = False


    ##
    # Pretty print internal state
    def __str__(self):
        return str("\n".join(["{0}:\n\t{1}".format(k,v) for k,v in self.toDict().items()]))


    def toDict(self):
        c = {k: v for k, v in vars(cppyy.gbl.cropData).items() if not k.startswith('_')}
        c = {x: getattr(self.cropData, x) for x in c.keys()}
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
        self.cropData = cppyy.gbl.initialiseTGRAINS_RLM_2(self.landscape)
        self.landscapeIDs = list(cppyy.gbl.getLandscapeIDs())

        if self.cropData.errorFlag != 0:
            raise CropModelException("Model initialisation failed")

        self.cropAreasBAU = self.cropData.cropAreas
        self.livestockNumbersBAU = self.cropData.livestockNumbers

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
        cppyy.gbl.runTGRAINS_RLM_2(self.cropData)

        if self.cropData.errorFlag != 0:
            raise CropModelException("Model run failed")

        return self.cropData

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
    # Set Crop Areas
    def set_crop_areas(self, cropAreas):

        if type(cropAreas) is not list:
            raise CropModelException("Crop Areas must be a list of floating-point numbers!")
        if len(cropAreas) != len(self.cropData.cropAreas):
            raise CropModelException("Crop Areas must be {0} items in length!".format(len(self.cropData.cropAreas)))
        for c in cropAreas:
            if type(c) is not float:
                raise CropModelException("Crop Areas must be numeric!")

        self.cropData.cropAreas = cropAreas

    ##
    # Set Livestock Numbers
    def set_livestock_numbers(self, liveStockNumbers):
        raise CropModelException("Not implemented yet!")


def test():
    print("Running Crop Model Tests...")
    model = CropModel()

    print("Initialising Model...")
    model.initialise_model()

    print("Running Model...")
    model.run_model()

    print(model)

    print()

    print(model.get_landscape_string(model.landscapeIDs[0]))
    print(model.get_crop_string(1))
    print(model.get_livestock_string(1))

    print("Success!")
    return 0;

if __name__ == "__main__":
    test()
