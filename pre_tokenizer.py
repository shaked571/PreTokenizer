import os
import ntpath
from tqdm import tqdm
from typing import Optional


class PreTokenizer:
    rule_file = 'bgupreflex_withdef.utf8'
    rule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'rules', rule_file))

    def __init__(self, use_unichar=True):
        self.rules = self.get_rules()
        if not use_unichar:
            self.rules = [r for r in self.rules if len(r[0]) > 1]
        self.rule_d = dict(self.rules)
        self.prefix_rules = set([list(r[0])[0] for r in self.rules])

    def line2rule(self, line: str) -> Optional[tuple]:
        if len(line) < 2:
            return
        lsplited = line.split()
        chars = lsplited.pop(0)
        chars_splits = list(set([w for w in lsplited if '^' in w or w == chars]))
        res = [chars]
        for cs in chars_splits:
            css = [i for i in list(cs) if i != "^"]
            if all([c in chars for c in css]):
                res.append(cs)
        return tuple(res)

    def get_rules(self, path=rule_path):
        rules = []
        with open(path, mode="r", encoding='utf-8') as f:
            for l in f:
                rule = self.line2rule(l)
                if rule is not None:
                    rules.append(rule)
        rules = sorted(rules, key=lambda x: len(x[0]), reverse=True)

        return rules

    def pre_tok(self, text: str) -> str:
        res = ''
        txt_split = text.split()
        for t in txt_split:
            if any([t.startswith(c) for c in self.prefix_rules]):
                lp = self.get_longest_prefix(t)
                if lp is None:
                    res += f" {t}"
                    continue
                rule = self.rule_d[lp]
                res += self.break_word(t, rule)
            else:
                res += f" {t}"
        return res[1:]  # remove the first redundant space

    def get_longest_prefix(self, t):
        for r in self.rules:
            if t.startswith(r[0]):  # rules are sorted from the longest to shortest
                return r[0]
        return None

    def break_word(self, word, rule):
        sub_t = rule.split('^')
        suffix = word.split("".join(sub_t), 1)[1]
        res = " " + " ".join(sub_t) + " " + suffix
        return res

    def split_file(self, path, out_path=None):
        if out_path is None:
            name = ntpath.basename(path)
            name += ".splitted"
            out_path = os.path.abspath(os.path.join(path, name))

        res = ""
        with open(path, mode="r", encoding='utf-8') as f:
            for l in tqdm(f):
                 res += self.pre_tok(l) + "\n"

        with open(out_path, mode="w", encoding='utf-8') as fo:
            fo.write(res)



if __name__ == '__main__':
        pth = "D:\he_dedup-train.txt"
        pt = PreTokenizer()
        pt.split_file(pth)