from django.urls import path

from . import views

urlpatterns = [
    path(
        "action/select/",
        views.CashGiftsRecordActionSelectView.as_view(),
        name="action_select",
    )
]
