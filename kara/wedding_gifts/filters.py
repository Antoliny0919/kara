import django_filters
from django import forms


class GiftSearchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="iexact",
        widget=forms.TextInput(attrs={"placeholder": "Search"}),
    )
