import { useState, useEffect } from "react";
import logo from "../assets/logo_rmbg.png";

// eslint-disable-next-line react/prop-types
const ChatButton = ({ toggleSidebar }) => {
	const [isMounted, setIsMounted] = useState(false);

	useEffect(() => {
		// Add a 2-second delay before triggering the animation
		const timeout = setTimeout(() => {
			setIsMounted(true);
		}, 2000);

		// Cleanup the timeout to prevent memory leaks
		return () => clearTimeout(timeout);
	}, []);

	return (
		<div
			className={`fixed ${
				isMounted ? "bottom-12 right-6" : "bottom-[-100px] right-6"
			} ease-[linear(0,_0.283_9.3%,_0.529_20%,_0.75_32.8%,_0.911_45.7%,_0.963_51.7%,_1_57.7%,_0.979_63.8%,_0.973_70.3%,_0.996_90.4%,_1)] transition-all duration-1000`}>
			<div className="rounded-full p-[2px] hover:bg-gradient-to-r from-blue-800 to-indigo-900 transition-all duration-300 ease-in-out shadow-lg">
				<button
					onClick={toggleSidebar}
					className="px-4 py-4 bg-gray-800 rounded-full cursor-pointer transition-transform duration-300 ease-in-out">
					<img src={logo} alt="Logo" className="w-14" />
				</button>
			</div>
		</div>
	);
};

export default ChatButton;
