#pragma once
#include <vector>
#include <string>

void initialiseTGRAINS_RLM(int myUniqueLandscapeID, double& maxCropArea, std::vector<double>& cropAreas, std::vector<int>& livestockNumbers, int& errorFlag);

void runTGRAINS_RLM(
	std::vector<double> cropAreas, std::vector<int> livestockNumbers,
	double& greenhouseGasEmissions, double& nLeach, std::vector<double>& pesticideImpacts,
	double& profit, double& production,
	std::vector<double>& nutritionaldelivery, std::vector<double>& healthRiskFactors,
	int& errorFlag
);

std::vector<int> getLandscapeIDs();
std::string getLandscapeString(int index);
std::string getCropString(int index);
std::string getLiveStockString(int index);

