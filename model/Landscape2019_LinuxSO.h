#pragma once

#include <string>

//#ifdef __cplusplus 
//extern "C" {
//#endif

//Add frontend functions here.

const int MaxNumCrops(15);
const int MaxNumAnimals(5);

//extern "C"{
extern "C" int add(int a, int b);
extern "C" int subtract(int a, int b);

extern "C" void InitialiseTGRAINS_RLM(
	int myUniqueLandscapeID, double& MaxCropArea, int NumCropsTypeAvailable, int NumLivestockTypeAv, double CropAreas[],
	int LivestockNumbersBL[], int& ErrorFlag
);

extern "C" void RunTGRAINS_RLM(
	double CropAreas[], int LivestockNumbers[], double& GreenhouseGasEmissions, double& NLeach,
	double PesticideImpacts[], double& Profit, double& Production, double Nutritionaldelivery[],
	double HealthRiskFactors[],
	int& ErrorFlag
);

extern "C" char* GetCropString(int index);
extern "C" char * GetLiveStockString(int index);
//}

//#ifdef __cplusplus
//}
//#endif
