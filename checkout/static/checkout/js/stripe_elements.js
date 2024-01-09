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
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// Create stripe variable usinnng strip public key
var stripe = Stripe(stripePublicKey);
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

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    // Error displayed as html in card error div
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textcontent = ''
    }
})

// Handle form submit
// Get payment form
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Prevent default action of POST
    ev.preventDefault();
    // Disabling card element and submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // Toggles payment form out and loading overlay in
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    // stripe.confirmCardPayment() method sends card info securely to stripe
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    // Once card info has been sent, then, this function executes
    }).then(function(result) {
        // Checking for error and diplaying message
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            // Toggles payment form back in and loading overlay out
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            // Re-enable card element and sumbit button
            // Allows user to fix error
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        // If there are no errors, set status to succeeded and submit form
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});