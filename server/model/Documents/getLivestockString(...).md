# Function Call
```cpp
std::string getLiveStockString(int index);
```

# Purpose
This function can be used to find the animal type associated with a given index. 

The concept is that you:
1. run initialise; 
2. find out how many animal types can be associated with a given region (`livestockAreas.size()`);
3. use this function to find out what they are.

This could be used to populate the interface. 

The user then associates the number of animals with each type, preserving that order. 

# Argument Summary
Variable name | Intent | Purpose
-|- |-
index|input|Possible values between `0` and `livestockAreas.size()-1`.



