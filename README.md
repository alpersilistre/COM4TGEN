# Model Based Testing

## Requirements

- Python 3 or higher
- Virtual environment
    1. Create it with: `py -3 -m venv env`
    2. Activate it with: `env\scripts\activate`
    3. Install pip modules when the virtual environment is activated

### Required Pip Modules

- networkx => For graph operations
    - numpy==1.19.3 => There is a bug in the latest numpy version (1.19.4)
- python-louvain => For community detection
- matplotlib
