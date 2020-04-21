// assign Form to the admin user
function myAssign(financeId) {
    $.get('/finance/' + financeId + '/status/assign', function(data) {
       if(data.assign) {
           location.reload();
       }
       else {
           alert(data.text);
       }
    });
};

// change Form status
function myStatus(financeId) {
    $.get('/finance/' + financeId + '/status/' + status, function(data) {
       if(data.status) {
           location.reload();
       }
       else {
           alert(data.text);
       }
    });
};

// change Transaction status
function myTransactionStatus(financeId, transactionId, status) {
    $.get('/finance/' + financeId + '/' + transactionId + '/status/' + status, function(data) {
       if(data.status) {
           location.reload();
       }
       else {
           alert(data.text);
       }
    });
}

// accept or deny users
function setUserStatus(userId, status) {
    $.post('/registration', {user_id : userId, status : status}, function(data) {
        if (data.status) {
            $('#content').load(" #content > *");
        }
        else {
            alert(data.text);
        }
    });
}