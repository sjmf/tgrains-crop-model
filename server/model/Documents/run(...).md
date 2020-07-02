# Function Call
```cpp
void run(
	std::vector<double> cropAreas, std::vector<double> livestockAreas,
	double& greenhouseGasEmissions, double& nLeach, std::vector<double>& pesticideImpacts,
	double& profit, double& production,
	std::vector<double>& nutritionalDelivery, std::vector<double>& healthRiskFactors,
	int& errorFlag
);
```

# Purpose
This function can be used to run scenarios on the various cropping strategies we might try. 

These are expressed as `cropAreas` and `livestockAreas`. 

You can use the current values for these inputs (from [initialise(...)](/TGRAINS/TGRAINS-Interface/initialise(...).md)) to get a benchmark.

# Argument Summary
Variable name | Intent | Purpose
-|-|-
cropAreas | input | A vector of crop areas in ha of each crop type. These are allocated in the order that can be deduced using GetCropString. 
livestockNumbers | input | A vector of livestock numbers of each animal type. These are allocated in the order that can be deduced using GetLivestockString.
greenhouseGasEmissions | output | Total emissions in CO2-equiv (average kg/ha/year)
nLeach | output | N leach average kg/ha/year
pesticideImpacts | output | Metrics of impacts from pesticides (large numbers are worse than small)<br>1. Ground water<br>2. Fish<br>3. Birds<br>4. Bees<br>5. Beneficial anthropods 
profit | output | Profit over variable costs (average £ ha-1)
production | output | Calories
nutritionalDelivery |  | Percentage of each in terms of cal. This should be compared with EatLancet (see [Eat-Lancet.md](/TGRAINS/TGRAINS-Interface/Eat-Lancet.md))<br>1. Whole grains<br>2. Tubers or starchy vegetables<br>3. Vegetables<br>4. Fruits<br>5. Dairy foods<br>6. Added fats<br>7. Added fats<br>8. Added sugars<br>9. Animal Protein<br>10. Vegetable Protein
healthRiskFactors | output | Risks of<br>1. Stroke<br>2. Cancer<br>3 Heart disease<br>4. Diabetes
errorFlag | input & output | If non zero on output then an error has occurred
