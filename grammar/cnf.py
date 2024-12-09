from collections import defaultdict


class CNF:
    def __init__(self, grammar_file: str):
        self.cfg = self.read_cfg_file(grammar_file)
        self.nonterminals = self.get_noterminals()
        self.binary_rules = self.get_binary_rules()
        self.unary_rules = self.get_unary_rules()

    def read_cfg_file(self, filename: str):
        cfg = []
        with open(filename) as file:
            for line in file:
                line = line.strip().split(" -> ")
                cfg.append((line[0], line[1]))
        return cfg

    def get_noterminals(self):
        noterminal = set()
        for rule in self.cfg:
            noterminal.add(rule[0])
        return tuple(noterminal)

    def get_unary_rules(self):
        rules = []
        for rule in self.cfg:
            tmp = rule[1].split()
            if len(tmp) == 1:
                rules.append(tuple([rule[0], rule[1]]))
        return rules

    def get_binary_rules(self):
        rules = []
        for rule in self.cfg:
            tmp = rule[1].split()
            if len(tmp) == 2:
                rules.append(tuple([rule[0], tmp[0], tmp[1]]))
        return rules

    def parsable(self, sentence: str):
        P = defaultdict(bool)
        _P = defaultdict(bool)

        sentence = sentence.split(" ")
        length = len(sentence)

        for i in range(1, length + 1):
            for A, w in self.unary_rules:
                if w == sentence[i - 1]:
                    P[(i, i, A)] = True
                    _P[(i ,i ,A)] = [(i ,i ,A)]

        for l in range(2, length + 1):
            for i in range(1, length + 2 - l):
                j = i + l - 1
                for k in range(i, j):
                    for A, B, C in self.binary_rules:
                        if P[(i, k, B)] and P[(k + 1, j, C)]:
                            P[(i, j, A)] = True
                            _P[(i ,j ,A)] = [(i, k, B), (k + 1, j, C)]

        print(_P)
        return P[(1, length, "S")]
