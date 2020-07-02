# Function Call
```cpp
std::string getFoodGroupString(int index);
```

# Purpose
This function can be used to find the food group associated with a given index of nutritionalDelivery. 

The concept is that you:
1. run [run(...)](/TGRAINS/TGRAINS-Interface/run(...).md); 
2. find out how many food groups there are (`nutritionalDelivery.size()`);
3. use this function to find out what they are.

This could be used to populate the interface. 

# Argument Summary
Variable name | Intent | Purpose
-|- |-
index|input|Possible values between `0` and `nutritionalDelivery.size()-1`.


