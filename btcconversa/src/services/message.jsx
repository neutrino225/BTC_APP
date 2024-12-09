import axios from "axios";

const sendMessage = async (message, sender_id, account_number) => {
	const url = "http://localhost:5005/webhooks/rest/webhook";
	const payload = {
		sender: sender_id,
		message: message,
		metadata: {
			account_number: account_number,
		},
	};

	try {
		const response = await axios.post(url, payload);
		return response.data;
	} catch (error) {
		console.error("Error sending message:", error);
		throw error;
	}
};

export default sendMessage;
