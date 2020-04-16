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

// add new Form
function addForm() {
    $.get('/create_form', function(data) {
        if(data) {
            // load only #content children (this prevents creation of another table or div)
            $('#content').load(" #content > *");
        }
        else {
            alert('Failed to Create New Form. Please contact the Admin if this happens again.')
        }
    });
};

// add new Transaction to the Finance form
function addTransaction(financeId) {
    $.get('/finance/' + financeId + '/create_transaction', function(data) {
        if(data) {
            // load only #content children (this prevents creation of another table or div)
            $('#content').load(" #content > *");
        }
        else {
            alert('Failed to Create New Document. Please contact the Admin if this happens again.');
        }
    });
};

// submit Finance form
function mySubmit(financeId) {
    $.get('/finance/' + financeId + '/submit', function(data) {
       if(data.submit) {
           location.reload();
       }
       else {
           alert(data.text);
       }
    });
};

// submit Transaction
function myTransactionSubmit(financeId, transactionId) {
    $.get('/finance/' + financeId + '/' + transactionId + '/submit', function(data) {
       if(data.submit) {
           location.reload();
       }
       else {
           alert(data.text);
       }
    });
};

// delete Finance form
function myDelete(financeId) {
    let delConfirmation = confirm("Are you sure you want to delete this Form?");
    if (delConfirmation) {
        $.get('/finance/' + financeId + '/delete', function(data) {
            if (data.delete) {
                window.location = '/finance';
            }
            else {
                alert(data.text);
            }
        });
    }
};

// delete Transaction
function myTransactionDelete(financeId, transactionId) {
    let delConfirmation = confirm("Are you sure you want to delete this Transaction?");
    if (delConfirmation) {
        $.get('/finance/' + financeId + '/' + transactionId + '/delete', function(data) {
            if (data.delete) {
                // checks if the page contains #content object, if not, you must be doing this from transaction tab
                if ($('#content').length) {
                    // load only #content children (this prevents creation of another table or div)
                    $('#content').load(" #content > *");
                }
                else {
                    window.location = '/finance/' + financeId;
                }
            }
            else {
                alert(data.text);
            }
        });
    }
};