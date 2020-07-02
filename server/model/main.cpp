
#include "TGRAINS.h"
#include <iostream>
#include <chrono>

void init(std::vector<double>& cropAreas, std::vector<double>& livestockAreas, int& ErrorFlag){

	using 
		std::cout,
		std::endl
	;

	int myUniqueLandscapeID = 101;
	double maxCropArea = 0.0;

	cout << "\n\n-------------------------------PreInit" << endl;
	cout << "myUniqueLandscapeID = " << myUniqueLandscapeID << endl;
	cout << "MaxCropArea = " << maxCropArea << endl;
	cout << "NumCropsTypeAvailable = " << cropAreas.size() << endl;
	cout << "NumLivestockTypeAv = " << livestockAreas.size() << endl;
	cout << "CropAreas = {"; for(double d : cropAreas){ cout << d << ", "; } cout << "}" << endl;
	cout << "LivestockNumbers = {"; for(int i : livestockAreas){ cout << i << ", "; } cout << "}" << endl;
	cout << "ErrorFlag = " << ErrorFlag << endl;

	cout << "\nmain.cpp: INITIALISING...\n" << endl;
	initialise(myUniqueLandscapeID, maxCropArea, cropAreas, livestockAreas, ErrorFlag);
	cout << "\nmain.cpp: ...FINISHED\n" << endl;

	cout << "\n\n-------------------------------String Functions" << endl;
	std::vector<int> landscapeIDs = getLandscapeIDs();

	cout << "landscapeIDs = {"; for(size_t i : landscapeIDs){ cout << i << ", "; } cout << "}" << endl;
	cout << "landscapeStrings.length = {"; for(size_t i : landscapeIDs){ cout << getLandscapeString(i).length() << ", "; } cout << "}" << endl;
	cout << "landscapeStrings = {"; for(size_t i : landscapeIDs){ cout << getLandscapeString(i) << ", "; } cout << "}" << endl;

	cout << "cropStrings = {"; for(size_t i = 0; i < cropAreas.size(); i++){ cout << getCropString(i) << ", "; } cout << "}" << endl;
	cout << "animalStrings = {"; for(size_t i = 0; i < livestockAreas.size(); i++){ cout << getLiveStockString(i) << ", "; } cout << "}" << endl;

	cout << "\n\n-------------------------------PostInit" << endl;

	cout << "myUniqueLandscapeID = " << myUniqueLandscapeID << endl;
	cout << "MaxCropArea = " << maxCropArea << endl;
	cout << "NumCropsTypeAvailable = " << cropAreas.size() << endl;
	cout << "NumLivestockTypeAv = " << livestockAreas.size() << endl;
	cout << "CropAreas = {"; for(double d : cropAreas){ cout << d << ", "; } cout << "}" << endl;
	cout << "LivestockNumbers = {"; for(int i : livestockAreas){ cout << i << ", "; } cout << "}" << endl;
	cout << "ErrorFlag = " << ErrorFlag << endl;
}

void run(std::vector<double>& cropAreas, std::vector<double>& livestockAreas, int& ErrorFlag){

	using 
		std::cout,
		std::endl
	;

	double
		greenhouseGasEmissions,
		nLeach,
		profit,
		production
	;
	std::vector<double>
		pesticideImpacts(5,0),
		nutritionaldelivery,
		healthRiskFactors
	;

	cout << "\n\n-------------------------------PreRun" << endl;
	cout << "GreenhouseGasEmissions = " << greenhouseGasEmissions << endl;
	cout << "NLeach = " << nLeach << endl;
	cout << "pesticideImpacts = {"; for(double d : pesticideImpacts){ cout << d << ", "; } cout << "}" << endl;
	cout << "Profit = " << profit << endl;
	cout << "Production = " << production << endl;
	cout << "nutritionaldelivery = {"; for(double d : nutritionaldelivery){ cout << d << ", "; } cout << "}" << endl;
	cout << "healthRiskFactors = {"; for(double d : healthRiskFactors){ cout << d << ", "; } cout << "}" << endl;

	//----------------------------------------------------------------------------------------------------
	int totalCropArea = 0;
	for(double d : cropAreas){
		totalCropArea += d;
	}

	for(double d : livestockAreas){
		totalCropArea += d;
	}

	int numCrops = cropAreas.size();
	int numLivestock = livestockAreas.size();

	cout << "numCrops = " << numCrops << endl;
	cout << "numLivestock = " << numLivestock << endl;

	std::vector<double> 
		cropProps = { 0.1, 0.05, 0.1, 0.075, 0.125, 0.07, 0.06, 0.05, 0.05, 0.025, 0.05 },
		livestockProps = {0.05, 0.025, 0.075, 0.025, 0.03, 0.04}
	;

	double sumProps = 0;
	for(double d : cropProps) sumProps += d;
	for(double d : livestockProps) sumProps += d;
	cout << "sumProps = " << sumProps << endl;

	for(size_t i = 0; i < cropAreas.size(); i++){
		cropAreas.at(i) = totalCropArea * cropProps.at(i);
	}

	for(size_t i = 0; i < livestockAreas.size(); i++){
		livestockAreas.at(i) = totalCropArea * livestockProps.at(i);
	}

	cout << "New cropAreas = {"; for(double d : cropAreas){ cout << d << ", "; } cout << "}" << endl;
	cout << "New livestockAreas = {"; for(double d : livestockAreas){ cout << d << ", "; } cout << "}" << endl;

	cout << "\nmain.cpp: RUNNING...\n" << endl;
	run(cropAreas, livestockAreas, greenhouseGasEmissions, nLeach, pesticideImpacts, profit, production, nutritionaldelivery, healthRiskFactors, ErrorFlag);
	cout << "\nmain.cpp: ...FINISHED\n" << endl;

	cout << "\n\n-------------------------------PostRun" << endl;
	cout << "GreenhouseGasEmissions[kg-CO2/yr] = " << greenhouseGasEmissions << endl;
	cout << "NLeach[kg-N/yr] = " << nLeach << endl;
	cout << "pesticideImpacts[EIQ/yr] = {"; for(double d : pesticideImpacts){ cout << d << ", "; } cout << "}" << endl;
	cout << "Profit[gbp/yr] = " << profit << endl;
	cout << "Production[million kcal/y] = " << production << endl;

	cout << "foodGroupStrings = {"; for(size_t i = 0; i < nutritionaldelivery.size(); i++){ cout << getFoodGroupString(i) << ", "; } cout << "}" << endl;
	cout << "nutritionaldelivery = {"; for(double d : nutritionaldelivery){ cout << d << ", "; } cout << "}" << endl;
	cout << "healthRiskFactors = {"; for(double d : healthRiskFactors){ cout << d << ", "; } cout << "}" << endl;
}

int main(){

	std::cout << "Pre init - starting count" << std::endl;
	std::chrono::steady_clock::time_point startClock = std::chrono::steady_clock::now();

	using std::cout;
	using std::endl;

	std::vector<double> cropAreas;
	std::vector<double> livestockAreas;
	int ErrorFlag = 0;

	init(cropAreas, livestockAreas, ErrorFlag);
	run(cropAreas, livestockAreas, ErrorFlag);

	std::chrono::steady_clock::time_point endClock = std::chrono::steady_clock::now();
	std::cout << "Run time = " << std::chrono::duration_cast<std::chrono::seconds>(endClock - startClock).count() << "[s]" << std::endl;

	return 0;
}
