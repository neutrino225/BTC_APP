$(document).ready(function () {
	// Toggle chatbox visibility when the chatbot button is clicked
	$("#chatbot-button").click(function () {
		$(".chat-box").toggle(); // Toggle visibility of the chatbox
	});

	// Close the chatbox when the header is clicked
	$(".chat-box-header").click(function () {
		$(".chat-box").hide(); // Hide the chatbox
	});

	$("#login-form").submit(function (event) {
		event.preventDefault(); // Prevent default form submission behavior

		var username = $("#username").val();
		var password = $("#password").val();

		$.ajax({
			url: "/login", // Flask login API
			type: "POST",
			data: {
				username: username,
				password: password,
			},
			success: function (response) {
				console.log("Login response:", response); // Log the response from Flask
				if (response.sender_id) {
					// Store sender_id and account_number in sessionStorage
					sessionStorage.setItem("sender_id", response.sender_id);
					sessionStorage.setItem("account_number", response.account_number);
					console.log(
						"Sender ID stored in sessionStorage:",
						response.sender_id
					); // Log sender_id for debugging

					// Redirect to the dashboard
					window.location.href = "/dashboard";
				} else {
					alert("Invalid credentials");
				}
			},
			error: function (error) {
				console.log("Error during login:", error);
				alert("Error during login. Please try again.");
			},
		});
	});

	// Function to send the message to RASA
	function sendMessageToRasa(message) {
		var sender_id = sessionStorage.getItem("sender_id");
		var account_number = sessionStorage.getItem("account_number");
		console.log("Sender ID retrieved from sessionStorage:", sender_id); // Log sender_id for debugging

		if (!sender_id || !account_number) {
			alert("You need to log in first.");
			return;
		}

		var payload = {
			sender: sender_id, // Pass the sender_id as the session identifier
			message: message,
			metadata: {
				account_number: account_number, // Pass the account_number in the metadata
			},
		};

		$.ajax({
			url: "http://localhost:5005/webhooks/rest/webhook", // RASA webhook URL
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify(payload), // Send the payload as a JSON string
			xhrFields: {
				withCredentials: true, // Ensure session cookies are sent with the request
			},
			success: function (response) {
				console.log("RASA response:", response); // Log the response from RASA for debugging
				if (response && response.length > 0) {
					// Combine all responses into one string without changing it
					let botMessage = response.map((res) => res.text).join("\n");
					displayBotResponse(botMessage); // Display the raw response as it is
				}

				console.log("Response from RASA:", response); // Log the response from RASA for debugging
			},
			error: function (error) {
				console.log("Error while sending message to RASA:", error);
				alert("Error communicating with the chatbot. Please try again.");
			},
		});
	}

	// Display the user's message in the chatbox
	function displayUserMessage(message) {
		$(".chat-box-body").append(`<p><strong>You:</strong> ${message}</p>`);
		$(".chat-box-body").scrollTop($(".chat-box-body")[0].scrollHeight); // Scroll to the bottom of the chatbox
	}

	// Display the bot's response in the chatbox with no modifications
	function displayBotResponse(response) {
		$(".chat-box-body").append(`<p><strong>Bot:</strong> ${response}</p>`); // Display the response directly without any modification
		$(".chat-box-body").scrollTop($(".chat-box-body")[0].scrollHeight); // Scroll to the bottom of the chatbox
	}

	// Handle 'Enter' keypress to send message
	$("#user-message-input").keypress(function (event) {
		if (event.which === 13) {
			// 13 is the Enter key
			var message = $("#user-message-input").val();
			console.log("User message:", message); // Log the user message for debugging

			// Send the user's message to RASA
			sendMessageToRasa(message);

			// Display the user's message in the chatbox
			displayUserMessage(message);

			// Clear the input field
			$("#user-message-input").val("");
		}
	});
});
