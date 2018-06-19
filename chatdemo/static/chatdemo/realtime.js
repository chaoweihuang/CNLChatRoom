$(function() {
    // When we're using HTTPS, use WSS too.
    $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);
    var to_focus = $("#message");
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/ws/");

    chatsock.onmessage = function(message) {

        if($("#no_messages").length) {
            $("#no_messages").remove();
        }

        var data = JSON.parse(message.data);
        if (data.type == "presence") {
            //update lurkers count
            lurkers = data.payload.lurkers;
            lurkers_ele = document.getElementById("lurkers-count");
            lurkers_ele.innerText = lurkers;

            //update logged in users list
            user_list = data.payload.members;
            document.getElementById("loggedin-users-count").innerText = user_list.length;
            user_list_obj = document.getElementById("user-list");
            user_list_obj.innerText = "";

            //alert(user_list);
            for(var i = 0; i < user_list.length; i++ ){
                var user_ele = document.createElement('li');
                user_ele.setAttribute('class', 'list-group-item list-group-item-action');
                user_ele.onclick = clickUserList;
                user_ele.innerText = user_list[i];
                user_list_obj.append(user_ele);
            }
            return;
        } else if (data.type == "chat") {
            if (($('#chat_room_name').text() == data.chat_room_name && $('#user_name').text() == data.user)
                || ($('#chat_room_name').text() == data.user && $('#user_name').text() == data.chat_room_name)
                || ($('#chat_room_name').text() == "Lobby" && data.chat_room_name == "Lobby")) {
                var chat = $("#chat")
                var ele = createMessage(data.user, data.message);
                alert(ele.innerText);
                chat.append(ele)
                $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);
            }
            return;
        } else if (data.type == "reload") {
            var chat = $("#chat")
            if ($('#chat_room_name').text() != data.chat_room_name) {
                alert("chat_room_name is wrong");
                return;
            }
            chat.empty();
            messages = data.messages;
            for(var i = 0; i < messages.length; i++) {
                var ele = createMessage(messages[i][0], messages[i][1]);
                chat.append(ele);
            }
            $('#last_message_id').text(data.first_message_id);
            if (data.first_message_id > 0) {
                $('#load_old_messages').removeClass('disabled');
            } else {
                $('#load_old_messages').addClass('disabled');
            }
            $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);
            return;
        }
    };

    $("#chatform").on("submit", function(event) {
        var message = {
            message: $('#message').val(),
            chat_room_name: $('#chat_room_name').text(),
            type: "chat"
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    setInterval(function() {
    chatsock.send(JSON.stringify("heartbeat"));
    }, 10000);

    function clickUserList() {
        $('#back_to_lobby').removeClass('active');
        $('#user-list').find('.active').removeClass('active');
        $('#chat_room_name').text($(this).text());
        $(this).addClass('active');

        var message = {
            message: "",
            chat_room_name: $('#chat_room_name').text(),
            type: "reload"
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    }

    function createMessage(username, message) {
        var ele = $('<li class="list-group-item"></li>')
        var btn = document.createElement('button');
        btn.setAttribute('class', 'btn btn-default btn-blacklist')
        btn.innerText = 'B';
        btn.onclick = clickBlackList;
        ele.append(btn);
        ele.append('<strong>'+username+'</strong> : ')
        ele.append(message)

        return ele;
    }

    function clickBlackList() {
        var message = {
            type: "black-list",
            blacked_user: $(this).parent().find('strong').text()
        }
        return false;
    }

    $('.list-group-item-action').click(clickUserList);

    $('.btn-blacklist').click(clickBlackList);
});
