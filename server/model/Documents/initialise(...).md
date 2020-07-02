
# Function Call
```cpp
void initialise(int myUniqueLandscapeID, double& area_max, std::vector<double>& cropAreas, std::vector<double>& livestockAreas, int& errorFlag);
```

# Purpose
Run once at the start to initialise model define the landscape of interest. The function returns for the given `myUniqueLandscapeID`: 
* the maximum area that can be cropped; 
* the baseline crop areas;
* the baseline livestock areas for the area. 

The baselines give the current business of usual (BAU) state. 
This BAU state can be used in [run(...)](/TGRAINS/TGRAINS-Interface/run(...).md) to get benchmark statistics with which to compare scenarios. 

# Argument Summary
Variable name | Intent | Purpose
-|- |-
myUniqueLandscapeID | input | Define which landscape we are using<br>101 = East Anglia<br>102 = South Wales
area_max | output | The largest area that can be cropped. When running scenarios, do not exceed this area.
cropAreas | output | The crop areas for the BAU state.
livestockAreas | output | The livestock areas for the BAU state.
errorFlag | input & output | If non zero on output then an error has occurred.

