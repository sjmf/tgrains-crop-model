#pragma once
#include <string>
#include <vector>

void initialise(
	int myUniqueLandscapeID, double& maxCropArea, std::vector<double>& cropAreas, std::vector<double>& livestockAreas, int& errorFlag
);

void run(
	std::vector<double> cropAreas, std::vector<double> livestockAreas,
	double& greenhouseGasEmissions, double& nLeach, std::vector<double>& pesticideImpacts,
	double& profit, double& production,
	std::vector<double>& nutritionaldelivery, std::vector<double>& healthRiskFactors,
	int& errorFlag
);

std::vector<int> getLandscapeIDs();
std::string getLandscapeString(int id);
std::string getCropString(int index);
std::string getLiveStockString(int index);
std::string getFoodGroupString(int index);