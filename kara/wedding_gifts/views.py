from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, IntegerField, When
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, View
from django.views.generic.base import ContextMixin

from kara.base.views import PartialTemplateCreateView, PartialTemplateResponseMixin

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
