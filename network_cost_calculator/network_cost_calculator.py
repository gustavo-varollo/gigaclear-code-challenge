"""
network_cost_calculator

This module contains the NetworkCostCalculator class, which is used to calculate network
infrastructure costs based on rate cards and a network graph. It also includes a FileManager class
for handling file operations.

Classes:
    - NetworkCostCalculator: A class for calculating network infrastructure costs.
    - FileManager: A class for handling file operations, including loading rate cards and the
      network graph.

Usage:
    To use the NetworkCostCalculator class, create an instance with rate cards and a network graph,
    and then call its methods to calculate costs for various rate cards and network routes.

Example:
    # Import the module
    from network_cost_calculator import NetworkCostCalculator

    # Create a NetworkCostCalculator instance
    calculator = NetworkCostCalculator(rate_cards, graph)

    # Calculate costs for a specific rate card
    result = calculator.calculate_total_cost(graph, "Rate Card A")

Note:
    Ensure that the rate cards are provided in a compatible format and that the graph represents the
    network infrastructure accurately for accurate cost calculations.
"""

import argparse
import json

import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Union, Tuple, List

import networkx as nx


class FileManager:
    """
    FileManager is a utility class for handling file operations in the NetworkCostCalculator.

    This class provides methods to load rate cards data from a JSON file and load a network graph
    from a GraphML file.

    Attributes:
        graphml_file_path (str): The file path to the GraphML file containing the network graph.
        json_file_path (str): The file path to the JSON file containing rate cards data.

    Methods:
        load_rate_cards: Load rate cards data from a JSON file.
        load_network_graph: Load a network graph from a GraphML file.

    Example:
        # Create a FileManager instance with file paths.
        file_manager = FileManager("network.graphml", "rate_cards.json")

        # Load rate cards data.
        rate_cards = file_manager.load_rate_cards()

        # Load the network graph.
        graph = file_manager.load_network_graph()

    Note:
        Ensure that the provided file paths are valid and that the file contents are correctly
        formatted for accurate data loading.
    """

    def __init__(self, graphml_file_path, json_file_path):
        """
        Initialize a FileManager instance with file paths.

        Args:
            graphml_file_path (str): The file path to the GraphML file containing the network graph.
            json_file_path (str): The file path to the JSON file containing rate cards data.
        """
        self.graphml_file_path = os.path.abspath(graphml_file_path)
        self.json_file_path = os.path.abspath(json_file_path)

    def load_rate_cards(self):
        """
        Load rate cards data from a JSON file.

        Returns:
            dict: Loaded rate cards data.
        """
        try:
            with open(self.json_file_path, "r", encoding="utf-8") as rate_cards_file:
                rate_cards_data = json.load(rate_cards_file)
                # Lowercase rate card names and replace spaces with underscores
                for rate_card_name, rate_card in rate_cards_data.items():
                    lower_cased_name = rate_card_name.lower().replace(" ", "_")
                    rate_cards_data[lower_cased_name] = rate_card
                    if lower_cased_name != rate_card_name:
                        del rate_cards_data[rate_card_name]
            return rate_cards_data.get("rate_cards", {})
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"JSON file not found: {self.json_file_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error decoding JSON from file: {self.json_file_path}"
            ) from e

    def load_network_graph(self):
        """
        Load a network graph from a GraphML file.

        Returns:
            nx.Graph: Loaded network graph.
        """
        try:
            return nx.read_graphml(self.graphml_file_path, node_type=str)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"GraphML file not found: {self.graphml_file_path}"
            ) from e


class NetworkCostCalculator:
    """
    NetworkCostCalculator is a class for calculating network infrastructure costs based on rate
    cards and a network graph.

    Attributes:
       graph (nx.Graph): The network graph representing the infrastructure.
       rate_cards (dict): A dictionary of rate cards, where each card is identified by a name.

    Methods:
       __init__: Initializes the NetworkCostCalculator instance with file paths for rate cards
           and the network graph.
       calculate_route_cost: Calculates the cost of a route based on rate card and edge information.
       get_node_type: Gets the type of node from the network graph.
       get_node_price: Gets the price of a node type from the rate card.
       calculate_total_cost: Calculates the total cost for a specific rate card.
       get_routes: Gets all routes in the graph.
       add_route_to_results: Adds route information to the results' dictionary.
       process_graph: Calculates costs for all rate cards for the given graph.

    Note:
       Ensure that the rate cards are provided in a compatible format and that the graph represents
       the network infrastructure accurately for accurate cost calculations.
    """

    def __init__(self, json_file_path: str, graphml_file_path: str) -> None:
        """
        Initialize the NetworkCostCalculator with file paths for rate cards and the graph.

        Args:
            json_file_path (str): The path to the JSON rate cards file.
            graphml_file_path (str): The path to the GraphML graph file.
        """
        # Create a FileManager instance for handling file operations
        file_manager = FileManager(graphml_file_path, json_file_path)

        self.graph = file_manager.load_network_graph()
        self.rate_cards = {
            rate_card["name"].lower().replace(" ", "_"): rate_card
            for rate_card in file_manager.load_rate_cards()
        }

        # Configure logging
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)

    def calculate_route_cost(
        self, rate_card: Dict, route: Tuple[str, str, Dict[str, Union[str, int]]]
    ) -> int:
        """
        Calculate the cost of a route based on rate card and edge information.

        Args:
            rate_card (Dict): The rate card specifying cost rates.
            route (Tuple[str, str, Dict[str, Union[str, int]]]): Tuple containing route information
                (start node, end node, and edge data).

        Returns:
            int: The calculated cost.
        """
        start_node, end_node, edge_data = route
        start_node_price = self.get_node_price(
            rate_card, self.get_node_type(start_node)
        )
        end_node_price = self.get_node_price(rate_card, self.get_node_type(end_node))

        return (
            start_node_price
            + (
                edge_data.get("length")
                * rate_card.get(f"Trench/m ({edge_data.get('material')})", 0)
            )
            + end_node_price
        )

    def get_node_type(self, node: str) -> str:
        """
        Get the type of node from the network graph.

        Args:
            node (str): The ID of the node.

        Returns:
            str: The type of the node.
        """
        return self.graph.nodes[node].get("type", "")

    @staticmethod
    def get_node_price(rate_card: Dict, node_type: str) -> int:
        """
        Get the price of a node type from the rate card.

        Args:
            rate_card (Dict): The rate card specifying cost rates.
            node_type (str): The type of the node.

        Returns:
            int: The price of the node type.
        """
        return rate_card.get(node_type, 0)

    async def calculate_total_cost(self, rate_card_name: str) -> Dict:
        """
        Calculate the total cost of building the network based on a specified rate card.

        Args:
            rate_card_name (str): The name of the rate card to use for cost calculation.

        Returns:
            Dict: A dictionary containing the results.
        """
        rate_card = self.rate_cards.get(rate_card_name)
        if not rate_card:
            raise ValueError(f"Rate card '{rate_card_name}' not found.")

        results = {}

        # Concurrently calculate costs for each edge
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = []

            for route in self.get_routes():
                task = loop.run_in_executor(
                    executor,
                    self.calculate_route_cost,
                    rate_card,
                    route,
                )
                tasks.append(task)

            # Gather results
            route_costs = await asyncio.gather(*tasks)
            total_cost = sum(route_costs)

        # Create the result dictionary
        results_key = f"rate_card_{rate_card_name}"
        results[results_key] = {}
        for route in self.get_routes():
            route_cost = self.calculate_route_cost(rate_card, route)
            self.add_route_to_results(results, results_key, route, route_cost)

        # Add the total cost for all routes under this rate card
        results[results_key][f"{results_key}_routes_total"] = total_cost

        return results

    def get_routes(self) -> List[Tuple[str, str, Dict[str, Union[str, int]]]]:
        """
        Get all routes in the graph as a list of tuples containing route information.

        Returns:
            List[Tuple[str, str, Dict[str, Union[str, int]]]]: A list of route tuples.
        """
        routes = []
        for source_node, target_node, edge_data in self.graph.edges(data=True):
            routes.append((source_node, target_node, edge_data))
        return routes

    @staticmethod
    def add_route_to_results(
        results: Dict,
        results_key: str,
        route: Tuple[str, str, Dict[str, Union[str, int]]],
        route_cost: int,
    ) -> None:
        """
        Add route information to the results' dictionary.

        Args:
            results (Dict): The dictionary containing results.
            results_key (str): The key for the rate card results.
            route (Tuple[str, str, Dict[str, Union[str, int]]]): Tuple containing route information
                (start node, end node, and edge data).
            route_cost (int): The calculated cost of the route.

        Returns:
            None
        """
        start_node, end_node, edge_data = route
        route_key = f"route_{start_node}--{end_node}"
        if results_key not in results:
            results[results_key] = {}
        results[results_key][route_key] = {
            "length": edge_data["length"],
            "material": edge_data["material"],
            "cost": route_cost,
        }

    async def process_graph(self) -> Dict:
        """
        Calculate costs for all rate cards for the given graph.

        Returns:
            Dict: A dictionary containing the results for all rate cards.
        """
        try:
            results = {}

            for rate_card_name in self.rate_cards.keys():
                self.logger.info(f"Calculating costs for rate card: {rate_card_name}")
                total_cost = await self.calculate_total_cost(rate_card_name)
                results.update(total_cost)

            self.logger.info("Calculation completed successfully.")
            return results
        except Exception as e:
            self.logger.error(f"Error processing graph: {str(e)}")


def main():
    """
    Main entry point for the Network Cost Calculator.

    Parses command-line arguments, loads the network graph and rate cards data,
    and calculates costs for all rate cards.

    Usage: To run the script, use the following command: python -m
    network_cost_calculator.network_cost_calculator <graphml_file_path> <rate_cards_json_file_path>
    """
    parser = argparse.ArgumentParser(description="Network Cost Calculator")
    parser.add_argument("graphml_file", type=str, help="Path to the GraphML file")
    parser.add_argument("json_file", type=str, help="Path to the JSON rate cards file")
    parser.parse_args()


if __name__ == "__main__":
    main()
