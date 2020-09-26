import os
from unittest import TestCase
from pre_tokenizer import PreTokenizer


class TestPreTokenizer(TestCase):
    # example_file_text =
    pre_tokenizer = PreTokenizer()

    def test_split_basic_text(self):
        # Arrange
        text = "אבא הלך לעבודה."
        expected_res = "אבא ה לך ל עבודה."
        # Act
        res = self.pre_tokenizer.pre_tok(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split.")

    def test_split_2_lines(self):
        # Arrange
        text = "אבא הלך לעבודה." + "\n" + "אבא הלך לעבודה."
        expected_res = "אבא ה לך ל עבודה." + " " +"אבא ה לך ל עבודה."
        # Act
        res = self.pre_tokenizer.pre_tok(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split.")


    def test_line2rule(self):
        # Arrange
        line = "וכשכ ו^כש^כ CONJ+TEMP-SUBCONJ+PREPOSITION:: ו^כש^כ CONJ+TEMP-SUBCONJ+ADVERB:: ו^כש^כ^ה CONJ+TEMP-SUBCONJ+PREPOSITION+DEF::"
        expected_res = tuple(['וכשכ', "ו^כש^כ"])
        # Act
        res = self.pre_tokenizer.line2rule(line)
        # Assert
        self.assertEquals(res, expected_res)

    def test_get_rules(self):
        exa_text_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'test_data', 'rules_sample'))

        res = self.pre_tokenizer.get_rules(exa_text_path)
        expected_res = [('כשמה', 'כש^מ^ה'), ('כשכ', 'כש^כ'), ('כשל', 'כש^ל'), ('כשמ', 'כש^מ'), ('שמ', 'ש^מ'),
                        ('ל', 'ל')]

        self.assertEquals(expected_res, res)

    def test_get_longest_prefix(self):
        w = "כשהאיש"
        expected_res = "כשה"
        res = self.pre_tokenizer.get_longest_prefix(w)
        self.assertEquals(expected_res, res)

    def test_break_word(self):
        # Arrange
        word = "כשהאנשים"
        rule = "כש^ה"
        expected_res = " כש ה אנשים"

        # Act
        res = self.pre_tokenizer.break_word(word, rule)

        self.assertEquals(expected_res, res)

    def test_break_word_with_punct(self):
        # Arrange
        word = "כשהאנשים."
        rule = "כש^ה"
        expected_res = " כש ה אנשים."

        # Act
        res = self.pre_tokenizer.break_word(word, rule)

        self.assertEquals(expected_res, res)
