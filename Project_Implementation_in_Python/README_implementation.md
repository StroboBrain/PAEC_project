# Implementation in Python
This folder contains the implementation of the TLA+ specification in Python.

## Network
We use a simple network simulation to model the communication between the users.

## Shopping List
We use a simple shopping list class to model the shopping list of each user.

## main_hardcode.py
Runs the code with preset data

## unique identifiers
We use the uuid libary for uniquie identifiers. while a conflict is in theory possible, the real possiblility is neglicable.

## Testing
### Simple Unit testing
Some test in the tests folder are simple unit tests to test the functionality of the classes and methods.

### Proablilistic Testing
#### Action Counter
The action counter is impleneted outside of the methodes to reduce entanglement.