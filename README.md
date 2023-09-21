# Network Cost Calculator

The Network Cost Calculator is a tool that calculates construction costs for building a network infrastructure based on rate cards and infrastructure data. This tool is designed to help estimate the costs associated with constructing a network given a set of predefined rate cards and an infrastructure graph.

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Library Usage](#library-usage)
  - [Command-Line Interface (CLI)](#command-line-interface-cli)
  - [Code Snippet](#code-snippet)
- [Project Structure](#project-structure)
- [Testing](#testing)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- NetworkX library (`pip install networkx`)

### Installation

1. Clone this repository to local machine:

   ```bash
   git clone https://github.com/gustavo-varollo/gigaclear-code-challenge.git

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
   
## Usage
### Library Usage
To use the Network Cost Calculator as a library, follow these steps:

1. Import the NetworkCostCalculator class from the network_cost_calculator.network_cost_calculator module:

    ```python
    from network_cost_calculator.network_cost_calculator import NetworkCostCalculator
    
2. Create an instance of NetworkCostCalculator with rate cards data and a network graph:

    ```python
    # Example rate cards data (see rate_cards.json)
    rate_cards_data = [
        {
            "name": "Rate Card A",
            "Cabinet": 1000,
            "Trench/m (verge)": 50,
        },
        # Add more rate cards as needed
    ]
    
    # Example network graph (see problem.graphml)
    graph = nx.read_graphml("network_cost_calculator/graphml_files/problem.graphml", node_type=str)
    
    # Create a calculator instance
    calculator = NetworkCostCalculator("path/to/json/rate_cards.json",
                                   "path/to/graphml/graph.graphml")

3. Use the calculator instance to calculate costs for different rate cards:

    ```python
    # Calculate costs for a specific rate card
    results = asyncio.run(calculator.calculate_total_cost("rate_card_snake_case"))
    
    # Print the results
    print(results)

### Command-Line Interface (CLI)
The Network Cost Calculator also provides a CLI for processing graphs and calculating costs. To use it, run the following command:

```bash
python -m network_cost_calculator.network_cost_calculator <graphml_file_path> <rate_cards_json_file_path>
```

### Code Snippet

The following code snippet demonstrates how to use the Network Cost Calculator library to calculate network infrastructure costs based on rate cards and a network graph.

```python
# Example network cost calculator.
import asyncio

from network_cost_calculator.network_cost_calculator import NetworkCostCalculator

# Create a NetworkCostCalculator instance with rate cards and a network graph.
calculator = NetworkCostCalculator("network_cost_calculator/json_files/rate_cards.json",
                                   "network_cost_calculator/graphml_files/problem.graphml")

# Calculate costs for all rate cards in parallel using the `process_graph` method.
results = asyncio.run(calculator.process_graph())
print(results)

# Calculate costs for a specific rate card individually using the `calculate_total_cost` method.
# Replace "rate_card_a" with the desired rate card name.
results_individual_card = asyncio.run(calculator.calculate_total_cost("rate_card_a"))
print(results_individual_card)
```

## Project Structure
The project is organized as follows:

- `network_cost_calculator/`: The main Python package containing the network cost calculator.
- `graphml_files/`: Directory for storing GraphML files representing network infrastructure.
- `json_files/`: Directory for storing rate cards in JSON format.
- `network_cost_calculator.py`: The core module containing the NetworkCostCalculator class.
- `tests/`: Directory containing unit tests for the NetworkCostCalculator class.
- `requirements.txt`: List of Python dependencies required for the project.
- `README.md`: This file providing project information.
## Testing
Unit tests are included to verify the correctness of the calculator's functionalities. To run the tests, use the following command:
```bash
python -m unittest network_cost_calculator.tests.test_network_cost_calculator
```