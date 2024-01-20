from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from bag.contexts import bag_contents

import stripe
import json

@require_POST
def cache_checkout_data(request):
    try:
        # Making POST request to this view and give it the client secret
        # from the payment intent. If we split it at the word secret,
        # the 1st part will be the 'Payment Intent Id'. This is then
        # stored in a variable called 'pid'
        pid = request.POST.get('client_secret').split('_secret')[0]
        # Set up stripe using secret key to modify the payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Give payment intent the pid and tell it what we want to modify.
        # In this case we are adding some metadata
        stripe.PaymentIntent.modify(pid, metadata={
            # Add json dump of users shopping bag
            'bag': json.dumps(request.session.get('bag', {})),
            # If they checked to save their information
            'save_info': request.POST.get('save_info'),
            # User placing the order
            'username': request.user,
        })
        return HttpResponse(status=200)
    # Error message if anything goes wrong
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)

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
            # commit=False prevents multiple save events
            # from being commited to the database
            order = order_form.save(commit=False)
            # Get payment id for this specific order
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            # Set original shopping bag on the model and dump
            # shopping bag to a json string and set on the order
            order.original_bag = json.dumps(bag)
            # save the order
            order.save()
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
                except Product.DoesNotExist:
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

        # If the user is authenticated, attempt to prefill the
        # form with any info the user maintains in their profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                # Use initial parameter on order form to
                # pre-fill all fields with relevant info
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            # If user is not authenticated, an empty form is rendered
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
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
    
    # User must be authenticated
    if request.user.is_authenticated:
        # Get users profile
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            # Create an instance of the user profile form, using the profile data
            # and telling it we're going to update the profile we've obtained above.
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()
    
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