import os
from unittest import TestCase
from pre_tokenizer import PreTokenizer


class TestPreTokenizer(TestCase):
    pre_tokenizer = PreTokenizer()

    def test_split_a_file(self):
        # Arrange
        example_file_text = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'test_data', 'simple_text'))
        out_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'test_data', 'out'))
        # Act
        self.pre_tokenizer.split_file(example_file_text, out_path)
        # Assert
        self.assertTrue(os.path.isfile(out_path))
        os.remove(out_path)

    def test_not_split_known_words(self):
        # Arrange
        text = "אבא שלי שמח ."
        expected_res = text
        # Act
        res = self.pre_tokenizer.act(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split.")

    def test_split_basic_text(self):
        # Arrange
        text = "אבא הלך לעבודה."
        expected_res = "אבא ה לך ל עבודה."
        # Act
        res = self.pre_tokenizer.act(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split.")

    def test_split_basic_text_without_unichar(self):
        # Arrange
        text = "כשאבא הלך לעבודה."
        expected_res = "כש אבא הלך לעבודה."
        pre_wo_unichar = PreTokenizer(use_unichar=False)
        # Act
        res = pre_wo_unichar.act(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split in uni char mode.")

    def test_split_2_lines(self):
        # Arrange
        text = "אבא הלך לעבודה." + "\n" + "אבא הלך לעבודה."
        expected_res = "אבא ה לך ל עבודה." + " " +"אבא ה לך ל עבודה."
        # Act
        res = self.pre_tokenizer.act(text)
        # Assert
        self.assertEqual(expected_res, res, "Failed on simple split.")

    def test_line2rule(self):
        # Arrange
        line = "וכשכ ו^כש^כ CONJ+TEMP-SUBCONJ+PREPOSITION:: ו^כש^כ CONJ+TEMP-SUBCONJ+ADVERB:: ו^כש^כ^ה CONJ+TEMP-SUBCONJ+PREPOSITION+DEF::"
        expected_res = tuple(['וכשכ', "ו^כש^כ"])
        # Act
        res = self.pre_tokenizer.line2rule(line)
        # Assert
        self.assertEqual(res, expected_res)

    def test_get_rules(self):
        # Arrange
        exa_text_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'test_data', 'rules_sample'))
        # Act
        res = self.pre_tokenizer.get_rules(exa_text_path)
        expected_res = [('כשמה', 'כש^מ^ה'), ('כשכ', 'כש^כ'), ('כשל', 'כש^ל'), ('כשמ', 'כש^מ'), ('שמ', 'ש^מ'),
                        ('ל', 'ל')]
        # Assert
        self.assertEqual(expected_res, res)

    def test_get_longest_prefix(self):
        # Arrange
        w = "כשהאיש"
        expected_res = "כשה"
        # Act
        res = self.pre_tokenizer.get_longest_prefix(w)
        # Assert
        self.assertEqual(expected_res, res)

    def test_break_word(self):
        # Arrange
        word = "כשהאנשים"
        rule = "כש^ה"
        expected_res = " כש ה אנשים"
        # Act
        res = self.pre_tokenizer.break_word(word, rule)
        # Assert
        self.assertEqual(expected_res, res)

    def test_break_word_with_sign_long(self):
        # Arrange
        pre_tokenizer_sign = PreTokenizer(separator='$$')
        word = "שמשביעים"
        rule = "ש^מש^ב"
        expected_res = " ש$$ מש$$ ב$$ יעים"
        # Act
        res = pre_tokenizer_sign.break_word(word, rule)
        # Assert
        self.assertEqual(expected_res, res)

    def test_break_word_with_punct(self):
        # Arrange
        word = "כשהאנשים."
        rule = "כש^ה"
        expected_res = " כש ה אנשים."
        # Act
        res = self.pre_tokenizer.break_word(word, rule)
        # Assert
        self.assertEqual(expected_res, res)
