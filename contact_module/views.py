from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView

from site_module.models import SiteSetting
from .forms import ContactForm


class ContactUsView(FormView):
    template_name = 'contact_module/contact_us.html'
    form_class = ContactForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, SiteSetting.load().contact_success_message)
        return redirect('contact_us')  # redirect after POST avoids double submits
