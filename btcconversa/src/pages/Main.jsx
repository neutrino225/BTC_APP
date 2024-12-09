import { useState, useEffect } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import logo_rmbg from "../assets/logo_rmbg.png";
import Chatbot from "../components/Chatbot";
import useChatStore from "../store/useChatStore";
import btclogo from "../assets/BTC.png";
import { FeatureIcon, FeatureCard } from "../components/Features";
import PromptCard from "../components/PromptCard";
import ChatButton from "../components/ChatButton";
import { motion } from "framer-motion";

const Main = () => {
	const [isOpen, setIsOpen] = useState(false);
	const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
	const [selectedPrompt, setSelectedPrompt] = useState(""); // State for selected prompt

	const clearMessages = useChatStore((state) => state.clearMessages);

	const toggleSidebar = () => setIsOpen(!isOpen);

	const handleLogout = () => {
		clearMessages();

		sessionStorage.removeItem("sender_id");
		sessionStorage.removeItem("account_number");

		window.location.href = "/";
	};

	const features = [
		{
			icon: <FeatureIcon d="M13 10V3L4 14h7v7l9-11h-7z" />,
			title: "Real-time Transactions",
			description:
				"View all your transactions instantly and stay up to date with your finances.",
		},
		{
			icon: (
				<FeatureIcon d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
			),
			title: "Automated Responses",
			description:
				"Get quick answers to common queries with our AI-powered chatbot.",
		},
		{
			icon: (
				<FeatureIcon d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			),
			title: "Personalized Insights",
			description:
				"Receive tailored financial advice based on your transaction history.",
		},
		{
			icon: (
				<FeatureIcon d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
			),
			title: "Fund Transfers",
			description:
				"Make seamless fund transfers between your accounts or to other banks.",
		},
		{
			icon: (
				<FeatureIcon d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
			),
			title: "Secure Payments",
			description: "Make secure payments to merchants with just a few clicks.",
		},
		{
			icon: (
				<FeatureIcon d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
			),
			title: "Notifications",
			description:
				"Receive real-time notifications about your account activities.",
		},
	];

	const examples = [
		{
			prompt: "What's my account balance?",
		},
		{
			prompt: "Show me my transaction history.",
		},
		{
			prompt: "Transfer $500 to John Doe.",
		},
	];

	useEffect(() => {
		const handleResize = () => {
			setIsMobile(window.innerWidth < 768);
		};

		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	return (
		<>
			{/* Main content and Sidebar Panel Group */}
			<PanelGroup direction="horizontal">
				<Panel minSize={65}>
					<div className="h-screen flex flex-col">
						<div className="stars">
							{Array.from({ length: 50 }).map((_, index) => (
								<div key={index} className="star"></div>
							))}
						</div>
						{/* Header inside the resizable panel */}
						<header className="header-section w-full max-md:px-5 md:w-9/12 mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center shadow-xl">
							{/* Logo */}
							<a className="flex-shrink-0 flex gap-2 justify-center items-center">
								<p>
									<span className="text-base md:text-2xl text-white font-poppins tracking-wide font-extrabold">
										CONVERSA
									</span>
								</p>
							</a>

							<button
								onClick={handleLogout}
								className="relative py-2 px-8 text-black text-base font-bold overflow-hidden bg-white rounded-full transition-all duration-400 ease-in-out shadow-md hover:scale-105 hover:text-white hover:shadow-lg active:scale-90 before:absolute before:top-0 before:-left-full before:w-full before:h-full before:bg-gradient-to-r before:from-blue-500 before:to-blue-300 before:transition-all before:duration-500 before:ease-in-out before:z-[-1] before:rounded-full hover:before:left-0">
								Logout
							</button>
						</header>

						<main className="main-section flex flex-col gap-10 pt-32 w-full overflow-y-auto select-none">
							{/* Hero Section */}
							<div className="h-52 w-8/12 mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
								<div className="max-w-7xl mx-auto">
									<div className="flex justify-center items-center max-md:flex-col gap-5 w-full">
										<h1 className="text-4xl md:text-6xl font-extrabold text-white drop-shadow-lg">
											Welcome to{" "}
										</h1>
										<h1 className="relative text-4xl md:text-6xl font-extrabold text-white flex justify-center items-center ml-8 drop-shadow-lg">
											<span className="max-md:hidden absolute w-16 top-1 -left-12 transform hover:rotate-6 transition-transform duration-300">
												<img
													src={logo_rmbg}
													alt="logo"
													className="drop-shadow-lg"
												/>
											</span>
											<span className="md:hidden absolute w-10 top-1 -left-8 transform hover:rotate-6 transition-transform duration-300">
												<img
													src={logo_rmbg}
													alt="logo"
													className="drop-shadow-lg"
												/>
											</span>
											onversa
										</h1>
									</div>

									<p className="text-gray-300 text-sm mt-4 tracking-wide">
										Simplifying your banking experience with AI-powered
										conversations.
									</p>

									<div className="flex justify-center items-center gap-2 mt-8 transition-transform transform hover:scale-105">
										<p className="text-white font-semibold text-lg">
											Powered by
										</p>
										<img
											src={btclogo}
											alt="BluTech Logo"
											className="h-5 drop-shadow-lg"
										/>
									</div>
								</div>
							</div>

							{/* Sample Prompts Section */}
							<section className="features-section backdrop-blur-md rounded-xl p-8 shadow-2xl max-w-7xl mx-auto ">
								<h2 className="text-3xl font-semibold text-white text-center mb-8">
									How to Talk to Conversa?
								</h2>
								<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
									{examples.map((item, index) => (
										<div
											key={index}
											onClick={() => {
												setSelectedPrompt(item.prompt);

												if (!isOpen) {
													toggleSidebar();
												}
											}}>
											<PromptCard prompt={item.prompt} />
										</div>
									))}
								</div>
							</section>

							{/* Features Section */}
							<section className="features-section backdrop-blur-md rounded-xl p-8 shadow-2xl max-w-7xl mx-auto">
								<h2 className="text-3xl font-semibold text-white mb-8 text-center">
									Why Choose Conversa?
								</h2>
								<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
									{features.map((feature, index) => (
										<FeatureCard key={index} {...feature} />
									))}
								</div>
							</section>

							{/* Footer */}
							<footer className="mt-auto bg-gray-800 py-4">
								<div className="flex justify-between items-center max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
									<div className="flex justify-center items-center gap-2">
										<p className="text-white/80 text-lg font-bold">
											Powered by
										</p>
										<img src={btclogo} alt="BluTech Logo" className="h-5" />
									</div>
								</div>
							</footer>
						</main>
					</div>
				</Panel>

				{/* Resizer Handle between panels */}
				{!isMobile && isOpen && (
					<PanelResizeHandle className="w-2 bg-gray-800 hover:bg-gray-700 cursor-col-resize" />
				)}

				{/* Sidebar Panel */}
				{!isMobile && isOpen && (
					<Panel minSize={25} defaultSize={30}>
						{/* Sidebar */}
						{/* Add sidebar in a div so the stars dont show in the background */}
						<div className="sidebar-section h-full flex flex-col bg-[#102D41]">
							{/* Chatbot component */}
							<Chatbot
								toggleSidebar={toggleSidebar}
								selectedPrompt={selectedPrompt}
							/>
						</div>
					</Panel>
				)}
			</PanelGroup>

			{/* Full-screen chatbot for mobile view */}
			{isMobile && isOpen && (
				<motion.div
					className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center z-50"
					initial={{ opacity: 0 }}
					animate={{ opacity: 1 }}
					exit={{ opacity: 0 }}
					transition={{ duration: 0.3 }}>
					<motion.div
						className="bg-[#102D41] w-full h-full md:w-96 md:h-auto rounded-lg flex flex-col"
						initial={{ scale: 0.95 }}
						animate={{ scale: 1 }}
						exit={{ scale: 0.95 }}
						transition={{ duration: 0.3 }}>
						<Chatbot
							toggleSidebar={toggleSidebar}
							selectedPrompt={selectedPrompt}
						/>
					</motion.div>
				</motion.div>
			)}

			{/* Chat toggle button */}
			<ChatButton toggleSidebar={toggleSidebar} />
		</>
	);
};

export default Main;
