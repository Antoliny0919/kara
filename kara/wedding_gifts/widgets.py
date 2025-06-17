from kara.base.widgets import DropdownCheckboxSelectMultiple


class TagSelectWidget(DropdownCheckboxSelectMultiple):
    option_template_name = "wedding_gifts/widgets/tag_select_option.html"

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value:
            option["attrs"]["description"] = value.instance.description
            option["attrs"]["hex_color"] = value.instance.hex_color
        return option
