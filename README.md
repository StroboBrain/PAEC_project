# Repo for PAEC Project: Distributed Shopping List Replicart

A distributed shopping list system with formal TLA+ specification and a Python CLI implementation with probabilistic testing framework.

## Repository Structure

- **`src/`** - Python implementation and probabilistic testing
  - `main.py` - Main file to start the CLI
  - `storage*.py` - Storage API for persisent/in memory replication
  - `network_handler.py` - Simple networking module that sends UDP messages across processes.
  - `replica_sync.py` - Contains the replica merging logic.
  - `[item|request]_handler.py` - Contains the logic for item/request actions.
  - `user_handler.py` - Manages local useres of the CLI.
  
- **`data/`** - Replica storage directory for JSON files
- **`TLA/`** - TLA+ specification and model definitions

## Probabilistic Testing

To run the probabilistic tester, navigate to the `src/` directory and execute:
```bash
python3 probabililstic_testing.py --steps [STEPS] --runs [RUNS]
```
The optional parameter ```--steps``` defines the amount of randomly chosen actions that are exectued before the exploration stops.
The optional parameter ```--runs``` defines the amount of runs (individual exectuions of ```[STEPS]``` amount of random actions).

## Command Line Interface

To run the CLI, navigate to the ```src/```directory and execute:
```bash
python3 main.py
```
The CLI will first promt you to either create a new local user account, or to log into an existing one. The login is not secure and only serves to seperate different users replicas.

After the login, you can type ```help``` to see all available commands and start using the shopping list.
