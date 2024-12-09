import random
from grammar.cnf import CNF  # Import CNF grammar parsing module
from collections import defaultdict

# Utility function to compute the logarithm of a value.
def log(x): 
    from math import log
    if x > 0: 
        return log(x)
    else: 
        return float("-inf")  # Return negative infinity for non-positive values

class PCNF:
    def __init__(self, grammar_file: str, probablity_file=""):
        """
        Initializes a PCNF (Probabilistic Chomsky Normal Form) parser.
        
        Args:
            grammar_file: Path to the grammar file defining rules in CNF.
            probablity_file: (Optional) Path to the file containing rule probabilities.
        """
        self.grammar = CNF(grammar_file)  # Load the CNF grammar rules
        if probablity_file == "":
            self.q = self.init_q()  # Initialize probabilities randomly
        else:
            self.q = self.read_pcfg_file(probablity_file)  # Load probabilities from file

    def read_pcfg_file(self, filename: str):
        """
        Reads rule probabilities from a PCFG (Probabilistic Context-Free Grammar) file.
        
        Args:
            filename: Path to the file containing rule probabilities.
        
        Returns:
            A defaultdict containing probabilities of unary and binary rules.
        """
        pcfg = []
        with open(filename) as file:
            for line in file:
                line = line.strip().split(" -> ")
                pcfg.append((line[0], line[1]))
        q = defaultdict(float)
        for rule in pcfg:
            tmp = rule[1].split()
            if len(tmp) == 2:
                q[tuple([rule[0], tmp[0]])] = float(tmp[1])  # Unary rule
            elif len(tmp) == 3:
                q[tuple([rule[0], tmp[0], tmp[1]])] = float(tmp[2])  # Binary rule
        return q

    def init_q(self):
        """
        Randomly initializes probabilities for grammar rules in the CNF grammar.

        Returns:
            A defaultdict containing randomly assigned probabilities for rules.
        """
        q = defaultdict(float)

        for A in self.grammar.nonterminals:
            c = 0  # Count of rules for a nonterminal

            # Count unary rules for A
            for A2, w in self.grammar.unary_rules:
                if A2 == A:
                    c += 1

            # Count binary rules for A
            for A2, B, C in self.grammar.binary_rules:
                if A2 == A:
                    c += 1

            sum = 0.0

            # Assign probabilities for unary rules
            for A2, w in self.grammar.unary_rules:
                if A2 == A:
                    if c == 1:
                        q[tuple([A, w])] = 1.0 - sum
                    else:
                        q[tuple([A, w])] = random.uniform(0, 1.0 - sum)
                    c -= 1
                    sum += q[tuple([A, w])]

            # Assign probabilities for binary rules
            for A2, B, C in self.grammar.binary_rules:
                if A2 == A:
                    if c == 1:
                        q[tuple([A, B, C])] = 1.0 - sum
                    else:
                        q[tuple([A, B, C])] = random.uniform(0, 1.0 - sum)
                    c -= 1
                    sum += q[tuple([A, B, C])]

        return q

    def sentence_prob(self, sentence: str):
        """
        Computes the probability of a given sentence based on the grammar.
        
        Args:
            sentence: The input sentence as a string.

        Returns:
            The log-probability of the sentence and the parse table.
        """
        P = defaultdict(lambda: float("-inf"))  # Stores log-probabilities
        table = defaultdict(None)  # Parse table

        sentence = sentence.strip().split(" ")
        length = len(sentence)

        # Base case: Initialize unary rules
        for i in range(1, length + 1):
            for A, w in self.grammar.unary_rules:
                if w == sentence[i - 1]:
                    P[(i, i, A)] = log(self.q.get((A, w), 0))
                    table[(i, i, A)] = [(i, i, w)]
                    table[(i, i, w)] = []

        # Dynamic programming over spans of increasing length
        for l in range(2, length + 1):
            for i in range(1, length + 2 - l):
                j = i + l - 1
                for k in range(i, j):
                    for A, B, C in self.grammar.binary_rules:
                        if (P.get((i, k, B), float("-inf")) != float("-inf") 
                        and P.get((k + 1, j, C), float("-inf")) != float("-inf")):
                            if (
                                P.get((i, k, B), float("-inf"))
                                + log(self.q.get((A, B, C), 0))
                                + P.get((k + 1, j, C), float("-inf"))
                            ) > P.get((i, j, A), float("-inf")):
                                P[(i, j, A)] = (
                                    P.get((i, k, B), float("-inf"))
                                    + log(self.q.get((A, B, C), 0))
                                    + P.get((k + 1, j, C), float("-inf"))
                                )
                                table[(i, j, A)] = [(i, k, B), (k + 1, j, C)]

        return P[1, length, "S"], table  # Probability of the sentence starting with S

    def gen_sentence(self, symbol):
        """
        Generates a random sentence based on the grammar and probabilities.
        
        Args:
            symbol: Starting non-terminal symbol.

        Returns:
            A generated sentence as a string.
        """
        tokens = []

        # Collect unary rule expansions
        for A, w in self.grammar.unary_rules:
            if A == symbol:
                num = int(self.q.get((A, w)) * 1000)
                for _ in range(num):
                    tokens.append(w)

        # Collect binary rule expansions
        for A, B, C in self.grammar.binary_rules:
            if A == symbol:
                num = int(self.q.get((A, B, C)) * 1000)
                for _ in range(num):
                    tokens.append(tuple([B, C]))

        # Randomly select a rule to expand
        inx = int(random.uniform(0, len(tokens)))
        next_symbol = tokens[inx]

        # Recursively generate sentence
        if isinstance(next_symbol, tuple):
            return (
                self.gen_sentence(next_symbol[0])
                + " "
                + self.gen_sentence(next_symbol[1])
            )
        else:
            return next_symbol
