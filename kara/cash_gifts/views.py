from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView
from django.views.generic.detail import DetailView

from .forms import CashGiftsRecordRepositoryForm
from .models import CashGiftsRecordRepository


class CashGiftsRecordActionSelectView(TemplateView):
    template_name = "cash_gifts/gifts_record_action_select.html"


class AddCashGiftsRecordRepositoryView(LoginRequiredMixin, CreateView):
    template_name = "cash_gifts/gifts_record_repository_add.html"
    form_class = CashGiftsRecordRepositoryForm

    def form_valid(self, form):
        form.instance.owner_id = self.request.user.pk
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _(
                "The cash gifts record repository has been added. "
                "Go ahead and record the gifts you've received!"
            ),
        )
        return reverse("repository", args=(self.object.pk,))


class CashGiftsRecordRepositoryView(LoginRequiredMixin, DetailView):
    template_name = "cash_gifts/gifts_record_repository_detail.html"
    model = CashGiftsRecordRepository
