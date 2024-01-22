from django.forms.widgets import ClearableFileInput
# Using "as _" means gettext_lazy() can be called using _()
from django.utils.translation import gettext_lazy as _


# Custom django widget used to beautify image selection on forms
class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'