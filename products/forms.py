from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category

# Product form class that extents the model form
class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        # Dunder string used to include all the strings
        fields = '__all__'

    # Replace image field on form to use custom image widget
    image = forms.ImageField(label='Image', required=False, widget= CustomClearableFileInput)

    # Override init method to make changes to the fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get all categories
        categories = Category.objects.all()
        # Use a list comprehension to create a list of tuples of
        # the friendly names associated with their category id's.
        # List comprehension is shorthand for loop used to add items to a list.
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Update category field on the form to
        # use friendly names instead of id's.
        self.fields['category'].choices = friendly_names
        # Iterate through the fields and set classes
        # to match the theme of the rest of site.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'