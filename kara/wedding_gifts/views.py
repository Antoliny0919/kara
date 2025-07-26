from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Case,
    Count,
    F,
    IntegerField,
    OuterRef,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin

from kara.base.views import (
    PartialTemplateCreateView,
    PartialTemplateListView,
    PartialTemplateResponseMixin,
)

from .forms import CashGiftForm, InKindGiftForm, WeddingGiftRegistryForm
from .models import CashGift, InKindGift, WeddingGiftRegistry
from .tables import CashGiftTable, InKindGiftTable


class WeddingGiftRegistryActionSelectView(TemplateView):
    template_name = "wedding_gifts/wedding_gift_registry_action_select.html"


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


class MyRegistryDashboardView(LoginRequiredMixin, PartialTemplateListView):
    template_name = "wedding_gifts/my_registry_dashboard.html"
    paginate = {WeddingGiftRegistry._meta.model_name: {"list_per_page": 2}}
    context_object_name = {WeddingGiftRegistry._meta.model_name: "registries"}

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        cash_gift_cnt = Count("cash_gifts", distinct=True)
        in_kind_gift_cnt = Count("in_kind_gifts", distinct=True)
        self.queryset = [
            WeddingGiftRegistry.objects.filter(owner=user).annotate(
                cash_gift_cnt=cash_gift_cnt,
                in_kind_gift_cnt=in_kind_gift_cnt,
            )
        ]
        # Number of registries, total recorded cash, and number of in kind gifts
        self.my_wedding_gift_items_cnt = WeddingGiftRegistry.objects.filter(
            owner=user
        ).aggregate(
            my_registry_cnt=Count("id", distinct=True),
            my_cash_gift_cnt=cash_gift_cnt,
            my_in_kind_gift_cnt=in_kind_gift_cnt,
        )
        # Registry with the most recorded gifts
        self.top_gift_cnt_registry = (
            WeddingGiftRegistry.objects.filter(owner=user)
            .annotate(
                cash_gift_cnt=cash_gift_cnt,
                in_kind_gift_cnt=in_kind_gift_cnt,
                total_gift_cnt=F("cash_gift_cnt") + F("in_kind_gift_cnt"),
            )
            .order_by("-total_gift_cnt")
            .first()
        )
        # Registry with the highest received amount
        self.top_total_price_registry = (
            WeddingGiftRegistry.objects.filter(owner=user)
            .annotate(
                total_price=Coalesce(
                    Subquery(
                        CashGift.objects.filter(registry=OuterRef("pk"))
                        .values("registry")
                        .annotate(total=Sum("price"))
                        .values("total")[:1]
                    ),
                    Value(0),
                )
                + Coalesce(
                    Subquery(
                        InKindGift.objects.filter(registry=OuterRef("pk"))
                        .values("registry")
                        .annotate(total=Sum("price"))
                        .values("total")[:1]
                    ),
                    Value(0),
                )
            )
            .order_by("-total_price")
            .first()
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = {
            "top_gift_cnt_registry": self.top_gift_cnt_registry,
            "top_total_price_registry": self.top_total_price_registry,
        }
        context.update(extra_context)
        context.update(self.my_wedding_gift_items_cnt)
        return context


class WeddingGiftRegistryAddView(LoginRequiredMixin, CreateView):
    template_name = "wedding_gifts/registry_add.html"
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


class WeddingGiftRegistryDetailView(UpdateView):
    template_name = "wedding_gifts/registry_detail.html"
    form_class = WeddingGiftRegistryForm
    queryset = WeddingGiftRegistry.objects.all()

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("The wedding gift registry has been successfully updated!"),
        )
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registry = WeddingGiftRegistry.objects.filter(pk=self.object.pk)
        cash_gift_insight = registry.aggregate(
            cash_gift_cnt=Count("cash_gifts"),
            cash_gift_total_price=Coalesce(Sum("cash_gifts__price"), 0),
        )
        in_kind_gift_insight = registry.aggregate(
            in_kind_gift_cnt=Count("in_kind_gifts"),
            in_kind_gift_total_price=Coalesce(Sum("in_kind_gifts__price"), 0),
        )
        context.update(cash_gift_insight)
        context.update(in_kind_gift_insight)
        context["gift_total_price"] = (
            cash_gift_insight["cash_gift_total_price"]
            + in_kind_gift_insight["in_kind_gift_total_price"]
        )

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
        queryset = self.model[self.gift_type].objects.all().order_by("-id")
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
    template_name = "wedding_gifts/gift_insights.html"
