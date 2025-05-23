from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from kara.base.tables import Table
from kara.base.views import PartialTemplateCreateView, PartialTemplateDetailView

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


class CashGiftsRecordRepositoryDetailView(
    LoginRequiredMixin, PartialTemplateDetailView
):
    template_name = "cash_gifts/gifts_record_repository_detail.html"
    partial_template_identifier = "#cash-gifts-section"

    def add_form_to_context(self, context):
        if not (self.request.htmx and self.request.GET):
            # Add `CashGiftsForm` to the context unless it's an HTMX GET request.
            context["cash_gifts_form"] = CashGiftsForm()

    def get_template_names(self):
        if self.request.htmx and self.request.GET:
            # Only render the table for HTMX GET requests
            self.partial_template_identifier = "#cash-gifts-table"
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_form_to_context(context)
        cash_gift_records = self.object.cash_gift_records.all().order_by("-id")
        table = Table(
            self.request,
            model=CashGifts,
            base_queryset=cash_gift_records,
            list_per_page=settings.CASH_GIFT_TABLE_LIST_PER_PAGE,
        )
        context["table"] = table
        return context

    def get_object(self, queryset=None):
        self.object = CashGiftsRecordRepository.objects.prefetch_related(
            "cash_gift_records"
        ).get(pk=self.kwargs.get(self.pk_url_kwarg))
        return self.object


class CashGiftAddView(PartialTemplateCreateView):
    form_class = CashGiftsForm
    template_name = "cash_gifts/gifts_record_repository_detail.html"
    partial_template_identifier = "#cash-gifts-section"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = CashGiftsRecordRepository.objects.prefetch_related(
            "cash_gift_records"
        ).get(pk=self.kwargs.get("pk"))
        cash_gift_records = object.cash_gift_records.all().order_by("-id")
        table = Table(
            self.request,
            model=CashGifts,
            base_queryset=cash_gift_records,
            list_per_page=settings.CASH_GIFT_TABLE_LIST_PER_PAGE,
        )
        context["object"] = object
        context["table"] = table
        return context

    def reuse_form(self, form):
        # In `UnitNumberField`(price), the selected unit is reused.
        selected = form["price"].value()[0]
        initial = {"price": {"select": selected}}
        new_form = self.form_class(initial=initial)
        return new_form

    def form_valid(self, form):
        form.instance.repository_id = self.kwargs.get("pk")
        return super().form_valid(form)
