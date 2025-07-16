from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.views.generic.base import View

from kara.base.tests.models import Fruit, Skill, Tag
from kara.base.views import (
    MultipleObjectMixin,
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


class SkillView(MultipleObjectMixin, View):
    model = None

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return context


class MultipleObjectMixinTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.skill = Skill.objects.create(name="fire", damage=30)
        cls.tag1 = Tag.objects.create(
            name="friend", description="my best friend", hex_color="#676767"
        )
        cls.tag2 = Tag.objects.create(
            name="health", description="health people", hex_color="#121212"
        )

    def setUp(self):
        self.factory = RequestFactory()

    def assertQueryEqual(self, queryset, *args):
        id_list_1 = list(queryset.values_list("id", flat=True))
        id_list_2 = [object.pk for object in args]
        self.assertEqual(id_list_1, id_list_2)

    def test_get_queryset(self):
        view = SkillView.as_view()
        request = RequestFactory().get("/fake-url/")
        view.request = request
        # Raise an error if either the queryset or the model is not set
        with self.assertRaises(ImproperlyConfigured):
            view(request)

        SkillView.model = Skill
        context = view(request)
        self.assertIn("skill_list", context)
        self.assertQueryEqual(context["skill_list"], self.skill)

        # Supports multiple models via list or tuple
        SkillView.model = [Skill, Tag]
        context = view(request)
        self.assertIn("skill_list", context)
        self.assertIn("tag_list", context)
        self.assertQueryEqual(context["skill_list"], self.skill)
        self.assertQueryEqual(context["tag_list"], self.tag1, self.tag2)

        SkillView.model = None
        SkillView.queryset = Tag.objects.filter(id=self.tag1.pk)
        context = view(request)
        self.assertIn("tag_list", context)
        self.assertQueryEqual(context["tag_list"], self.tag1)

        # Supports multiple queryset via list or tuple
        SkillView.queryset = (Skill.objects.all(), Tag.objects.filter(id=self.tag1.pk))
        context = view(request)
        self.assertIn("tag_list", context)
        self.assertIn("skill_list", context)
        self.assertQueryEqual(context["tag_list"], self.tag1)
        self.assertQueryEqual(context["skill_list"], self.skill)

    def test_get_context_object_name(self):
        SkillView.model = Skill
        view = SkillView.as_view()
        request = RequestFactory().get("/fake-url/")
        view.request = request
        context = view(request)
        self.assertIn("skill_list", context)
        SkillView.context_object_name = {
            Skill._meta.model_name: "skill_new_context_name"
        }
        context = view(request)
        self.assertIn("skill_new_context_name", context)
        self.assertQueryEqual(context["skill_new_context_name"], self.skill)

    def test_paginate_object(self):
        SkillView.model = Skill
        view = SkillView.as_view()
        request = RequestFactory().get("/fake-url/")
        view.request = request
        context = view(request)
        self.assertNotIn("skill_pagination", context)
        SkillView.paginate = {Skill._meta.model_name: {"list_per_page": 2}}
        context = view(request)
        self.assertIn("skill_list", context)
        self.assertIn("skill_list_pagination", context)
        pagination = context["skill_list_pagination"]
        self.assertTrue(isinstance(pagination, SkillView.pagination_class))

        # Pagination also supports multiple models and
        # uses context_object_name as part of the context key
        SkillView.queryset = [Skill.objects.all(), Tag.objects.filter(id=self.tag1.pk)]
        SkillView.context_object_name = {Skill._meta.model_name: "skill_c_name"}
        SkillView.paginate = {
            Skill._meta.model_name: {"list_per_page": 2},
            Tag._meta.model_name: {"list_per_page": 2, "page_kwarg": "tag_p"},
        }
        context = view(request)
        self.assertIn("skill_c_name_pagination", context)
        self.assertIn("tag_list_pagination", context)
