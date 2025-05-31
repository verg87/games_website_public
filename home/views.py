from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class HomePage(TemplateView):
    template_name = "home.html"

    def post(self, request):
        return render(request, self.template_name)

    def get(self, request):
        return render(request, self.template_name)
