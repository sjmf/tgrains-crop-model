# Function Call
```cpp
std::string getCropString(int index);
```

# Purpose
This function can be used to find the crop type associated with a given index. 

The concept is that you:
1. run initialise;
2. find out how many crops can be associated with a given region (`cropAreas.size()`);
3. use this function to find out what these crops are.

This could be used to populate the interface. 

The user then associates the area with each crop type -preserving that order. 

# Argument Summary
Variable name | Intent | Purpose
-|- |-
index | input | Possible values between `0` and `cropAreas.size()-1`.
