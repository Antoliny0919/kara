from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from kara.base.utils import pascal_to_snake
from kara.base.views import (
    PartialTemplateCreateView,
    PartialTemplateDetailView,
    PartialTemplateResponseMixin,
)

from .forms import CashGiftForm, InKindGiftForm, WeddingGiftRegistryForm
from .models import CashGift, InKindGift, WeddingGiftRegistry
from .tables import CashGiftTable, InKindGiftTable


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


class GiftViewMixin(PartialTemplateResponseMixin):
    template_name = "wedding_gifts/wedding_gift_registry_detail.html"
    partial_template_identifier = "#gift-records-section"
    gift_map = {
        "cash": {
            "model": CashGift,
            "form": CashGiftForm,
            "table": CashGiftTable,
        },
        "in_kind": {
            "model": InKindGift,
            "form": InKindGiftForm,
            "table": InKindGiftTable,
        },
    }

    def get_gift_url_name(self):
        """
        Returns the URL that calls the `Gift` API.
        The URL name for the `Gift` API is expected to be the
        snake_case version of the model name.

        e.g. StockGift --> stock_gift
        """
        model = self.gift_data["model"]
        model_name = model.__name__
        url_name = pascal_to_snake(model_name)
        try:
            result_url = reverse(url_name, args=(self.registry_pk,))
        except NoReverseMatch:
            raise NoReverseMatch(
                "The URL name for the APIView of the `%s` model is expected"
                "to be the snake_case version of the model name."
                'Please register "%s" as the URL name.' % (model_name, result_url)
            )
        return result_url

    def dispatch(self, request, *args, **kwargs):
        gift_type = self.request.GET.get("gift_type", None) or self.request.POST.get(
            "gift_type", None
        )
        if request.method == "GET":
            if gift_type is None or (gift_type and len(dict(self.request.GET)) > 1):
                # If gift_type is missing from the query or
                # if multiple query parameters including gift_type are present,
                # only the table is partially updated.
                self.partial_template_identifier = "#gift-records-table-section"
        self.gift_type = gift_type or "cash"
        self.gift_data = self.gift_map[self.gift_type]
        self.registry_pk = self.kwargs.get(self.pk_url_kwarg)
        # Finds the related_name of the gift model associated with the registry.
        related_model = self.gift_data["model"]
        related_field = related_model._meta.get_field("registry")
        self.gift_related_name = related_field.remote_field.related_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.object, WeddingGiftRegistry):
            gifts = getattr(self.object, self.gift_related_name).all().order_by("-id")
        else:
            gifts = self.queryset
        table = self.gift_data["table"](
            self.request,
            model=self.gift_data["model"],
            base_queryset=gifts,
            list_per_page=settings.WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE,
        )
        gift_url = self.get_gift_url_name()
        context.update(
            {
                "gift_type": self.gift_type,
                "detail_registry_url": reverse(
                    "detail_registry", args=(self.registry_pk,)
                ),
                "table": table,
                "gift_url": gift_url,
            }
        )
        return context


class WeddingGiftRegistryDetailView(
    LoginRequiredMixin, GiftViewMixin, PartialTemplateDetailView
):
    def get_object(self, queryset=None):
        self.object = WeddingGiftRegistry.objects.prefetch_related(
            self.gift_related_name
        ).get(pk=self.kwargs.get(self.pk_url_kwarg))
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.htmx or (
            self.partial_template_identifier != "#gift-records-table-section"
        ):
            # Passes the form unless it's an HTML request or
            # a request that only returns the table template.
            form = self.gift_data["form"]()
            context.update({"gift_form": form})
        return context


class CashGiftView(GiftViewMixin, PartialTemplateCreateView):
    form_class = CashGiftForm
    queryset = CashGift.objects.all().order_by("-id")
    form_name = "gift_form"

    def reuse_form(self, form):
        # In `UnitNumberField`(price), the selected unit is reused.
        selected = form["price"].value()[0]
        initial = {"price": {"select": selected}}
        new_form = self.form_class(initial=initial)
        return new_form

    def form_valid(self, form):
        form.instance.registry_id = self.kwargs.get("pk")
        return super().form_valid(form)


class InKindGiftView(GiftViewMixin, PartialTemplateCreateView):
    form_class = InKindGiftForm
    queryset = InKindGift.objects.all().order_by("-id")
    form_name = "gift_form"

    def reuse_form(self, form):
        # In `UnitNumberField`(price), the selected unit is reused.
        selected = form["price"].value()[0]
        initial = {"price": {"select": selected}}
        new_form = self.form_class(initial=initial)
        return new_form

    def form_valid(self, form):
        form.instance.registry_id = self.kwargs.get("pk")
        return super().form_valid(form)
