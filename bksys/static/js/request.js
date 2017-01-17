function validateTime(time) {
    var arr = time.split(":");
    if (arr.length != 2) {
        return false;
    } else {
        if (isNaN(arr[0]) || isNaN(arr[1])) {
            return false;
        }
        if (arr[0] > 24 || arr[1] > 60 || arr[0] < 0 || arr[1] < 0) {
            return false;
        }
        if (arr[1].toString().length != 2) {
            return false;
        }
        if (arr[0].toString().length == 0) {
            return false;
        }
    }
    return true;
}

function performAJAX(url, dataType, data, callback) {
    $.ajax({
        type: 'POST',
        url: url,
        dataType: dataType,
        data: data,
        success: callback,
    });
    return false;
}

$("input[name=duration_radio]").click(function() {
    if (this.value == "userDuration") {
        $("input[name=durValue]").prop('disabled', false);
    } else {
        $("input[name=durValue]").val("");
        $("input[name=durValue]").prop('disabled', true);
    }
});

$('#booking_details').submit(function() {
    var event = $("#calendar").fullCalendar('clientEvents', "new_event")[0];
    var data = {
        'start': event.start.format("HH:mm:ss"),
        'end': event.end.format("HH:mm:ss"),
        'date': $("#calendar").fullCalendar('getDate').format("YYYY-MM-DD"),
    };
    data = $('#booking_details').serialize() + '&' + $.param(data);
    var callback = function(data){
        $('#showModal').html(data);
        $('#modal').modal('show');
    };  
    if ($('#booking_details').valid() == true) {
        performAJAX("/book_room/","html",data,callback);    
    }
    return false;
});

$('#findBookingForm').submit(function() {
    var callback = function(data){
        $('#result').html(data);
    };
    performAJAX('/findBooking/','html',$('#findBookingForm').serialize(),callback);
    return false;
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$('#cancelBooking').click(function() {
    $.ajax({
        type:'POST',
        url: "/checkIfRecurring/",
        dataType: 'html',
        data: {
            "id": booking_id,
        },
        success: function(data){
            if (data == "1"){
                $('#cancelBookingModal1').modal('show');
            } else {
                $('#cancelBookingModal').modal('show');
            }
        },
    });
    
});

$('#remAll,#remCurrent').click(function(){
    var deleteAll = false;
    if (this.id == "remAll"){
        deleteAll = true;
    }
    $.ajax({
        type: "POST",
        url: "/cancelBooking/",
        dataType: "html",
        data : {
            'id' : booking_id,
            'deleteAll':deleteAll,
        },
        success: function(data){
            if($('#cancelBookingModal1').is(':visible')){
                $('#modalText1').text(data);
                $('#remAll,#remCurrent').remove();
                $('#cancelBookingModal1').find("button#exit").text('Close');
            } else {
                $('#modalText').text(data);
                $('#remCurrent').remove();
                $('#cancelBookingModal').find("button#exit").text('Close');
            }
        }
    });
})

function getVAR(x) {
    var initial = $('#' + x).prop("defaultValue");
    var changed_val = $('#' + x).val();
    if (initial == changed_val) {
        return " ";
    } else {
        return changed_val;
    }
}

$('#update').click(function() {
        var booking_id = $('input[name=booking_id]').val();
        var booking = $("#calendar").fullCalendar('clientEvents', booking_id);
        var start= " ";
        var end = " ";
        var date = " ";
        var start = booking[0].start;
        if (start != undefined){
            start = booking[0].start.format("HH:mm:ss");
            date =  booking[0].start.format("YYYY-MM-DD");
            end = booking[0].end.format("HH:mm:ss");    
        } else {
            start = " ";
        }
        $.ajax({
            type: "POST",
            url: "/updateBooking/",
            dataType: "html",
            data: {
                "description":getVAR('description'),
                "contact":getVAR('contact'),
                "start":start,
                "end":end,
                "date":date,
                "booking_id": booking_id,    
            },
            success: function(data) {
                if ($('#viewBooking').valid() == true) {
                    $('#showUpdateBKModal').html(data);
                    $('#updatedBKModal').modal('show');
                }
            },
        });
        return false;
    });