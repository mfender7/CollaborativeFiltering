function makeConnection(socket_host, message, callback, clickEvent){
    /*
     * A class to make doing websocket requests much, erm, easier.
     * socket_url is the url of the websocket we will be communicating with
     * messages is an object containting a set of messages to be sent to the socket host
     */
    
    //create a websocket at the given url
    var response;
    var socket = new WebSocket(socket_host);

    socket.onopen = function(event) {
            socket.send(JSON.stringify(message));
    }

    socket.onmessage = function(event) {
        response = JSON.parse(event.data);
        socket.close();
        callback(response, clickEvent);
    }
}