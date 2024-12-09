import random
from grammar.cnf import CNF
from collections import defaultdict

def log(x): 
    from math import log
    if x > 0: return log(x)
    else: return float("-inf")

class PCNF:
    def __init__(self, grammar_file: str, probablity_file=""):
        self.grammar = CNF(grammar_file)
        if probablity_file == "":
            self.q = self.init_q()
        else:
            self.q = self.read_pcfg_file(probablity_file)

    def read_pcfg_file(self, filename: str):
        pcfg = []
        with open(filename) as file:
            for line in file:
                line = line.strip().split(" -> ")
                pcfg.append((line[0], line[1]))
        q = defaultdict(float)
        for rule in pcfg:
            tmp = rule[1].split()
            if len(tmp) == 2:
                q[tuple([rule[0], tmp[0]])] = float(tmp[1])
            elif len(tmp) == 3:
                q[tuple([rule[0], tmp[0], tmp[1]])] = float(tmp[2])
        return q

    def init_q(self):
        q = defaultdict(float)

        for A in self.grammar.nonterminals:
            c = 0
            for A2, w in self.grammar.unary_rules:
                if A2 == A:
                    c = c + 1

            for A2, B, C in self.grammar.binary_rules:
                if A2 == A:
                    c = c + 1

            sum = 0.0
            for A2, w in self.grammar.unary_rules:
                if A2 == A:
                    if c == 1:
                        q[tuple([A, w])] = 1.0 - sum
                    else:
                        q[tuple([A, w])] = random.uniform(0, 1.0 - sum)

                    c = c - 1
                    sum = sum + q[tuple([A, w])]

            for A2, B, C in self.grammar.binary_rules:
                if A2 == A:
                    if c == 1:
                        q[tuple([A, B, C])] = 1.0 - sum
                    else:
                        q[tuple([A, B, C])] = random.uniform(0, 1.0 - sum)

                    c = c - 1
                    sum = sum + q[tuple([A, B, C])]
        return q

    def sentence_prob(self, sentence: str):
        P = defaultdict(lambda: float("-inf"))
        table = defaultdict(None)

        sentence = sentence.strip().split(" ")
        length = len(sentence)

        for i in range(1, length + 1):
            for A, w in self.grammar.unary_rules:
                if w == sentence[i - 1]:
                    P[(i, i, A)] = log(self.q.get((A, w), 0))
                    table[(i, i, A)] = [(i, i, w)]
                    table[(i, i, w)] = []


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
                                
                                # if i == 1 and A == "S":
                                #     print(f"Substring (1, {j}) parsed.")

        return P[1, length, "S"], table

    def gen_sentence(self, symbol):
        tokens = []
        for A, w in self.grammar.unary_rules:
            if A == symbol:
                num = int(self.q.get((A, w)) * 1000)
                for _ in range(num):
                    tokens.append(w)
        for A, B, C in self.grammar.binary_rules:
            if A == symbol:
                num = int(self.q.get((A, B, C)) * 1000)
                for _ in range(num):
                    tokens.append(tuple([B, C]))
        inx = int(random.uniform(0, len(tokens)))
        next_symbol = tokens[inx]
        if isinstance(next_symbol, tuple):
            return (
                self.gen_sentence(next_symbol[0])
                + " "
                + self.gen_sentence(next_symbol[1])
            )
        else:
            return next_symbol
