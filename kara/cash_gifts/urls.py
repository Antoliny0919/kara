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
        "repository/<uuid:pk>/",
        views.CashGiftsRecordRepositoryDetailView.as_view(),
        name="repository",
    ),
    path(
        "repository/<uuid:pk>/record/add/",
        views.CashGiftAddView.as_view(),
        name="add_cash_gift",
    ),
]
