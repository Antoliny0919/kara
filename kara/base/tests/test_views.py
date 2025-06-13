from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.test import RequestFactory, SimpleTestCase, TestCase

from kara.base.tests.models import Fruit
from kara.base.views import (
    PartialTemplateFormMixin,
    PartialTemplateModelFormMixin,
    PartialTemplateResponseMixin,
)


class MoneyView(PartialTemplateResponseMixin):
    template_name = "test/template_money.html"


class DogView(PartialTemplateResponseMixin):
    pass


class PartialTemplateResponseMixinTests(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = MoneyView()

    def test_get_template_name(self):
        request = self.factory.get("/fake-url/")
        request.htmx = False
        self.view.request = request
        self.assertEqual("test/template_money.html", self.view.get_template_names()[0])
        request = self.factory.get("/fake-url/", HTTP_HX_TARGET="partial_test")
        request.htmx = True
        self.view.request = request
        self.assertEqual(
            "test/template_money.html#partial_test", self.view.get_template_names()[0]
        )

    def test_get_template_name_error(self):
        request = self.factory.get("/fake-url/")
        request.htmx = True
        self.view.request = request
        cases = ["", "test/template_dog.html"]
        for template_name in cases:
            with self.subTest(template_name=template_name):
                self.view.template_name = [template_name]
                with self.assertRaises(ImproperlyConfigured) as error:
                    self.view.get_template_names()
                self.assertEqual(
                    str(error.exception),
                    "PartialTemplateResponseMixin requires 'template_name' "
                    "to be defined and the request must include an 'Hx-Target' header.",
                )


class CakeForm(forms.Form):
    name = forms.CharField()


class CheeseCakeForm(forms.Form):
    name = forms.CharField()


class CakeView(PartialTemplateFormMixin, PartialTemplateResponseMixin):
    form_class = CakeForm
    template_name = "test/template_cake.html"


class CheeseCakeView(PartialTemplateFormMixin):
    form_class = CakeForm
    form_name = "cheese_cake_form"


class PartialTemplateFormMixinTests(SimpleTestCase):

    def test_form_name(self):
        view = CakeView()
        self.assertEqual(view.form_name, "cake_form")
        view = CheeseCakeView()
        self.assertEqual(view.form_name, "cheese_cake_form")

    def test_context_data(self):
        view = CakeView()
        context = view.get_context_data()
        self.assertIn("cake_form", context)
        view = CheeseCakeView()
        context = view.get_context_data(**{"cheese_cake_form": CakeForm()})
        self.assertIn("cheese_cake_form", context)
        self.assertTrue(isinstance(context["cheese_cake_form"], CakeForm))

    def test_form_invalid(self):
        view = CakeView()
        request = RequestFactory().get("/fake-url/")
        view.request = request
        view.request.htmx = False
        form = CheeseCakeForm()
        response = view.form_invalid(form)
        self.assertTrue(isinstance(response, TemplateResponse))


class FruitForm(forms.ModelForm):

    class Meta:
        model = Fruit
        fields = ["name", "price", "expiration_date"]


class FruitView(PartialTemplateModelFormMixin, PartialTemplateResponseMixin):
    form_class = FruitForm
    template_name = "test/template_fruit.html"

    def reuse_form(self, form):
        name = form.cleaned_data["name"]
        new_form = self.form_class(initial={"name": name})
        return new_form


class PartialTemplateModelFormMixinTests(TestCase):

    def test_reuse_form(self):
        form = FruitForm(
            data={"name": "mango", "price": 1000, "expiration_date": "2000-01-01"}
        )
        form.is_valid()
        view = FruitView()
        request = RequestFactory().get("/fake-url/")
        view.request = request
        view.request.htmx = False
        response = view.form_valid(form)
        context_form = response.context_data["fruit_form"]
        self.assertTrue(isinstance(context_form, FruitForm))
        self.assertFalse(context_form.is_bound)
        self.assertDictEqual(context_form.initial, {"name": "mango"})
