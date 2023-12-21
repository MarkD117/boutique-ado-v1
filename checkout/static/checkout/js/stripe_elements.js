/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

/*
    getting 'public key' and 'client secret' from template slicing off
    the first and last character of each removing the quotation marks
*/
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);
// Create stripe variable usinnng strip public key
var stripe = Stripe(stripe_public_key);
// Create and instance of strip elements
var elements = stripe.elements();
// Basic styles for the card
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// Create card element
var card = elements.create('card', {style: style});
// Mount card element to div
card.mount('#card-element');