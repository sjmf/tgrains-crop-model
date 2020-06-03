
#include "../Landscape2019_LinuxSO.h"
#include <iostream>
#include <iterator>
using namespace std;


int main(){

	using std::cout;
	using std::endl;

	int myUniqueLandscapeID = 102;

	double maxCropArea = 0;
	std::vector<double> cropAreas;
	std::vector<int> livestockNumbers;
	int ErrorFlag = 0;

#if (_GLIBCXX_USE_CXX11_ABI == 1)
    cout << "Using CXX11 ABI" << endl;
#endif
#if (_GLIBCXX_USE_CXX11_ABI == 0)
    cout << "Using old CXX ABI" << endl;
#endif


	cout << "\n\n-------------------------------PreInit" << endl;
	cout << "myUniqueLandscapeID = " << myUniqueLandscapeID << endl;
	cout << "MaxCropArea = " << maxCropArea << endl;
	cout << "NumCropsTypeAvailable = " << cropAreas.size() << endl;
	cout << "NumLivestockTypeAv = " << livestockNumbers.size() << endl;
	cout << "CropAreas = {"; for(double d:cropAreas){ cout << d << ", "; } cout << "}" << endl;
	cout << "LivestockNumbers = {"; for(int i : livestockNumbers){ cout << i << ", "; } cout << "}" << endl;
	cout << "ErrorFlag = " << ErrorFlag << endl;

	initialiseTGRAINS_RLM(myUniqueLandscapeID, maxCropArea, cropAreas, livestockNumbers, ErrorFlag);


	cout << "\n\n-------------------------------PostInit" << endl;
	cout << "myUniqueLandscapeID = " << myUniqueLandscapeID << endl;
	cout << "MaxCropArea = " << maxCropArea << endl;
	cout << "NumCropsTypeAvailable = " << cropAreas.size() << endl;
	cout << "NumLivestockTypeAv = " << livestockNumbers.size() << endl;
	cout << "CropAreas = {"; for(double d : cropAreas){ cout << d << ", "; } cout << "}" << endl;
	cout << "LivestockNumbers = {"; for(int i : livestockNumbers){ cout << i << ", "; } cout << "}" << endl;
	cout << "ErrorFlag = " << ErrorFlag << endl;

	double greenhouseGasEmissions = 0,
		nLeach = 0,
		profit = 0,
		production = 0
	;
	std::vector<double>
		pesticideImpacts,
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

	runTGRAINS_RLM(cropAreas, livestockNumbers, greenhouseGasEmissions, nLeach, pesticideImpacts, profit, production, nutritionaldelivery, healthRiskFactors, ErrorFlag);


	cout << "\n\n-------------------------------PostRun" << endl;
	cout << "GreenhouseGasEmissions = " << greenhouseGasEmissions << endl;
	cout << "NLeach = " << nLeach << endl;
	cout << "pesticideImpacts = {"; for(double d : pesticideImpacts){ cout << d << ", "; } cout << "}" << endl;
	cout << "Profit = " << profit << endl;
	cout << "Production = " << production << endl;
	cout << "nutritionaldelivery = {"; for(double d : nutritionaldelivery){ cout << d << ", "; } cout << "}" << endl;
	cout << "healthRiskFactors = {"; for(double d : healthRiskFactors){ cout << d << ", "; } cout << "}" << endl;


	cout << "\n\n-------------------------------String Functions" << endl;
	const std::vector<int> landscapeIDs = getLandscapeIDs();
	std::vector<std::string> landscapeStrings;
    std::vector<std::string> cropStrings;
    std::vector<std::string> livestockStrings;

	for(int i=0; i < landscapeIDs.size(); i++)
	    landscapeStrings.push_back(getLandscapeString(landscapeIDs[i]));
	for(int i=0; i < cropAreas.size(); i++)
	    cropStrings.push_back(getCropString(i));
	for(int i=0; i < livestockNumbers.size(); i++)
	    livestockStrings.push_back(getLiveStockString(i));

	cout << "landscapeIDs = {"; for(int i : landscapeIDs){ cout << i << ", "; } cout << "}" << endl;

    cout << "landscapeStrings.length = {"; for(int i=0; i < landscapeStrings.size(); i++){ cout << landscapeStrings[i].length() << ", "; } cout << "}" << endl;
    cout << "landscapeStrings = {"; for(int i=0; i < landscapeStrings.size(); i++){ cout << landscapeStrings[i] << ", "; } cout << "}" << endl;

    cout << "cropStrings = {"; for(int i = 0; i < cropAreas.size(); i++){ cout << cropStrings[i] << ", "; } cout << "}" << endl;
    cout << "animalStrings = {"; for(int i = 0; i < livestockNumbers.size(); i++){ cout << livestockStrings[i] << ", "; } cout << "}" << endl;

	return 0;
}
