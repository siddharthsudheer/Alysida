// $(document).ready(function() {
//     // Use a "/test" namespace.
//     // An application can open a connection on multiple namespaces, and
//     // Socket.IO will multiplex all those connections on a single
//     // physical channel. If you don't care about multiple channels, you
//     // can set the namespace to an empty string.
//     namespace = '/test';
//     // var io = require('socket.io')(server);
//     // Connect to the Socket.IO server.
//     // The connection URL has the following format:
//     //     http[s]://<domain>:<port>[/<namespace>]
//     var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

//     // Event handler for new connections.
//     // The callback function is invoked when a connection with the
//     // server is established.
//     socket.on('connect', function() {
//         socket.emit('my_event', {data: 'I\'m connected!'});
//     });

//     // Event handler for server sent data.
//     // The callback function is invoked whenever the server emits data
//     // to the client. The data is then displayed in the "Received"
//     // section of the page.
//     socket.on('my_response', function(msg) {
//         $('#log').append('<br>' + $('<div/>').text('Received :' + msg.data).html());
//     });

// });