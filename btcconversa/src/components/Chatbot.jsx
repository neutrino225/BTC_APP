import { useState, useEffect, useRef } from "react";
import UserMessage from "./messages/User";
import BotMessage from "./messages/Bot";
import useChatStore from "../store/useChatStore";

import logo from "../assets/Conversa.png";

import sendMessage from "../services/message";

import TransactionTable from "./TransactionTable";
import BankSelector from "./BankSelector";

// eslint-disable-next-line react/prop-types
const Chatbot = ({ toggleSidebar, selectedPrompt }) => {
	const [inputValue, setInputValue] = useState("");
	const { messages, addMessage } = useChatStore();
	const messagesEndRef = useRef(null);

	// Update input field when selectedPrompt changes
	useEffect(() => {
		if (selectedPrompt) {
			setInputValue(selectedPrompt); // Update the input value with the selected prompt
		}
	}, [selectedPrompt]);

	const handleSendMessage = async () => {
		// Get the input message from your input field
		if (inputValue.trim()) {
			// Add the user's message to the store
			addMessage({ text: inputValue, sender: "user" });

			// Clear the input field after sending the message
			setInputValue("");

			// Get sender_id and account_number from sessionStorage
			const sender_id = sessionStorage.getItem("sender_id");
			const account_number = sessionStorage.getItem("account_number");

			if (!sender_id || !account_number) {
				console.error(
					"Sender ID or Account number not found in sessionStorage"
				);
				return;
			}

			try {
				// Send the message to the backend
				const botResponse = await sendMessage(
					inputValue,
					sender_id,
					account_number
				);

				// Add the bot's response to the message store
				if (botResponse && botResponse.length > 0) {
					console.log(botResponse);

					if (botResponse.length === 1) {
						if (botResponse[0].custom.type === "transactions") {
							// if the custom.type.transactions contains a message append it to the chat else show the transactions
							if (botResponse[0].custom.transactions.message) {
								addMessage({
									text: botResponse[0].custom.transactions.message,
									sender: "bot",
								});
							} else {
								addMessage({
									text: "Here are your transactions:",
									sender: "bot",
								});

								addMessage({
									text: (
										<TransactionTable
											transactions={botResponse[0].custom.transactions}
										/>
									),
									sender: "bot",
								});
							}
						} else {
							if (botResponse[0].text === "Please provide the bank name.") {
								addMessage({
									text: (
										<BankSelector
											banks={[
												"Allied Bank",
												"Bank of Punjab",
												"Habib Bank",
												"MCB Bank",
												"United Bank",
											]}
											onSubmit={(selectedBank) => {
												// Pass the value to the bot as a message from the user
												setInputValue(selectedBank);
											}}
										/>
									),
									sender: "bot",
								});
							} else {
								addMessage({
									text: botResponse[0].text,
									sender: "bot",
								});
							}
						}
					}

					if (botResponse.length > 1) {
						// Create a new text concatenated with all the responses
						let text = "";
						botResponse.forEach((response) => {
							text += response.text;
						});

						addMessage({
							text: text,
							sender: "bot",
						});
					}
				} else {
					// Fallback response if no valid bot response
					addMessage({
						text: "I don't have any responses yet.",
						sender: "bot",
					});
				}
			} catch (error) {
				console.error(error.message);

				// Handle any errors while sending the message
				addMessage({
					text: "Error sending message. Please try again.",
					sender: "bot",
				});
			}
		}
	};

	// Handle key down event
	const handleKeyDown = (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			// Allow shift + enter for new line
			e.preventDefault(); // Prevent default form submission
			handleSendMessage(); // Call send message handler
		}
	};

	// Scroll to the bottom of the chat messages whenever messages change
	useEffect(() => {
		if (messagesEndRef.current) {
			messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
		}
	}, [messages]);

	return (
		<aside className="bg-[#ffffff] w-full h-screen flex flex-col z-50">
			<div className="p-4 border-b border-[#D9D9D9]">
				<div className="flex justify-between items-center">
					<img src={logo} alt="Conversa" className="w-10" />
					<button
						onClick={toggleSidebar}
						className="text-black hover:text-gray-600 transition-colors z-50">
						{" "}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							className="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			</div>

			{/* Chat messages */}
			<div className="flex-grow overflow-y-auto bg-white p-4">
				{" "}
				{/* //bg-[#102D41] */}
				<div className="flex flex-col space-y-4 gap-4">
					{/* Render messages from Zustand store */}
					{messages.map((message, index) => {
						// Check if the message is sent by the user
						if (message.sender === "user") {
							return <UserMessage key={index} message={message.text} />;
						}

						// Check if the message text is a React element
						if (
							typeof message.text === "object" &&
							message.text !== null &&
							message.text.type
						) {
							return <div key={index}>{message.text}</div>;
						}

						// Render bot message
						return <BotMessage key={index} message={message.text} />;
					})}
					{/* Reference to the end of the messages */}
					<div ref={messagesEndRef} />
				</div>
			</div>

			{/* Message input and send button */}
			<div className="p-3 bg-[#ffffff] border-t border-[#D9D9D9]">
				<div className="flex relative">
					<textarea
						placeholder="Type a message..."
						value={inputValue}
						onChange={(e) => setInputValue(e.target.value)} // Update input value
						onKeyDown={handleKeyDown} // Handle Enter key press
						className="flex-1 p-4 bg-[#ECF2FF] rounded-full text-black border-none outline-none placeholder-gray-400 resize-none" // Added resize-none
						rows="1" // Set default height
						style={{ overflow: "hidden" }} // Hide scrollbar initially
					/>
					<button
						onClick={handleSendMessage} // Call send message handler
						className="absolute p-3 rounded-full right-1.5 bottom-1 bg-blue-600 text-white hover:bg-blue-700 transition-colors flex-shrink-0" // Added flex-shrink-0 to maintain size
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							className="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M14 5l7 7m0 0l-7 7m7-7H3"
							/>
						</svg>
					</button>
				</div>
			</div>
		</aside>
	);
};

export default Chatbot;
