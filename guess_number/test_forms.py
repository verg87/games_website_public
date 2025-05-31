from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch
import random
from .forms import GuessNumGame, PredictInput


class PredictInputMixinTests(TestCase):
    client = Client
    cls = PredictInput

    def test_geometric_pattern(self) -> None:
        positive_sequence_2 = [4, 8, 16]
        positive_sequence_3 = [3, 9, 27]

        negative_sequence_2 = [64, 32, 16]
        negative_sequence_3 = [81, 27, 9]

        p_power_of_2 = self.cls.predict_geometric_pattern(self.cls, positive_sequence_2)
        p_power_of_3 = self.cls.predict_geometric_pattern(self.cls, positive_sequence_3)

        n_power_of_2 = self.cls.predict_geometric_pattern(self.cls, negative_sequence_2)
        n_power_of_3 = self.cls.predict_geometric_pattern(self.cls, negative_sequence_3)

        self.assertEqual(p_power_of_2, 32)
        self.assertEqual(p_power_of_3, 81)

        self.assertEqual(n_power_of_2, 8)
        self.assertEqual(n_power_of_3, 3)

    def test_arithmetic_pattern(self) -> None:
        p_sequence = [5, 10, 15]
        n_sequence = [35, 30, 25]

        positive = self.cls.predict_arithmetic_pattern(self.cls, p_sequence)
        negative = self.cls.predict_arithmetic_pattern(self.cls, n_sequence)

        self.assertEqual(positive, 20)
        self.assertEqual(negative, 20)

    def test_exponential_pattern(self) -> None:
        p_sequence = [1, 4, 9]
        n_sequence = [49, 36, 25]

        positive = self.cls.predict_exponential_pattern(self.cls, p_sequence)
        negative = self.cls.predict_exponential_pattern(self.cls, n_sequence)

        self.assertEqual(positive, 16)
        self.assertEqual(negative, 16)

    def test_fibonacci_pattern(self) -> None:
        p_sequence = [3, 5, 8]
        n_sequence = [55, 34, 21]

        positive = self.cls.predict_fibonacci_pattern(self.cls, p_sequence)
        negative = self.cls.predict_fibonacci_pattern(self.cls, n_sequence)

        self.assertEqual(positive, 13)
        self.assertEqual(negative, 13)

    def test_prime_pattern(self) -> None:
        p_sequence = [23, 29, 31]
        n_sequence = [47, 43, 41]

        positive = self.cls.predict_prime(self.cls, p_sequence)
        negative = self.cls.predict_prime(self.cls, n_sequence)

        self.assertEqual(positive, 37)
        self.assertEqual(negative, 37)


class GuessNumGameTests(TestCase):
    client = Client
    form = GuessNumGame

    def setUp(self) -> None:
        usr = "testuser"
        psw = "some12psw23"

        self.path = "/guess_the_number/"
        self.ctx_var = "user_input"
        self.ctx_results = ["bot_guess", "rounds", "accuracy"]

        User = get_user_model()
        User.objects.create_user(username=usr, password=psw)

        self.client.login(username=usr, password=psw)

    def test_behavior_with_valid_input(self) -> None:
        response = self.client.post(self.path, {self.ctx_var: 20})

        self.assertTrue(
            all([response.context[result] != None for result in self.ctx_results])
        )

    def test_behavior_with_invalid_input(self) -> None:
        response = self.client.post(self.path, {self.ctx_var: 120})

        self.assertFalse(
            all([result in response.context for result in self.ctx_results])
        )

    def test_guess_num_with_data_and_patterns(self) -> None:
        memory = [1, 2, 3, 5, 8]

        result = self.form.guess_num(self.form, memory)

        self.assertEqual(result, 8)

    def test_guess_num_with_data_no_patterns(self) -> None:
        memory = [7, 23, 45, 89, 26]

        result = self.form.guess_num(self.form, memory)

        self.assertTrue(25 <= result <= 47)

    def test_guess_num_with_data_no_patterns_functionality(self) -> None:
        recent_values = [7, 23, 45, 89]

        with patch("random.randint", side_effect=[2, 5]):
            first_digits = []
            second_digits = []

            for val in recent_values:
                val_str = str(val)

                if len(val_str) == 1:
                    first_digits.append("0")
                    second_digits.append(val_str[0])
                else:
                    first_digits.append(val_str[0])
                    second_digits.append(val_str[1])

            first_digits = sorted(first_digits)
            second_digits = sorted(second_digits)

            fd_guess = random.randint(int(first_digits[1]), int(first_digits[2]))
            sd_guess = random.randint(int(second_digits[1]), int(second_digits[2]))

            guess_int = int(f"{fd_guess}{sd_guess}")

            self.assertEqual(first_digits, ["0", "2", "4", "8"])
            self.assertEqual(second_digits, ["3", "5", "7", "9"])

            self.assertEqual(fd_guess, 2)
            self.assertEqual(sd_guess, 5)

            self.assertEqual(guess_int, 25)

    def test_guess_num_without_data(self) -> None:
        result = self.form.guess_num(self.form, [])

        self.assertTrue(0 <= result <= 100)
