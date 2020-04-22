// assign form to the admin user
function myAssign(financeId) {
    $.post('/finance/admin_status_change', {financeId : financeId, change : 'assign'}, function(data) {
        if(data.assign) {
            // reload page on submission
            location.reload();
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}

// change form status
function myStatus(financeId, status) {
    $.post('/finance/admin_status_change', {financeId : financeId, change : 'status', status : status}, function(data) {
        if(data.status) {
            // reload page on submission
            location.reload();
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}

// change transaction status
function myTransactionStatus(financeId, transactionId, status) {
    $.post('/transaction/admin_status_change', {financeId : financeId, transactionId : transactionId, status : status}, function(data) {
        if(data.status) {
            // reload page on submission
            location.reload();
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}

// accept or deny users
function setUserStatus(userId, status) {
    $.post('/registration', {user_id : userId, status : status}, function(data) {
        if (data.status) {
            // load only #content children (this prevents creation of another table or div)
            $('#content').load(" #content > *");
        }
        else {
            // if failed - display error text
            alert(data.text);
        }
    });
}