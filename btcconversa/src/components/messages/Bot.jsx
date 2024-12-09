/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import logo from "../../assets/Conversa.png";

const BotMessage = ({ message }) => {
	const [isVisible, setIsVisible] = useState(false);

	useEffect(() => {
		setIsVisible(true);
	}, []);

	return (
		<div className={`flex justify-start message ${isVisible ? "visible" : ""}`}>
			<div className="bg-transparent p-3 rounded-lg shadow flex justify-start items-start">
				<img
					src={logo}
					alt="Conversa Logo"
					className="w-8 h-8 rounded-full mr-2"
				/>

				<p
					className="text-black"
					dangerouslySetInnerHTML={{ __html: message }}></p>
			</div>
		</div>
	);
};

export default BotMessage;
