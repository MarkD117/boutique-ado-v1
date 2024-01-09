from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    # Prevents manually entering checkout url
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        # Putting form data into dictionary.
        # Done manually in order to skip the save infobox
        # which doesn't have a field on the order model.
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # Create instance of the order form using the form data
        order_form = OrderForm(form_data)
        # Save form if valid
        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    # Get product id out of bag
                    product = Product.objects.get(id=item_id)
                    # If the items value is an integer, then we are
                    # working with an item that does not have sizes
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            # No size sets the quantity to the item_data
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # else, we are working with an item that does have sizes
                    else:
                        # Iterate through each size and
                        # create a line item accordingly
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # This should generally never happen, but If a product isnt found, 
                # an error message is displayed, the empty order will be deleted,
                # and the user will be returned to the shopping bag page.
                except Prodcuct.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            
            # checking if the user requested to save their information
            request.session['save_info'] = 'save-info' in request.POST
            # redirect to a new url called 'checkout_success' with the order number passed as an argument
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            # If the form is not valid an error message is shown
            # and the user will be sent back to the checkout page
            # at the botton of this view with the form errors shown.
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        # Prevents manually entering checkout url
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # Checks if user wants to save their information
    save_info = request.session.get('save_info')
    # Gets order number created in previous view to send to the template
    order = get_object_or_404(Order, order_number=order_number)
    # Attach a success message letting the user know their order number
    # and that an email will be sent to the email they put in the form.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    
    # Delete the users shopping bag from the current session
    if 'bag' in request.session:
        del request.session['bag']
    
    # Set the template and the context
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    # Render the template
    return render(request, template, context)