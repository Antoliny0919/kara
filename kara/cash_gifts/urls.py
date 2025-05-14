from django.urls import path

from . import views

urlpatterns = [
    path(
        "action/select/",
        views.CashGiftsRecordActionSelectView.as_view(),
        name="action_select",
    ),
    path(
        "repository/add/",
        views.AddCashGiftsRecordRepositoryView.as_view(),
        name="add_repository",
    ),
    path(
        "repository/<int:pk>/",
        views.CashGiftsRecordRepositoryView.as_view(),
        name="repository",
    ),
    path(
        "repository/<int:pk>/record/add/",
        views.CashGiftAddView.as_view(),
        name="add_cash_gift",
    ),
    path(
        "repository/<int:pk>/record/refresh/",
        views.RefreshCashGiftTableView.as_view(),
        name="refresh_cash_gift_table",
    ),
]
