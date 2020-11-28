import os
import ntpath
from tqdm import tqdm
from typing import Optional, Set
import argparse
import logging

class PreTokenizer:
    _NOT_TO_SPlIT: Set[str]
    rule_file = 'bgupreflex_withdef.utf8'
    rule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'rules', rule_file))

    def __init__(self, input_f, output_f, use_unichar=True, separator='', improved_mode=True):
        self.logger = logging.getLogger("PreTokenizer")
        if improved_mode:
            self.act = self.pre_tok_improved
        else:
            self.act = self.pre_tok_classic

        self._NOT_TO_SPlIT = {'של', 'שלכם', 'שלנו', 'שלהם', 'שלך', 'שלי', 'מי', 'מה'}
        self.rules = self.get_rules()
        if not use_unichar:
            self.rules = [r for r in self.rules if len(r[0]) > 1]
        self.separator = separator.strip('"\'')
        if separator.isdigit() or separator.isspace() or separator.isalpha():
            raise ValueError(f"The separator is {separator} - but it can't be a number, space or only letters.")
        self.rule_d = dict(self.rules)
        self.prefix_rules = set([list(r[0])[0] for r in self.rules])

        self.logger.info(f"Input file: {input_f}")
        self.logger.info(f"Output file: {output_f}")
        if self.separator == "":
            self.logger.info(f"Not using separator")
        else:
            self.logger.info(f"Separator used: {self.separator}")
        self.logger.info(f"Using unichar for separation: {use_unichar}")
        self.logger.info(f"Run on improved mode: {improved_mode}")



    @staticmethod
    def line2rule(line: str) -> Optional[tuple]:
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

    def pre_tok_improved(self, text: str) -> str:
        res = ''
        txt_split = text.split()
        for t in txt_split:
            if any([t.startswith(c) for c in self.prefix_rules]) and t not in self._NOT_TO_SPlIT:
                lp = self.get_longest_prefix(t)
                if lp is None or len(t) < len(lp) + 2:
                    res += f" {t}"
                    continue
                rule = self.rule_d[lp]
                res += self.break_word(t, rule)
            else:
                res += f" {t}"
        return res[1:]  # remove the first redundant space

    def pre_tok_classic(self, text: str) -> str:
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
        res = " " + f"{self.separator} ".join(sub_t) + f"{self.separator} " + suffix
        return res

    def split_file(self, path, out_path=None):
        if out_path is None:
            name = ntpath.basename(path)
            name += ".splitted"
            out_path = os.path.abspath(os.path.join(path, name))

        res = ""
        with open(path, mode="r", encoding='utf-8') as f:
            for l in tqdm(f):
                res += self.act(l) + "\n"

        with open(out_path, mode="w", encoding='utf-8') as fo:
            fo.write(res)


if __name__ == '__main__':
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')


    parser = argparse.ArgumentParser(description='Pre split an Hebrew text.')
    parser.add_argument('input', type=str, help='The path to he input file')
    parser.add_argument('output', type=str,
                        help='The path to he output file, if not supplied the output file default would be ['
                             'InputFile].splitted')
    parser.add_argument('-unichar', type=str2bool, default=True,
                        help="If False, do not use the one chars to break the sentence The default is True i.e. "
                             "to break also unichars as Hey (the 5th letter in the Alef Bet),"
                             " Bet (the 2th letter in the Alef Bet) etc.")
    parser.add_argument('-improved', type=str2bool, default=True,
                        help="If True wouldn't split a close set of  common words and run with a condition that "
                             "the algorithm would  split a word only if the len of the word is bigger or equal to"
                             " the len of the prefix. By default True, unless run with False ")
    parser.add_argument('-separator', type=str, default='',
                        help="A sign to seperate every char, for example using the flag \n"
                             "-separator $$\n"
                             "  will seperate a [to-ken] to to$$ ken. The default is ''")

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    pt = PreTokenizer(input_path, output_path, args.unichar, args.separator, args.improved)
    pt.split_file(input_path, output_path)
