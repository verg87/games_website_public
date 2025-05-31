from django import forms
from random import randint
import math


def _geometric_pattern_helper(memory: list, power: int) -> int:
    """Returns next number in geometric sequence"""

    if all([memory[i] * power == memory[i + 1] for i in range(2)]):
        return memory[2] * power
    elif all([memory[i] / power == memory[i + 1] for i in range(2)]):
        return memory[2] // power

    return None


class PredictInput:
    """Take the user input and see whether it's in some pattern"""

    def predict_geometric_pattern(self, memory: list) -> int:
        """
        Returns the next term in the geometric sequence if found and valid,
        or None if no valid progression is detected.
        """

        if (power_of_2 := _geometric_pattern_helper(memory, 2)) != None:
            if 0 < power_of_2 <= 100:
                return power_of_2

        elif (power_of_3 := _geometric_pattern_helper(memory, 3)) != None:
            if 0 < power_of_3 <= 100:
                return power_of_3

        return None

    def predict_arithmetic_pattern(self, memory: list) -> int:
        """
        Returns the next term in the arithmetic sequence if found and valid,
        or None if no valid progression is detected.
        """

        if memory[1] - memory[0] == memory[2] - memory[1]:
            if 0 <= memory[2] + (memory[1] - memory[0]) <= 100:
                return memory[2] + (memory[1] - memory[0])

        return None

    def predict_exponential_pattern(self, memory: list) -> int:
        """
        Returns the next term in the exponential sequence if found and valid,
        or None if no valid pattern is detected.
        """

        if all(
            [math.sqrt(memory[i]) % 1 == 0 and memory[0] < memory[2] for i in range(3)]
        ):
            next_number = int((math.sqrt(memory[2]) + 1) * (math.sqrt(memory[2]) + 1))
            if 0 < next_number <= 100:
                return next_number

        elif all(
            [math.sqrt(memory[i]) % 1 == 0 and memory[0] > memory[2] for i in range(3)]
        ):
            next_number = int((math.sqrt(memory[2]) - 1) * (math.sqrt(memory[2]) - 1))
            if 0 < next_number <= 100:
                return next_number

        return None

    def predict_fibonacci_pattern(self, memory: list) -> int:
        """
        Returns the next Fibonacci-like term if found and valid,
        or None if no valid progression is detected.
        """

        if memory[2] == memory[1] + memory[0]:
            next_number = memory[2] + memory[1]
            if 0 < next_number <= 100:
                return next_number

        elif memory[0] == memory[1] + memory[2]:
            next_number = memory[1] - memory[2]
            if 0 < next_number <= 100:
                return next_number

        return None

    def predict_prime(self, memory: list) -> int:
        """
        Returns the prime number that follows the matched subsequence
        if found, or None if no match exists.
        """

        primes = [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
        ]
        
        if not all(num in primes for num in memory):
            return None
    
        if memory[0] > memory[-1]:
            primes = primes[::-1]
        
        index = primes.index(memory[-1])
        
        try:
            return primes[index+1]
        except IndexError:
            return None


class GuessNumGame(forms.Form):
    user_input = forms.IntegerField(
        min_value=0, max_value=100, label="Enter your number"
    )

    user_input.widget.attrs.update({"autofocus": "true"})

    input = PredictInput()

    def guess_num(self, memory: list[int]) -> int:
        """
        Guesses the next user number by checking if last few values were in some pattern.
        If not uses random forest regression model to predict next number
        """

        if len(memory) <= 4:
            return randint(0, 100)

        recent_values = memory[-5:-1]

        geometric = self.input.predict_geometric_pattern(recent_values[1:])
        arithmetic = self.input.predict_arithmetic_pattern(recent_values[1:])
        exponent = self.input.predict_exponential_pattern(recent_values[1:])
        fibonacci = self.input.predict_fibonacci_pattern(recent_values[1:])
        prime = self.input.predict_prime(recent_values[1:])

        operations = [geometric, arithmetic, exponent, fibonacci, prime]
        pattern_match = next(
            (i for i in range(len(operations)) if operations[i] != None), None
        )

        if pattern_match != None:
            return operations[pattern_match]

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

        fd_guess = randint(int(first_digits[1]), int(first_digits[2]))  
        sd_guess = randint(int(second_digits[1]), int(second_digits[2])) 

        guess_int = int(f"{fd_guess}{sd_guess}")

        return guess_int
