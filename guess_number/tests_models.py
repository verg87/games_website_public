from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import GuessNumber, games_info


class GuessNumberTests(TestCase):

    path = "/guess_the_number/"
    view_name = "comp-guesses-num"
    template = "guess_number.html"

    username = "testuser"
    password = "some12psw23"

    ctx_var = ["user_input"]
    ctx_results = ["bot_guess", "rounds", "accuracy"]


    model = GuessNumber
    client = Client

    def setUp(self):
        """Set up for all methods below"""

        User = get_user_model()
        User.objects.create_user(username=self.username, password=self.password)

        self.client.login(username=self.username, password=self.password)

    def test_get_memory_with_objects(self):
        """Check for get_memory to retrieve memory as a list"""

        self.model.objects.create(rounds=1, accuracy=0, memory="12")
        self.assertTrue(self.model.objects.exists())

        result = self.model.get_memory(self.model)

        self.assertEqual(result, [12])

    def test_get_memory_without_objects(self):
        """Check for get_memory to return an empty list if there are no objects"""

        self.assertFalse(self.model.objects.exists())

        result = self.model.get_memory(self.model)

        self.assertEqual(result, [])

    def test_get_object_not_exists(self):
        """Check whether get_object will create a new object if there's none in the table"""

        self.assertFalse(self.model.objects.exists())
        obj_guess_correct = self.model.get_object(self.model, 12, 12)

        self.assertEqual(obj_guess_correct.rounds, 1)
        self.assertEqual(obj_guess_correct.accuracy, 100)
        self.assertEqual(obj_guess_correct.memory, '12')

    def test_get_object_incorrect_guess(self):
        """Check whether get_object evaluates accuracy correctly"""

        self.assertFalse(self.model.objects.exists())
        obj_guess_incorrect = self.model.get_object(self.model, 12, 13)

        self.assertEqual(obj_guess_incorrect.rounds, 1)
        self.assertEqual(obj_guess_incorrect.accuracy, 0)
        self.assertEqual(obj_guess_incorrect.memory, '12')

    def test_update_table(self):
        """Check for update_table to update the fields properly"""

        self.model.objects.create(rounds=1, accuracy=0, memory="12")
        self.assertTrue(self.model.objects.exists())

        last_object = self.model.objects.last()
        # TODO decide between instance = GuessNumber() and model = GuessNumber

        games_info.update_table(last_object, 13)

        self.assertEqual(last_object.rounds, 2)
        self.assertTrue(last_object.accuracy == 0 or last_object.accuracy == 50)
        self.assertEqual(last_object.memory, "12 13")

    def test_update_accuracy(self):
        """Test update_accuracy for updating the accuracy"""

        self.model.guessed_correctly = 0
        self.model.objects.create(rounds=1, memory=12, accuracy=0)
        games_info.update_table(self.model.objects.last(), 13)

        updated_accuracy = games_info.update_accuracy(13, 13)

        self.assertEqual(updated_accuracy, 50)
        # TODO make guessed_correctly a model field

    def test_get_rounds(self):
        """Check if get_rounds method will actually return correct rounds"""

        self.model.objects.create(rounds=1, memory=12, accuracy=0)

        rounds = self.model.get_rounds(self.model)

        self.assertEqual(rounds, 1)

    def test_get_accuracy(self):
        """Check if get_accuracy method works as expected"""

        self.model.guessed_correctly = 0
        result_correct_guess = self.model.get_accuracy(self.model, 12, 12, 1)

        self.assertEqual(result_correct_guess, 100)
        self.assertEqual(self.model.guessed_correctly, 1)

        self.model.guessed_correctly = 0
        result_incorrect_guess = self.model.get_accuracy(self.model, 13, 12, 1)

        self.assertEqual(result_incorrect_guess, 0)
        self.assertEqual(self.model.guessed_correctly, 0)

        self.model.guessed_correctly = 0
        result_no_rounds = self.model.get_accuracy(self.model, 12, 12, 0)

        self.assertEqual(result_no_rounds, 0)

    def test_reset(self):
        """Test the reset for zeroing out the fields"""

        self.client.post(self.path, {self.ctx_var[0]: 20})

        response = self.client.post(self.path, {"reset_button": ""})

        self.assertFalse(
            all([result in response.context for result in self.ctx_results])
        )

        last_object = self.model.objects.last()

        self.assertEqual(last_object.rounds, 0)
        self.assertEqual(last_object.accuracy, 0.0)
        self.assertEqual(last_object.memory, "")
        self.assertEqual(self.model.guessed_correctly, 0)
