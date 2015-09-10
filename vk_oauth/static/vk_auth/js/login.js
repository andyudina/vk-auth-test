$( document ).ready(function() {
    $('#error-msg').hide();
    var fragment = window.location.hash.substr(1);
    if (fragment) {
        //very very dangerous!!
        $.ajax({url: '/login', type: "get", data: {fragment: fragment}}).done(function(data) {
            //alert(JSON.parse(data)['result']);
            if(JSON.parse(data)['result'] == true) {
                //alert('Its ok');
                window.location = "http://localhost:8000/logout";
            }
            else {
                $('#error-msg').show();
            }
        });
    }
});
