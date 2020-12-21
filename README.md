# Model Based Testing

These are current capabilities of the project:

- Show networkx graph in a visual view
- Apply community detection
    - Show communities
- Load graphwalker json model and convert it to a networkx graph
- Generate test cases from graphwalker json model

## Requirements

- Python 3 or higher
- Virtual environment
    1. Create it with: `py -3 -m venv env`
    2. Activate it with: `env\scripts\activate`
    3. Install pip packages when the virtual environment is activated

### Required Pip Packages

- networkx => For graph operations
    - numpy==1.19.3 => There is a bug in the latest numpy version (1.19.4)
- python-louvain => For community detection
- matplotlib

#### Follow this steps to install the required packages

1. pip install networkx
2. pip install python-louvain
3. pip install matplotlib
4. pip install numpy==1.19.3

### Graphwalker

- Graphwalker cli is required to generate test cases. You can install graphwalker cli from the [following page](https://graphwalker.github.io/).
- The cli jar must be available in the root of the project. In the future, path option will be available.
- Java 8 or higher must be available in your system.
