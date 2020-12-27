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

## Workflow

1. Create a model in Graphwalker studio
2. Save it as a json file such as: LoginSignUpForm.json
3. Load this json and convert it to a networkx graph
    - Generate test cases and measure time
4. Apply community detection and create multiple graphs
    - Generate test cases and measure time

## References

1. [Networkx](https://github.com/networkx/networkx)
2. [Community Detection for Networkx](https://python-louvain.readthedocs.io/en/latest/index.html)
3. [Graphwalker](https://github.com/GraphWalker/graphwalker-project/wiki)
