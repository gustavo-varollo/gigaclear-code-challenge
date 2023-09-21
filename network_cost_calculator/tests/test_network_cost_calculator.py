"""
test_network_cost_calculator

This module contains unit tests for the NetworkCostCalculator class in the
'network_cost_calculator' module. It tests various aspects of the calculator's functionality to
ensure correctness.

Classes:
    TestNetworkCostCalculator: A test case class for testing the NetworkCostCalculator class.

Usage:
    To run the unit tests, execute this module directly or use a test runner such as 'unittest'.

Example:
    # Run the tests
    python -m unittest network_cost_calculator.tests.test_network_cost_calculator

Note: These tests are designed to verify the behavior and correctness of the
NetworkCostCalculator class.
"""

import asyncio
import json
import os
import tempfile
import unittest

import networkx as nx

from network_cost_calculator.network_cost_calculator import (
    NetworkCostCalculator,
    FileManager,
)


class TestFileManager(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment and create temporary files for testing.
        """
        # Create a temporary GraphML file
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".graphml"
        ) as graphml_file:
            graphml_file.write(
                """<?xml version="1.0" encoding="UTF-8"?>
            <graphml xmlns="http://graphml.graphdrawing.org/xmlns">
            <key attr.name="length" attr.type="long" for="edge" id="length" />
            <key attr.name="material" attr.type="string" for="edge" id="material" />
            <key attr.name="type" attr.type="string" for="node" id="type" />
                <graph edgedefault="undirected">
                    <node id="A">
                        <data key="type">Cabinet</data>
                    </node>
                    <node id="B">
                        <data key="type">Pot</data>
                    </node>
                    <edge source="A" target="B">
                        <data key="material">verge</data>
                        <data key="length">50</data>
                    </edge>
                </graph>
            </graphml>
            """
            )

        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".json"
        ) as json_file:
            json.dump(
                {
                    "rate_cards": [
                        {
                            "name": "Rate Card A",
                            "Cabinet": 1000,
                            "Trench/m (verge)": 50,
                            "Trench/m (road)": 100,
                            "Chamber": 200,
                            "Pot": 100,
                        },
                        {
                            "name": "Rate Card B",
                            "Cabinet": 1200,
                            "Trench/m (verge)": 40,
                            "Trench/m (road)": 80,
                            "Chamber": 200,
                            "Pot": 20,
                        },
                    ]
                },
                json_file,
            )

        # Get the file paths for the temporary files
        self.graphml_file_path = graphml_file.name
        self.json_file_path = json_file.name

    def tearDown(self):
        """
        Clean up temporary files after testing.
        """
        os.remove(self.graphml_file_path)
        os.remove(self.json_file_path)

    def test_load_rate_cards(self):
        """
        Test loading rate cards data from a JSON file.
        """
        file_manager = FileManager(self.graphml_file_path, self.json_file_path)
        rate_cards = file_manager.load_rate_cards()
        self.assertIsInstance(rate_cards, list)
        self.assertEqual(len(rate_cards), 2)

    def test_load_network_graph(self):
        """
        Test loading a network graph from a GraphML file.
        """
        file_manager = FileManager(self.graphml_file_path, self.json_file_path)
        graph = file_manager.load_network_graph()
        self.assertIsInstance(graph, nx.Graph)


class TestNetworkCostCalculator(unittest.TestCase):
    """
    TestNetworkCostCalculator

    This class defines a test case for the NetworkCostCalculator class in the
    'network_cost_calculator' module. It contains individual test methods to verify
    the correctness of various methods and functionalities of the calculator.

    Test Methods:
        test_get_node_type: Test getting the type of node.
        test_get_node_price: Test getting the price of a node type from a rate card.
        test_calculate_route_cost: Test calculating the cost of a route.
        test_calculate_total_cost: Test calculating total cost for a rate card.
        test_process_graph: Test processing the graph and calculating costs for all rate cards.
        test_empty_graph: Test handling an empty graph gracefully.
        test_rate_card_not_found: Test handling a rate card not found gracefully.
        test_invalid_json_file: Test handling an invalid JSON file gracefully.

    Usage:
        To run the test case, execute this class directly or use a test runner such as 'unittest'.

    Example:
        # Run this test case
        python -m unittest test_network_cost_calculator.TestNetworkCostCalculator
    """

    def setUp(self):
        """
        Set up test environment and create a NetworkCostCalculator instance.
        """

        # Create temporary files for GraphML and JSON data
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".graphml"
        ) as graphml_file:
            # Write graph data to the temporary GraphML file
            graphml_file.write(
                """<?xml version="1.0" encoding="UTF-8"?>
            <graphml xmlns="http://graphml.graphdrawing.org/xmlns">
            <key attr.name="length" attr.type="long" for="edge" id="length" />
            <key attr.name="material" attr.type="string" for="edge" id="material" />
            <key attr.name="type" attr.type="string" for="node" id="type" />
                <graph edgedefault="undirected">
                    <node id="A">
                        <data key="type">Cabinet</data>
                    </node>
                    <node id="B">
                        <data key="type">Pot</data>
                    </node>
                    <edge source="A" target="B">
                        <data key="material">verge</data>
                        <data key="length">50</data>
                    </edge>
                </graph>
            </graphml>
            """
            )

        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".json"
        ) as json_file:
            # Write rate card data to the temporary JSON file
            json.dump(
                {
                    "rate_cards": [
                        {
                            "name": "Rate Card A",
                            "Cabinet": 1000,
                            "Trench/m (verge)": 50,
                            "Trench/m (road)": 100,
                            "Chamber": 200,
                            "Pot": 100,
                        },
                        {
                            "name": "Rate Card B",
                            "Cabinet": 1200,
                            "Trench/m (verge)": 40,
                            "Trench/m (road)": 80,
                            "Chamber": 200,
                            "Pot": 20,
                        },
                    ]
                },
                json_file,
            )

        # Get the file paths for the temporary files
        self.graphml_file_path = graphml_file.name
        self.json_file_path = json_file.name

        # Initialize the NetworkCostCalculator with the temporary file paths
        self.calculator = NetworkCostCalculator(
            self.json_file_path, self.graphml_file_path
        )

    def test_get_node_type(self):
        """
        Test getting the type of node.
        """
        calculator = self.calculator  # Use the calculator created in setUp
        node_type = calculator.get_node_type("A")
        self.assertEqual(node_type, "Cabinet")

    def test_get_node_price(self):
        """
        Test getting the price of a node type from a rate card.
        """
        calculator = self.calculator  # Use the calculator created in setUp
        price = calculator.get_node_price(
            calculator.rate_cards.get("rate_card_a"), "Cabinet"
        )
        self.assertEqual(price, 1000)

    def test_calculate_route_cost(self):
        """
        Test calculating the cost of a route.
        """
        calculator = self.calculator
        rate_card = calculator.rate_cards["rate_card_a"]

        # The route is from node A to B with a length of 50 and material "verge"
        route = ("A", "B", {"material": "verge", "length": 50})
        cost = calculator.calculate_route_cost(rate_card, route)
        expected_cost = (
            1000 + 50 * rate_card["Trench/m (verge)"] + 100  # Cabinet + (50 * 50) + Pot
        )
        self.assertEqual(cost, expected_cost)

    def test_calculate_total_cost(self):
        """
        Test calculating total cost for a rate card.
        """
        calculator = self.calculator

        # Check if the rate card exists in calculator.rate_cards
        if "rate_card_a" not in calculator.rate_cards:
            self.fail(f"Rate card '{'rate_card_a'}' not found in calculator.rate_cards")

        # Retrieve the rate card
        rate_card = calculator.rate_cards["rate_card_a"]

        expected_total_cost = 0
        expected_result = {"rate_card_rate_card_a": {}}

        for route in calculator.get_routes():
            expected_route_name = f"route_{route[0]}--{route[1]}"
            route_cost = calculator.calculate_route_cost(rate_card, route)

            # Update the expected result
            expected_result["rate_card_rate_card_a"][expected_route_name] = {
                "length": route[2]["length"],
                "material": route[2]["material"],
                "cost": route_cost,
            }

            expected_total_cost += route_cost

        expected_result["rate_card_rate_card_a"][
            "rate_card_rate_card_a_routes_total"
        ] = expected_total_cost

        # Calculate the total cost using the calculate_total_cost method
        results = asyncio.run(calculator.calculate_total_cost("rate_card_a"))

        self.assertEqual(results, expected_result)

    def test_process_graph(self):
        """
        Test processing the graph and calculating costs for all rate cards.
        """
        calculator = self.calculator
        results = asyncio.run(calculator.process_graph())

        # Calculate the expected costs based on the provided graph and rate card data
        expected_result = {}
        for rate_card_name in calculator.rate_cards.keys():
            expected_rate_card_name = f"rate_card_{rate_card_name}"
            expected_result[expected_rate_card_name] = {}
            rate_card = calculator.rate_cards[rate_card_name]

            total_cost = 0
            for route in calculator.get_routes():
                route_cost = calculator.calculate_route_cost(rate_card, route)
                start_node, end_node, _ = route
                route_key = f"route_{start_node}--{end_node}"
                expected_result[expected_rate_card_name][route_key] = {
                    "length": route[2]["length"],
                    "material": route[2]["material"],
                    "cost": route_cost,
                }
                total_cost += route_cost

            expected_result[expected_rate_card_name][
                f"{expected_rate_card_name}_routes_total"
            ] = total_cost

        # Assert that the actual and expected results match
        self.assertEqual(results, expected_result)

    def test_empty_graph(self):
        """
        Test handling an empty graph gracefully.
        """
        calculator = self.calculator  # Use the calculator created in setUp

        # Calculator's graph attribute to use the empty graph
        calculator.graph = nx.Graph()

        # Calculate results for the empty graph
        results = asyncio.run(calculator.process_graph())

        # Expect an empty result dictionary for an empty graph
        expected_result = {
            "rate_card_rate_card_a": {"rate_card_rate_card_a_routes_total": 0},
            "rate_card_rate_card_b": {"rate_card_rate_card_b_routes_total": 0},
        }

        self.assertEqual(results, expected_result)

    def test_rate_card_not_found(self):
        """
        Test handling a rate card not found gracefully.
        """
        calculator = self.calculator  # Use the calculator created in setUp
        with self.assertRaises(ValueError):
            asyncio.run(calculator.calculate_total_cost("Nonexistent Rate Card"))

    def test_invalid_json_file(self):
        """
        Test handling an invalid JSON file gracefully.
        """
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".json"
        ) as json_file:
            # Write an invalid JSON data to the temporary JSON file
            json_file.write("Invalid JSON Data")

        # Create a FileManager instance with the temporary GraphML path and the invalid JSON path
        file_manager = FileManager(self.graphml_file_path, json_file.name)

        with self.assertRaises(ValueError) as context:
            # Use the FileManager to load rate cards
            file_manager.load_rate_cards()

        # Check that a JSONDecodeError is the cause of the raised ValueError
        self.assertIsInstance(context.exception.__cause__, json.JSONDecodeError)


if __name__ == "__main__":
    unittest.main()
