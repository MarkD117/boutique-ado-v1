// Get value of country field upon page load, and store in variable
let countrySelected = $('#id_default_country').val();
// If country selected is false, set color to light grey
if(!countrySelected) {
    $('#id_default_country').css('color', '#aab7c4');
};
// Capture change event
$('#id_default_country').change(function() {
    // Get value of box every time it changes
    countrySelected = $(this).val();
    // Determine proper color depending on the initial value
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});