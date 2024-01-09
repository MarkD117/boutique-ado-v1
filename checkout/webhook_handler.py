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
            content=f'Webhook received: {event["type"]}',
            status=200)