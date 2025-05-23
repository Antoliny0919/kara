from django.urls import path

from . import views

urlpatterns = [
    path(
        "registry/action/select/",
        views.WeddingGiftRegistryActionSelectView.as_view(),
        name="registry_action_select",
    ),
    path(
        "registry/add/",
        views.AddWeddingGiftRegistryView.as_view(),
        name="add_registry",
    ),
    path(
        "registry/<uuid:pk>/",
        views.WeddingGiftRegistryDetailView.as_view(),
        name="detail_registry",
    ),
    path(
        "registry/<uuid:pk>/cash_gift/add/",
        views.CashGiftAddView.as_view(),
        name="add_cash_gift",
    ),
]
