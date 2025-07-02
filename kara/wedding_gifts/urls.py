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
        "registry/<uuid:pk>/add/",
        views.GiftAddView.as_view(),
        name="add_gift",
    ),
    # The detail logic(PUT, PATCH, DELETE) will be provided at a later time.
    # path(
    #     "registry/<uuid:pk>/cash_gift/<int:pk>/",
    #     views.CashGiftView.as_view(),
    #     name="cash_gift_detail",
    # ),
    # path(
    #     "registry/uuid:pk/in_kind_gift/<int:pk>/",
    #     views.InKindGiftView.as_view(),
    #     name="in_kind_gift_detail",
    # ),
]
