// form validation
bootstrapValidate('#personal_code', 'regex:^.{11}$:Personal code should be 11 digits|integer:Personal code should only contain digits and not include characters like the hyphen ("-")');
bootstrapValidate('#email', 'email:Please input a correct e-mail address');

// todo CHANGE TO jquery POST

// add a new bank account
function bankSubmit() {
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
            $('#bankContent').load(" #bankContent > *");
        }
        else {
            alert(data.text);
        }
    });
    }
}
