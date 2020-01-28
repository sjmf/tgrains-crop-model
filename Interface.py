#!/usr/bin/env python
# coding: utf-8

import cppyy
import ctypes
from array import array
from ctypes import c_double
from ctypes import c_int

cppyy.include('model/Landscape2019_LinuxSO.h')
cppyy.load_library('model/libLandscape2019_LinuxSO.so')

#void InitialiseTGRAINS_RLM(
#    int     myUniqueLandscapeID, 
#    double& MaxCropArea, 
#    int     NumCropsTypeAvailable, 
#    int     NumLivestockTypeAv, 
#    double  CropAreas[],
#    int     LivestockNumbersBL[], 
#    int&    ErrorFlag);

myUniqueLandscapeID =   101
MaxCropArea =           c_double(60000.0)
NumCropsTypeAvailable = 10
NumLivestockTypeAv =    2
CropAreas =             array('d', [i+.0 for i in range(cppyy.gbl.MaxNumCrops)])
LivestockNumbersBL =    array('i', [i for i in range(cppyy.gbl.MaxNumAnimals)])
ErrorFlag =             c_int(0)

# Sense-check input (to prevent segmentation faults in the C++ library)
assert len(LivestockNumbersBL) == cppyy.gbl.MaxNumAnimals, \
    "Array length for LivestockNumbersBL! {0} != {1}"\
    .format(len(LivestockNumbersBL), cppyy.gbl.MaxNumAnimals)

assert len(CropAreas) == cppyy.gbl.MaxNumCrops, \
    "Array length for CropAreas! {0} != {1}"\
    .format(len(CropAreas), cppyy.gbl.MaxNumCrops)

# Initialise Model
cppyy.gbl.InitialiseTGRAINS_RLM(
    myUniqueLandscapeID,
    MaxCropArea,
    NumCropsTypeAvailable,
    NumLivestockTypeAv,
    CropAreas,
    LivestockNumbersBL,
    ErrorFlag
)

#void RunTGRAINS_RLM(
#    double CropAreas[MaxNumCrops], 
#    int LivestockNumbers[MaxNumAnimals], 
#    double& GreenhouseGasEmissions, 
#    double& NLeach,
#    double PesticideImpacts[5], 
#    double& Profit, 
#    double& Production, 
#    double Nutritionaldelivery[10],
#    double HealthRiskFactors[4],
#    int& ErrorFlag)

# NB: the below expression `[i for i in range(x)]` 
# generates our test data with the correct array lengths

CropAreas =              array('d', [i+.0 for i in range(cppyy.gbl.MaxNumCrops)]) 
LivestockNumbers =       array('i', [i for i in range(cppyy.gbl.MaxNumAnimals)])
GreenhouseGasEmissions = c_double(0)
NLeach =                 c_double(0)
PesticideImpacts =       array('d', [i+.0 for i in range(5)])
Profit =                 c_double(0)
Production =             c_double(0)
Nutritionaldelivery =    array('d', [i+.0 for i in range(10)])
HealthRiskFactors =      array('d', [i+.0 for i in range(4)])
ErrorFlag =              c_int(0)


# Sense-check input (to prevent segmentation faults in the C++ library)
assert len(LivestockNumbers) == cppyy.gbl.MaxNumAnimals, \
    "Array length for LivestockNumbers! {0} != {1}"\
        .format(len(LivestockNumbers), cppyy.gbl.MaxNumAnimals)
assert len(CropAreas) == cppyy.gbl.MaxNumCrops, \
    "Array length for CropAreas! {0} != {1}"\
        .format(len(CropAreas), cppyy.gbl.MaxNumCrops)

cppyy.gbl.RunTGRAINS_RLM(
    CropAreas, 
    LivestockNumbers, 
    GreenhouseGasEmissions, 
    NLeach,
    PesticideImpacts, 
    Profit, 
    Production, 
    Nutritionaldelivery,
    HealthRiskFactors,
    ErrorFlag
)

print(PesticideImpacts)
print(Profit)
print(cppyy.gbl.GetCropString(9))

