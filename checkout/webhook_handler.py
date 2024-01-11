from django.http import HttpResponse


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
        print(intent)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)