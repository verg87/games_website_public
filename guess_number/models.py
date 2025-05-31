from django.db import models
from collections import Counter
from datetime import datetime, timedelta, timezone
from core.generic_models.time_stamp_model import TimeStampedModel


class GuessNumber(TimeStampedModel):
    """Main model class for guess_number app"""

    rounds = models.IntegerField(default=1)
    accuracy = models.FloatField(default=0.0)

    memory = models.TextField(default="")

    guessed_correctly = 0

    def get_memory(self) -> list[int]:
        """Retrieves the memory as a list"""

        last_object = GuessNumber.objects.last()
        if last_object and last_object.memory:
            last_object.memory = last_object.memory.strip()

            return [int(num) for num in last_object.memory.split(" ")]

        return []

    def get_object(self, user_value: int, bot_guess: int) -> models.Model:
        """
        Return the last object in the table
        Create an object if there's none in the table
        Create a new object if the last one expired
        """

        if bot_guess == user_value:
            accuracy = 100
        else:
            accuracy = 0

        if not GuessNumber.objects.exists():
            GuessNumber.objects.create(rounds=1, memory=user_value, accuracy=accuracy)

        if games_info.is_expired(30): # pragma: no cover
            GuessNumber.objects.create(rounds=1, memory=user_value, accuracy=accuracy)

        last_object = GuessNumber.objects.last()

        return last_object

    def update_table(self, last_object: models.Model, new_value: int) -> None:
        """Updates the memory and rounds"""

        last_memory = last_object.memory + f" {str(new_value)}"
        last_object.memory = last_memory

        last_object.save()

        last_rounds = len(self.get_memory())
        last_object.rounds = last_rounds

        last_object.save()

    def update_accuracy(self, user_value: int, bot_guess: int) -> float:
        """Updates and saves the new accuracy"""

        last_object = GuessNumber.objects.last()
        updated_accuracy = self.get_accuracy(user_value, bot_guess, last_object.rounds)

        last_object.accuracy = updated_accuracy
        last_object.save()

        return updated_accuracy

    def get_rounds(self) -> int:
        """Returns the number of played rounds"""

        return GuessNumber.objects.last().rounds

    def get_accuracy(self, user_value: int, bot_guess: int, rounds: int) -> float:
        """Retrieves the accuracy"""

        if rounds == 0:
            return 0

        if user_value == bot_guess:
            self.guessed_correctly += 1

        accuracy = round((self.guessed_correctly / rounds * 100), 2)

        return accuracy

    def reset(self) -> None:
        """Resets the number of rounds and accuracy"""

        last_object = GuessNumber.objects.last()

        last_object.memory = ""
        last_object.rounds = 0
        last_object.accuracy = 0.0
        self.guessed_correctly = 0 

        last_object.save()

    def is_expired(self, experation_time: int) -> True | False:
        """Check if the last object in the table is expired"""

        created = GuessNumber.objects.last().created
        now = datetime.now(timezone.utc)

        if now - created >= timedelta(minutes=experation_time): # pragma: no cover
            return True

        return False

    def __str__(self):
        return GuessNumber.objects.filter(created=self.created).first().created.__str__() # pragma: no cover


games_info = GuessNumber()
