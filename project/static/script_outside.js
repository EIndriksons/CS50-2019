// registration form validation
$(function() {

    $.validator.setDefaults({
        errorClass : 'text-danger',
        highlight : function(element) {
            $(element)
                .closest('.form-group')
                .children('input')
                .addClass('is-invalid');
        },
        unhighlight : function(element) {
            $(element)
                .closest('.form-group')
                .children('input')
                .removeClass('is-invalid');
        }
    });

    $.validator.addMethod('strongPassword', function(value, element) {
        return this.optional(element)
            || value.length >= 8
            && /\d/.test(value)
            && /[a-z]/i.test(value);
    }, 'Your password must be at least 8 characters long and contain at least one character and one number')

    $('#register-form').validate({
        rules : {
            email : {
                required : true,
                email : true,
                remote : '/register_email_validation'
            },
            name : {
                required : true,
                nowhitespace : true,
                lettersonly : true
            },
            surname : {
                required : true,
                nowhitespace : true,
                lettersonly : true
            },
            password : {
                required : true,
                strongPassword : true
            },
            confirmpassword : {
                required : true,
                equalTo : '#password'
            }
        }
    });

});