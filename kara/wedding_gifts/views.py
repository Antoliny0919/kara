from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from kara.base.tables import Table
from kara.base.views import PartialTemplateCreateView, PartialTemplateDetailView

from .forms import CashGiftForm, WeddingGiftRegistryForm
from .models import CashGift, WeddingGiftRegistry


class WeddingGiftRegistryActionSelectView(TemplateView):
    template_name = "wedding_gifts/wedding_gift_registry_action_select.html"


class AddWeddingGiftRegistryView(LoginRequiredMixin, CreateView):
    template_name = "wedding_gifts/wedding_gift_registry_add.html"
    form_class = WeddingGiftRegistryForm

    def form_valid(self, form):
        form.instance.owner_id = self.request.user.pk
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _(
                "The wedding gift registry has been added. "
                "Go ahead and record the gifts you've received!"
            ),
        )
        return reverse("detail_registry", args=(self.object.pk,))


class WeddingGiftRegistryDetailView(LoginRequiredMixin, PartialTemplateDetailView):
    template_name = "wedding_gifts/wedding_gift_registry_detail.html"
    partial_template_identifier = "#gift-records-section"

    def add_form_to_context(self, context):
        if not (self.request.htmx and self.request.GET):
            # Add `CashGiftForm` to the context unless it's an HTMX GET request.
            context["cash_gift_form"] = CashGiftForm()

    def get_template_names(self):
        if self.request.htmx and self.request.GET:
            # Only render the table for HTMX GET requests
            self.partial_template_identifier = "#gifts-table"
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_form_to_context(context)
        cash_gifts = self.object.cash_gifts.all().order_by("-id")
        table = Table(
            self.request,
            model=CashGift,
            base_queryset=cash_gifts,
            list_per_page=settings.WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE,
        )
        context["table"] = table
        return context

    def get_object(self, queryset=None):
        self.object = WeddingGiftRegistry.objects.prefetch_related("cash_gifts").get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )
        return self.object


class CashGiftAddView(PartialTemplateCreateView):
    form_class = CashGiftForm
    template_name = "wedding_gifts/wedding_gift_registry_detail.html"
    partial_template_identifier = "#gift-records-section"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = WeddingGiftRegistry.objects.prefetch_related("cash_gifts").get(
            pk=self.kwargs.get("pk")
        )
        cash_gifts = object.cash_gifts.all().order_by("-id")
        table = Table(
            self.request,
            model=CashGift,
            base_queryset=cash_gifts,
            list_per_page=settings.WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE,
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
        form.instance.registry_id = self.kwargs.get("pk")
        return super().form_valid(form)
