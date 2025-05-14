from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import CashGiftsForm, CashGiftsRecordRepositoryForm
from .models import CashGifts, CashGiftsRecordRepository


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cash_gifts_form"] = CashGiftsForm()
        context["cash_gifts"] = self.object.cash_gift_records.all()
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        self.object = CashGiftsRecordRepository.objects.prefetch_related(
            "cash_gift_records"
        ).get(pk=pk)
        return self.object


class RefreshCashGiftTableView(ListView):
    model = CashGifts
    paginate_by = 10
    template_name = "cash_gifts/gifts_record_repository_detail.html"

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            partial_template_name = self.template_name + "#cash-gifts-section"
            objects = CashGifts.objects.filter(repository_id=self.kwargs.get("pk"))
            context["object"] = CashGiftsRecordRepository.objects.get(pk=1)
            context["cash_gifts"] = objects
            context["cash_gifts_form"] = CashGiftsForm()
            return render(self.request, partial_template_name, context)


class CashGiftAddView(CreateView):
    form_class = CashGiftsForm

    def form_valid(self, form):
        form.instance.repository_id = self.kwargs.get("pk")
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("refresh_cash_gift_table", args=(self.kwargs.get("pk"),))
