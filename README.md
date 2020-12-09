# Collections Assessment Data Warehouse
A program for performing collections assessment in academic libraries.

## Goals of this program

- Use SUSHI API to automatically harvest R5 COUNTER stats and save to a database
  - Get SUSHI credentials from CORAL/Alma ERM
- Store COUNTER R4, COUNTER R5, non-standard usage stats in a database
- Use relational database model to connect KBART, R4, R5 info
- Provide visualizations of statistics
- Has GUI

## Information on This Repository

### History
The development of this program did not begin in this repository; much of the project's previous content, including relevant aspects of the commit history, were moved to this repository as to create a repository suited for a Docker runtime environment and excluding all data from the developing institution.

### Runtime Environment
This repository is designed to be deployed a series of Docker containers. This repository will be pulled down into a Python Docker container and mingled with files containing private information located in the same directory as the Docker Compose file. More information about this runtime environment can be found in docs/Runtime_Environment/Runtime_Environment.md.