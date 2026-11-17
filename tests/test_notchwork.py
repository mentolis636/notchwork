"""Tests for notchwork.py. Run from the repo root with:

    python -m unittest discover -s tests -v
"""

import json
import os
import random
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

from notchwork import ALPHABET, REFLECTOR, ROTOR_WIRINGS, RotorMachine, parse_symbols  # noqa: E402


def random_symbols(rng, n):
    return "".join(rng.choice(ALPHABET) for _ in range(n))


class Cipher(unittest.TestCase):
    def test_known_message(self):
        machine = RotorMachine("LIGWMC", "SSSSSS")
        self.assertEqual(machine.process("MEET AT 21:30"), "2JP2 05 AR:XO")

    def test_decoding_is_the_same_operation(self):
        rng = random.Random(1)
        for _ in range(200):
            notches, start = random_symbols(rng, 6), random_symbols(rng, 6)
            text = random_symbols(rng, rng.randint(1, 1500))
            coded = RotorMachine(notches, start).process(text)
            self.assertEqual(RotorMachine(notches, start).process(coded), text)

    def test_a_symbol_never_codes_to_itself(self):
        rng = random.Random(2)
        for _ in range(100):
            notches, start = random_symbols(rng, 6), random_symbols(rng, 6)
            text = random_symbols(rng, 1000)
            coded = RotorMachine(notches, start).process(text)
            self.assertTrue(all(a != b for a, b in zip(text, coded)))

    def test_same_symbol_repeated_gives_changing_output(self):
        coded = RotorMachine("LIGWMC", "SSSSSS").process("A" * 60)
        self.assertGreater(len(set(coded)), 10)

    def test_wrong_start_position_garbles_the_message(self):
        text = "MEET AT 21:30 AT THE OLD BRIDGE"
        coded = RotorMachine("LIGWMC", "SSSSSS").process(text)
        self.assertNotEqual(RotorMachine("LIGWMC", "SSSSST").process(coded), text)

    def test_wrong_notch_garbles_a_long_message(self):
        rng = random.Random(3)
        text = random_symbols(rng, 800)
        coded = RotorMachine("LIGWMC", "SSSSSS").process(text)
        self.assertNotEqual(RotorMachine("LIGWMD", "SSSSSS").process(coded), text)

    def test_spaces_and_punctuation_pass_through(self):
        coded = RotorMachine("LIGWMC", "SSSSSS").process("A B, C.")
        self.assertEqual([c for c in coded if not c.isalnum()], [" ", ",", " ", "."])

    def test_lowercase_is_accepted(self):
        upper = RotorMachine("LIGWMC", "SSSSSS").process("HELLO 42")
        lower = RotorMachine("LIGWMC", "SSSSSS").process("hello 42")
        self.assertEqual(upper, lower)


class Tables(unittest.TestCase):
    def test_every_rotor_is_a_permutation_of_the_alphabet(self):
        for name, wiring in ROTOR_WIRINGS.items():
            self.assertEqual(sorted(wiring), sorted(ALPHABET), name)

    def test_reflector_pairs_symbols_and_never_fixes_one(self):
        self.assertEqual(sorted(REFLECTOR), sorted(ALPHABET))
        for i, ch in enumerate(ALPHABET):
            partner = REFLECTOR[i]
            self.assertNotEqual(partner, ch)
            self.assertEqual(REFLECTOR[ALPHABET.index(partner)], ch)


class KeyParsing(unittest.TestCase):
    def test_accepts_separators(self):
        self.assertEqual(parse_symbols("L-I-G-W-M-C", "Notches"), "LIGWMC")
        self.assertEqual(parse_symbols("l i g w m c", "Notches"), "LIGWMC")
        self.assertEqual(parse_symbols("7,K,2,W,M,9", "Notches"), "7K2WM9")

    def test_rejects_wrong_length_and_bad_symbols(self):
        for bad in ("LIGWM", "LIGWMCX", "LIGWM!", ""):
            with self.assertRaises(ValueError):
                parse_symbols(bad, "Notches")


class SharedVectors(unittest.TestCase):
    """The same vectors are checked against index.html by tests/check_web.js."""

    def test_vectors_file(self):
        with open(os.path.join(HERE, "vectors.json"), encoding="utf-8") as f:
            cases = json.load(f)
        self.assertGreater(len(cases), 10)
        for c in cases:
            got = RotorMachine(c["notches"], c["start"]).process(c["text"])
            self.assertEqual(got, c["coded"])


if __name__ == "__main__":
    unittest.main()
