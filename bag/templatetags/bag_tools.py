from django import template


register = template.Library()

# Create template filter to calculate subtotal
@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    return price * quantity