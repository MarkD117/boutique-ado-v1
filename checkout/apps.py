from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    # Lets django know there is a new signals module with some listeners in
    # it by overriding the ready method and importing our signals module.
    def ready(self):
        import checkout.signals