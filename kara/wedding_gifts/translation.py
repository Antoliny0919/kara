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
    _("Wedding Gift Records"),
    _(
        "View the wedding gift records and find the gifts you "
        "want by searching or using filters."
    ),
    _("View Insights"),
    _("Select a registry to view records."),
    _("Check out my wedding gift repositories and some fun insights"),
    _("My Wedding Gift Registries"),
]

LINK_BUTTON_TRANSLATIONS = [
    _("+ Add Registry"),
]

MY_WEDDING_GIFT_DASHBOARD_TRANSLATIONS = [
    _("My Wedding Gift Record Registries"),
    _("Clicking on a registry lets you view or edit its detailed information"),
    _("How many repositories and records have I added and written?"),
    _("Total number of repositories and gift records I have"),
    _("Wedding Gift Registry"),
    _("Cash Gift Record"),
    _("In Kind Gift Record"),
    _("Who received the most gifts?"),
    _("Recipient in the registry with the most recorded gifts"),
    _("Number of cash gift records"),
    _("Number of in kind gift records"),
    _("Who received the largest amount in gifts?"),
    _("Recipient of the registry with the highest total gift amount recorded"),
]

WEDDING_GIFT_REGISTRY_ADD = [
    _("Add Wedding Gift Record Registry"),
    _(
        "You can keep track of the wedding gifts you've received"
        " by adding a wedding gift registry! "
        "Try adding your wedding gift registry now"
    ),
]
