var popup_msg = function(msg, callback){
    // popup message use modal show.
};

$(document).ready(function(){
    // ajax csrf protect.
    // html header include <meta name="csrf-token" content="{{csrf_token()}}">
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajaxSetup({
        // catch and handle ajax method exception.
        error: function(request, status, error){
            if (request.status === 401) {
                // unauthorized
                alert('Unauthorized user! Please login.');
                window.location = '/login';
            } else {
                alert(error);
            }
        }
    });
});