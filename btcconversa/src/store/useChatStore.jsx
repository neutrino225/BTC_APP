import { create } from "zustand"; // Corrected import statement
import { persist } from "zustand/middleware";

const useChatStore = create(
	persist(
		(set) => ({
			messages: [{ text: "Hello! How can I assist you today?", sender: "bot" }],
			addMessage: (message) =>
				set((state) => ({ messages: [...state.messages, message] })),
			clearMessages: () =>
				set({
					messages: [
						{ text: "Hello! How can I assist you today?", sender: "bot" },
					],
				}),
		}),
		{
			name: "chat-storage", // Name of the local storage key
		}
	)
);

export default useChatStore;
