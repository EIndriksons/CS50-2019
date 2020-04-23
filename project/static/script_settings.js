// form validation
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

    $('#settings-form').validate({
        rules : {
            email : {
                required : true,
                email : true
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
            personal_code : {
                digits : true,
                minlength : 11,
                maxlength : 11
            },
            password_new_1 : {
                strongPassword : true
            },
            password_new_2 : {
                equalTo : '#password_new_1'
            },
            inputBank : {
                lettersonly : true
            },
            inputBankCode : {
                bic : true
            },
            inputBankIBAN : {
                iban : true
            }
        }
    });

});

// add a new bank account
function bankSubmit() {
    // left ajax for example purposes (jquery post example after this)
    $.ajax({
        data : {
            bank_name : $('#inputBank').val(),
            bank_code : $('#inputBankCode').val(),
            bank_iban : $('#inputBankIBAN').val(),
            active : $('#inputBankActive').is(':checked')
        },
        type : 'POST',
        url : '/bank_add'
    })
    .done(function(data) {
        if (data.bank) {
            $('#bankContent').load(" #bankContent > *");
        }
        else {
            alert(data.text);
        }
    });
}

// delete bank account
function bankDelete(bankId) {
    let delConfirmation = confirm("Are you sure you want to delete this Bank Account?");
    if (delConfirmation) {
        $.post('/bank_delete', {bank_id : bankId}, function(data) {
        if (data.delete) {
            // load only #content children (this prevents creation of another table or div)
            $('#bankContent').load(" #bankContent > *");
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
    }
}

// change default bank account
function changeDefault(bankId) {
    let delConfirmation = confirm("Are you sure you want to change the default Bank Account?");
    if (delConfirmation) {
        $.post('/bank_default', {bank_id : bankId}, function(data) {
        if (data.default) {
            // load only #content children (this prevents creation of another table or div)
            $('#bankContent').load(" #bankContent > *");
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
    }
}