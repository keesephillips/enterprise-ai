document.addEventListener("DOMContentLoaded", () => {
	// Connect to Socket.IO server
	// The server URL will be the same origin by default
	var socket = io(); // [2, 3]

	socket.on("connect", function () {
		console.log("Connected to server");
		// Optionally, send a join message or user info
		// socket.emit('user_join', {username: 'current_user_from_template_or_js'});
	});

	socket.on("disconnect", function () {
		console.log("Disconnected from server");
		addMessage({ username: "System", text: "You have been disconnected." });
	});

	// Listen for new messages from the server
	socket.on("new_chat_message", function (data) {
		addMessage(data);
	});

	// Listen for server/system messages
	socket.on("server_message", function (data) {
		addMessage({ username: "System", text: data.text });
	});

	// Handle form submission to send messages
	const form = document.getElementById("message-form");
	const input = document.getElementById("message-input");

	form.addEventListener("submit", function (e) {
		e.preventDefault();
		if (input.value) {
			socket.emit("user_message", { text: input.value }); // [2]
			input.value = ""; // Clear input field
		}
	});

	function addMessage(data) {
		const messages = document.getElementById("messages");
		const item = document.createElement("li");
		item.textContent = `${data.username}: ${data.text}`;
		messages.appendChild(item);
		// Scroll to the bottom of the chat window
		const chatWindow = document.getElementById("chat-window");
		if (chatWindow) {
			chatWindow.scrollTop = chatWindow.scrollHeight;
		}
	}
});
