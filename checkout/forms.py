from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # Overriding init method of form
        super().__init__(*args, **kwargs)
        # creating dictionary of custom placeholders
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        # Autofocus set to true makes cursor start in full name field
        self.fields['full_name'].widget.attrs['autofocus'] = True
        # Iterates through form fields adding a '*' to the
        # placeholder if it a required field on the model
        for field in self.fields:
            # country field asterisk is set on model. This if statement
            # prevents the below code from throwing an error as it will
            # not find the required country field key in the above dictionary
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                # Sets all placeholders to values in dictionary above
                self.fields[field].widget.attrs['placeholder'] = placeholder
            # Adds custom css class
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            # Remove form field labels as custom placeholders are set
            self.fields[field].label = False
