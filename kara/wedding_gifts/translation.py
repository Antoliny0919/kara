from django.utils.translation import gettext_lazy as _

# translation.py is provided for translation purposes.
# Add any values that need translation and are passed via variables.
# The added values will be recognized by makemessages command.
SECTION_HEADER_TRANSLATIONS = [
    _("Select Registry"),
    _(
        "Please select a repository before saving your record. "
        "Your saved records will be stored in the selected repository."
    ),
    _("Add Wedding Gift Record"),
    _("Record the wedding gifts you received."),
    _("My Registry"),
    _("View Records"),
]
