from django import forms
from django.test import TestCase

from kara.base.tests.models import Comment, Tag
from kara.wedding_gifts.widgets import TagSelectWidget


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["title", "author", "content", "tags"]
        widgets = {"tags": TagSelectWidget()}


class TagSelectWidgetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tags_data = [
            (
                {
                    "name": "Django",
                    "description": (
                        "The Web framework for perfectionists with deadlines."
                    ),
                    "hex_color": "#787878",
                }
            ),
            (
                {
                    "name": "React",
                    "description": "The library for web and native user interfaces.",
                    "hex_color": "#24C5C8",
                }
            ),
            (
                {
                    "name": "Rails",
                    "description": "Ruby on rails",
                    "hex_color": "#E32727",
                }
            ),
        ]
        for tag_data in cls.tags_data:
            Tag.objects.create(**tag_data)
        tags = Tag.objects.all()
        cls.comment = Comment.objects.create(
            title="My Favorite Skill",
            author="Dan Brian",
            content="My Favoriet Skill is ...",
        )
        cls.comment.tags.set(list(tags.values_list("id", flat=True)))

    def test_template_render(self):
        form = CommentForm(instance=self.comment)
        tag_render = str(form["tags"])
        self.assertIn(
            '<span class="color" style="background-color: #E32727"></span>', tag_render
        )
        self.assertIn("<div>Rails</div>", tag_render)
        self.assertIn("<div>Ruby on rails</div>", tag_render)

    def test_widget_options(self):
        expected = [
            {k: v for k, v in tag_data.items() if k != "name"}
            for tag_data in self.tags_data
        ]
        form = CommentForm(instance=self.comment)
        widget = form["tags"].field.widget
        optgroups = widget.optgroups(name="tags", value=[])
        for index, option in enumerate(optgroups):
            with self.subTest(option=option):
                # The 'attrs' must contain the 'description' and 'hex_color'
                # field values.
                attrs = option[1][0]["attrs"]
            self.assertDictEqual(attrs, expected[index])
