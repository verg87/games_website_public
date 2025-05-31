from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import GuessNumber, games_info
from .forms import GuessNumGame


class GuessNumView(LoginRequiredMixin, FormView):
    template_name = "guess_number.html"
    form_class = GuessNumGame
    model = GuessNumber

    def form_valid(self, form: GuessNumGame) -> HttpResponse:
        user_value = form.cleaned_data["user_input"]

        initial_bot_guess = form.guess_num([])
        object = games_info.get_object(user_value, initial_bot_guess)
        
        games_info.update_table(object, user_value)

        rounds = games_info.get_rounds()
        memory = games_info.get_memory()
        bot_guess = form.guess_num(memory)
        accuracy = games_info.update_accuracy(user_value, bot_guess)

        form = GuessNumGame

        context = {
            "form": form,
            "bot_guess": bot_guess,
            "rounds": rounds,
            "accuracy": accuracy,
        }

        return self.render_to_response(self.get_context_data(**context))

    def form_invalid(self, form: GuessNumGame) -> HttpResponse:

        if "reset_button" in self.request.POST:
            games_info.reset()

        elif "back" in self.request.POST:
            return redirect(reverse("home"))

        return self.render_to_response(self.get_context_data(form=form))
        # Same thing as
        # return render(self.request, self.template_name, {"form": form})
