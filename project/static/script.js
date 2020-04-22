// make table rows clickable
$(document).ready(function() {
    // using .on() to make sure the contents get selected even after partly reload
    $(document).on('click', '#content tbody tr', function(e) {
        // filtering off buttons so that it would not go to link when you press a button inside table row
        if (!$(e.target).is('button')) {
            // find table row link and go to it
            window.location = $(this).find('a').attr('href');
        }
    });
});

// add new finance form
function addForm() {
    $.post('/finance', {data : 'create_form'}, function(data) {
        if(data.form) {
            // load only #content children (this prevents creation of another table or div)
            $('#content').load(" #content > *");

            // go to the new form in new window
            window.open('/finance/' + data.link);
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}

// add new Transaction to the Finance form
function addTransaction(financeId) {
    $.post('/finance/create_transaction', {financeId : financeId}, function(data) {
       if(data.insert) {
            // load only #content children (this prevents creation of another table or div)
            $('#content').load(" #content > *");

            // go to the new transaction in new window
            window.open('/finance/' + financeId + '/' + data.link);
       }
       else {
           // if failed - display error text
            alert(data.text);
       }
    });
}

// submit finance form
function mySubmit(financeId) {
    $.post('/finance/user_status_change', {financeId : financeId, change : 'submit'}, function(data) {
        if(data.submit) {
            // reload page on submission
            location.reload();
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}

// delete finance form
function myDelete(financeId) {
    // deletion confirmation pop-up
    let delConfirmation = confirm("Are you sure you want to delete this Form?");
    if (delConfirmation) {
        $.post('/finance/user_status_change', {financeId : financeId, change : 'delete'}, function(data) {
            if (data.delete) {
                // go back to finance list page
                window.location = '/finance';
            }
            else {
                // if failed - display error text
                alert(data.text);
            }
        });
    }
}


// submit transaction
function myTransactionSubmit(financeId, transactionId) {
    $.post('/transaction/user_status_change', {financeId : financeId, transactionId : transactionId, change : 'submit'}, function(data) {
        if(data.submit) {
            // reload page on submission
            location.reload();
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}



// delete transaction
function myTransactionDelete(financeId, transactionId) {
    // deletion confirmation pop-up
    let delConfirmation = confirm("Are you sure you want to delete this Transaction?");
    if (delConfirmation) {
        $.post('/transaction/user_status_change', {financeId : financeId, transactionId : transactionId, change : 'delete'}, function(data) {
            if (data.delete) {
                // checks if the page contains #content object, if not, you must be doing this from transaction window
                if ($('#content').length) {
                    // load only #content children (this prevents creation of another table or div)
                    $('#content').load(" #content > *");
                }
                else {
                    // else go back to finance form page
                    window.location = '/finance/' + financeId;
                }
            }
            else {
                // if failed - display error text
                alert(data.text);
            }
        });
    }
}