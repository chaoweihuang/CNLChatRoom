$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";

    var loadhistorysock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/loadhistory/");

    loadhistorysock.onmessage = function(message) {

        var data = JSON.parse(message.data);

        new_messages = data.messages

        last_id = data.previous_id

        if(last_id == -1){
            $("#load_old_messages").addClass('disabled');
            $("#last_message_id").text(last_id)
            if(new_messages.length == 0){
                return;
            }
        }
        else{
            $("#last_message_id").text(last_id)
        }

        var chat = $("#chat")

        for(var i=new_messages.length - 1; i>=0; i--){
            var ele = createMessage(new_messages[i]['user'], new_messages[i]['message']);
            chat.prepend(ele)
        }

    };

    function createMessage(username, message) {
        var ele = $('<li class="list-group-item"></li>')
        var btn = document.createElement('button');
        btn.setAttribute('class', 'btn btn-default btn-blacklist')
        btn.innerText = 'B';
        btn.onclick = clickBlackList;
        ele.append('<strong>'+data.user+'</strong> : ')
        ele.append(data.message)

        return ele;
    }

    function clickBlackList() {
        alert("blacked " + $(this).parent().find('strong').text());
        return false;
    }

    $("#load_old_messages").on("click", function(event) {
        var message = {
            last_message_id: $('#last_message_id').text(),
            chat_room_name: $('#chat_room_name').text()
        }
        loadhistorysock.send(JSON.stringify(message));
        return false;
    });
});
