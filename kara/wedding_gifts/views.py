from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, IntegerField, When
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, View
from django.views.generic.base import ContextMixin

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
        return self.object.get_absolute_url()


class GiftViewMixin(PartialTemplateResponseMixin):
    template_name = "wedding_gifts/wedding_gift_registry_detail.html"
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
        self.gift_type = gift_type or "cash"
        self.gift_data = self.gift_map[self.gift_type]
        self.registry_pk = self.kwargs.get(self.pk_url_kwarg)
        # Finds the related_name of the gift model associated with the registry.
        related_model = self.gift_data["model"]
        related_field = related_model._meta.get_field("registry")
        self.gift_related_name = related_field.remote_field.related_name
        return super().dispatch(request, *args, **kwargs)

    def get_gifts_data(self):
        """
        Returns the gifts to be passed to the table
        """
        gifts = self.queryset
        if isinstance(self.object, WeddingGiftRegistry):
            # Retrieves the related gift objects from the given registry
            # using the gift_related_name
            gifts = getattr(self.object, self.gift_related_name).all().order_by("-id")
        return gifts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gifts = self.get_gifts_data()
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
                "gift_table": table,
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
        context["gift_form"] = self.gift_data["form"]()
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


class MyWeddingGiftRegistryView(TemplateView):
    template_name = "wedding_gifts/my_wedding_gifts_registry.html"


class WeddingGiftRegistryContextMixin(ContextMixin):
    partial_template = ["registry-selector"]

    def dispatch(self, request, *args, **kwargs):
        htmx_target = self.request.headers.get("Hx-Target", None)
        if request.htmx and htmx_target in self.partial_template:
            self.template_name = "wedding_gifts/base.html"
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        current_registry = self.kwargs.get("pk")
        context = super().get_context_data(**kwargs)
        objects = (
            WeddingGiftRegistry.objects.filter(owner=self.request.user)
            .annotate(
                cash_gift_cnt=Count("cash_gifts", distinct=True),
                in_kind_gift_cnt=Count("in_kind_gifts", distinct=True),
                current_is_first=Case(
                    When(pk=current_registry, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
            )
            .order_by("current_is_first", "updated_at")
        )
        context["registries"] = objects
        return context


class GiftAddView(
    LoginRequiredMixin, WeddingGiftRegistryContextMixin, PartialTemplateCreateView
):
    template_name = "wedding_gifts/gift_add.html"
    form_name = "gift_form"
    forms = {
        "cash": CashGiftForm,
        "in_kind": InKindGiftForm,
    }

    def dispatch(self, request, *args, **kwargs):
        gift_type = self.request.GET.get("gift_type", None) or self.request.POST.get(
            "gift_type", None
        )
        self.gift_type = gift_type or "cash"
        self.form_class = self.forms[self.gift_type]
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.registry_id = self.kwargs.get("pk")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "gift_type": self.gift_type,
                "current_registry_pk": self.kwargs.get("pk"),
            }
        )
        return context


class GiftTableView(
    WeddingGiftRegistryContextMixin, PartialTemplateResponseMixin, View
):
    template_name = "wedding_gifts/gift_table.html"
    model = {
        "cash": CashGift,
        "in_kind": InKindGift,
    }
    table = {"cash": CashGiftTable, "in_kind": InKindGiftTable}

    def dispatch(self, request, *args, **kwargs):
        gift_type = self.request.GET.get("gift_type", None) or self.request.POST.get(
            "gift_type", None
        )
        self.gift_type = gift_type or "cash"
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model[self.gift_type].objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.table[self.gift_type](
            self.request,
            model=self.model[self.gift_type],
            base_queryset=self.get_queryset(),
            list_per_page=settings.WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE,
        )
        context["table"] = table
        context["gift_type"] = self.gift_type
        context["current_registry_pk"] = self.kwargs.get("pk")
        return context


class GiftInsightsView(TemplateView):
    tempalte_name = "wedding_gifts/gift_insights.html"
