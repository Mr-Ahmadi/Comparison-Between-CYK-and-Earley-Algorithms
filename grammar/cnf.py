from collections import defaultdict

class CNF:
    def __init__(self, grammar_file: str):
        # Initialize the CNF object with the grammar file.
        # Read the grammar file and extract nonterminals, binary, and unary rules.
        self.cfg = self.read_cfg_file(grammar_file)
        self.nonterminals = self.get_noterminals()
        self.binary_rules = self.get_binary_rules()
        self.unary_rules = self.get_unary_rules()

    def read_cfg_file(self, filename: str):
        # Read a context-free grammar (CFG) file and parse rules into a list of tuples.
        cfg = []
        with open(filename) as file:
            for line in file:
                line = line.strip().split(" -> ")  # Split the rule into LHS and RHS.
                cfg.append((line[0], line[1]))  # Append as a tuple (LHS, RHS).
        return cfg

    def get_noterminals(self):
        # Extract nonterminal symbols from the grammar rules.
        noterminal = set()
        for rule in self.cfg:
            noterminal.add(rule[0])  # Add the LHS of each rule to the set of nonterminals.
        return tuple(noterminal)

    def get_unary_rules(self):
        # Extract unary rules (rules where RHS has one symbol).
        rules = []
        for rule in self.cfg:
            tmp = rule[1].split()  # Split RHS into components.
            if len(tmp) == 1:  # Check if the RHS has only one symbol.
                rules.append(tuple([rule[0], rule[1]]))
        return rules

    def get_binary_rules(self):
        # Extract binary rules (rules where RHS has exactly two symbols).
        rules = []
        for rule in self.cfg:
            tmp = rule[1].split()  # Split RHS into components.
            if len(tmp) == 2:  # Check if the RHS has exactly two symbols.
                rules.append(tuple([rule[0], tmp[0], tmp[1]]))
        return rules

    def parsable(self, sentence: str):
        # Check if a given sentence can be parsed using the CYK algorithm.
        P = defaultdict(bool)  # Dynamic programming table for parsability.
        _P = defaultdict(bool)  # Table to store back-pointers for reconstruction.

        sentence = sentence.split(" ")  # Split the sentence into words.
        length = len(sentence)  # Get the length of the sentence.

        # Handle unary rules for the diagonal of the table.
        for i in range(1, length + 1):
            for A, w in self.unary_rules:
                if w == sentence[i - 1]:  # Check if the unary rule matches the word.
                    P[(i, i, A)] = True
                    _P[(i, i, A)] = [(i, i, A)]

        # Handle binary rules for spans of increasing length.
        for l in range(2, length + 1):  # Length of the span.
            for i in range(1, length + 2 - l):  # Start index of the span.
                j = i + l - 1  # End index of the span.
                for k in range(i, j):  # Split point of the span.
                    for A, B, C in self.binary_rules:
                        # Check if the span can be created by combining two sub-spans.
                        if P[(i, k, B)] and P[(k + 1, j, C)]:
                            P[(i, j, A)] = True
                            _P[(i, j, A)] = [(i, k, B), (k + 1, j, C)]

        print(_P)  # Print the back-pointers for debugging or further processing.
        return P[(1, length, "S")]  # Return whether the entire sentence is parsable.
