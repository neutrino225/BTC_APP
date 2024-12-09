import { useEffect, useState } from "react";

// eslint-disable-next-line react/prop-types
const UserMessage = ({ message }) => {
	const [isVisible, setIsVisible] = useState(false);

	useEffect(() => {
		setIsVisible(true);
	}, []);

	return (
		<div className={`flex justify-start message ${isVisible ? "visible" : ""}`}>
			<div className="bg-[#ECF2FF] p-3 rounded-lg shadow flex gap-3">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					strokeWidth={1.5}
					stroke="currentColor"
					className="size-6">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
					/>
				</svg>

				<p className="text-black">{message}</p>
			</div>
		</div>
	);
};

export default UserMessage;
