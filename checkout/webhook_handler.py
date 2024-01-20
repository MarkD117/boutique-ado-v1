from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time
import stripe

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    # init method of the class is a setup method that's
    # called every time an instance of the class is created.
    def __init__(self, request):
        # Assigning request as an attribute of the class in
        # case we need to access any attributes of the request
        # coming from stripe.
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # Payment intent is saved in a key called event.data.object
        intent = event.data.object
        # Get info from intent metadata
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)

        # Clean the data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        # Profile set to None so we can still allow anonymous users to checkout
        profile = None
        username = intent.metadata.username
        # If the username is not 'AnonymousUser' the user is authenticated
        if username != 'AnonymousUser':
            # Get profile using username
            profile = UserProfile.objects.get(user__username=username)
            # If user has saved info box checked (from metadata)
            if save_info:
                # Update profile by adding shipping details as default delivery information
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()
        
        order_exists = False
        attempt = 1
        # While loop runs giving the webhook 5 attempts to
        # find the existing order, if it cannot find one
        # after 5 attempts, the order will be created
        # automatically by the webhook. This allows the
        # view time to submit the form and create the order.
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    # __iexact lookup field used to make data
                    # an exact match but case insensitive
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    # These items in the shopping details object
                    # are inside and address key (.address). This
                    # is for the webhook to deliver correctly
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
                
            except Order.DoesNotExist:
                # If order does not exist, attempt increments by 1.
                # Then pythons time module sleeps for 1 second
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                # Creating form to save using objects.create
                # using all the data from the payment intent
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    # Add user profile to created order to overwrite profile
                    # being set to None if the user was not logged in. This
                    # allows the webhook handler to create orders for users
                    # that are authenticated by attaching their profile and
                    # for anonymous users by setting that field to None.
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # bag is loaded from the json version in the
                # payment intent instead of from the session.
                # Code copied from checkout view.
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            # If anything goes wrong, the order will be deleted if
            # one was created and return 500 server error response
            # to Stripe. This will cause Stripe to automatically
            # try the webhook again later
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)