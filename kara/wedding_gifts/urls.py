from django.urls import path

from . import views

urlpatterns = [
    path(
        "registry/action/select/",
        views.WeddingGiftRegistryActionSelectView.as_view(),
        name="registry_action_select",
    ),
    path(
        "registry/",
        views.MyWeddingGiftRegistryView.as_view(),
        name="my_registry",
    ),
    path(
        "registry/add/",
        views.AddWeddingGiftRegistryView.as_view(),
        name="add_registry",
    ),
    path(
        "registry/<uuid:pk>/gift/add/",
        views.GiftAddView.as_view(),
        name="add_gift",
    ),
    path(
        "registry/<uuid:pk>/gift/table/",
        views.GiftTableView.as_view(),
        name="gift_table",
    ),
    path(
        "registry/<uuid:pk>/gift/insight/",
        views.GiftInsightsView.as_view(),
        name="gift_insight",
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
