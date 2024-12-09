import networkx as nx
import matplotlib.pyplot as plt
import time
import json  # Added for reading JSON files

class Ordered:
    def __init__(self, define_rules=None, probabilities=None, filename=None):
        if filename:
            self.define_rules, self.probabilities = self.load_grammar(filename)
        else:
            self.define_rules = define_rules
            self.probabilities = probabilities

        self.charts = []

    # Save grammar and probabilities to a JSON file
    def save_grammar(self, filename):
        data = {
            "define_rules": self.define_rules,
            "probabilities": self.probabilities,
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    def load_grammar(self, filename):
        with open(filename, "r") as file:
            data = json.load(file)
        return data["define_rules"], data["probabilities"]
    
    def predictor(self, rule, state):
        current_symbol = rule["rhs"][rule["dot"]]
        if current_symbol.isupper():
            return [{
                "lhs": current_symbol,
                "rhs": rhs,
                "dot": 0,
                "state": state,
                "end": state,
                "op": "PREDICTOR",
                "completor": [],
                "probability": self.probabilities[current_symbol][i][0]
            } for i, rhs in enumerate(self.define_rules[current_symbol])]
        return []

    def scanner(self, rule, next_input):
        current_symbol = rule["rhs"][rule["dot"]]
        if current_symbol.islower() and next_input in self.define_rules[current_symbol]:
            return [{
                "lhs": current_symbol,
                "rhs": [next_input],
                "dot": 1,
                "state": rule["end"],
                "end": rule["end"] + 1,
                "op": "SCANNER",
                "completor": [],
                "probability": self.probabilities[current_symbol][next_input]
            }]
        return []

    def completor(self, rule):
        return [
            {
                "lhs": r["lhs"],
                "rhs": r["rhs"],
                "dot": r["dot"] + 1,
                "state": r["state"],
                "end": rule["end"],
                "op": "COMPLETOR",
                "completor": [rule] + r["completor"],
                "probability": rule["probability"] * r["probability"]
            }
            for r in self.charts[rule["state"]]
            if r["dot"] < len(r["rhs"]) and r["rhs"][r["dot"]] == rule["lhs"]
        ]

    def early_parser(self, sentence: str):
        input_arr = sentence.split() + [""]
        # Initialize the chart with the initial state
        self.charts = [[{
            "lhs": "ROOT",
            "rhs": ["S"],
            "dot": 0,
            "state": 0,
            "end": 0,
            "op": "DUMMY",
            "completor": [],
            "probability": 1.0
        }]]

        # Parsing process
        for curr_state in range(len(input_arr)):
            curr_chart = self.charts[curr_state]
            next_chart = []

            for curr_rule in curr_chart:
                if curr_rule["dot"] < len(curr_rule["rhs"]):
                    # Perform prediction
                    for pred_rule in self.predictor(curr_rule, curr_state):
                        if pred_rule not in curr_chart:
                            curr_chart.append(pred_rule)

                    # Perform scanning
                    for scan_rule in self.scanner(curr_rule, input_arr[curr_state]):
                        if scan_rule not in next_chart:
                            next_chart.append(scan_rule)
                else:
                    # Perform completion
                    for comp_rule in self.completor(curr_rule):
                        if comp_rule not in curr_chart:
                            curr_chart.append(comp_rule)

            self.charts.append(next_chart)

        return self.charts

    def add_nodes_and_edges(self, graph, node, parent=None, depth=0):
        # Define a unique name for each node based on its attributes
        node_name = (node['lhs'], (node['state'], node['end']))
        graph.add_node(node_name, probability=node.get("probability", 1), layer=depth)
        
        if parent:
            # Add edge from parent to current node
            graph.add_edge(parent, node_name)

        # Recursively add child nodes
        for child in node.get('completor', []):
            self.add_nodes_and_edges(graph, child, parent=node_name, depth=depth + 1)

    def build_tree(self):
        roots = [r for r in self.charts[-2] if r["lhs"] == "ROOT" and r["dot"] == len(r["rhs"])]
        roots = sorted(roots, key=lambda root: root["probability"], reverse=True)
        root = roots[0]
        
        print(f"Prob: {root["probability"]}")
        # Create a directed graph
        graph = nx.DiGraph()

        # Add nodes and edges to the graph
        self.add_nodes_and_edges(graph, root)

        # Generate labels for visualization
        mapping = {node: node[0] for node in graph.nodes}

        # Set layout for the tree structure
        pos = nx.multipartite_layout(graph, subset_key="layer")

        # Visualize the graph
        plt.figure(figsize=(20, 10))
        nx.draw(
            graph,
            pos,
            labels=mapping,
            with_labels=True,
            arrows=True,
            node_size=3000,
            node_color="lightblue",
            font_size=12
        )
        plt.show()