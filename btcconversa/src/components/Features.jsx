import { useState, useRef, useEffect } from "react";

// eslint-disable-next-line react/prop-types
export const FeatureCard = ({ icon, title, description }) => {
	return (
		<div className="p-6 bg-[#1E2A2A] rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105 hover:bg-[#2A3A3A] group">
			<div className="text-center">
				{icon}
				<h3 className="mt-4 text-xl font-semibold text-white group-hover:text-blue-400 transition-colors duration-300">
					{title}
				</h3>
				<p className="mt-2 text-gray-300 group-hover:text-white transition-colors duration-300">
					{description}
				</p>
			</div>
		</div>
	);
};

// eslint-disable-next-line react/prop-types
export const FeatureIcon = ({ d }) => (
	<svg
		className="w-12 h-12 mx-auto text-blue-400 group-hover:text-white transition-colors duration-300"
		fill="none"
		stroke="currentColor"
		strokeWidth="2"
		viewBox="0 0 24 24"
		xmlns="http://www.w3.org/2000/svg">
		<path strokeLinecap="round" strokeLinejoin="round" d={d} />
	</svg>
);

const FeaturesSection = () => {
	const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
	const sectionRef = useRef(null);

	useEffect(() => {
		const handleMouseMove = (event) => {
			if (sectionRef.current) {
				const { left, top } = sectionRef.current.getBoundingClientRect();
				setMousePosition({
					x: event.clientX - left,
					y: event.clientY - top,
				});
			}
		};

		window.addEventListener("mousemove", handleMouseMove);

		return () => {
			window.removeEventListener("mousemove", handleMouseMove);
		};
	}, []);

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

	return (
		<section
			id="features"
			className="relative w-full py-20 px-10 sm:py-24 sm:px-16 lg:px-24 overflow-hidden"
			ref={sectionRef}>
			<div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8 relative z-10">
				{/* Heading */}
				<div className="max-w-3xl mx-auto text-center mb-16">
					<h2 className="text-4xl font-bold text-white sm:text-5xl mb-4">
						Features
					</h2>
					<p className="text-base text-gray-300 sm:text-lg">
						BTC Conversa offers a range of features to help you manage your
						finances. From account management to personalized insights,
						we&apos;ve got you covered.
					</p>
				</div>

				{/* Features Grid */}
				<div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
					{features.map((feature, index) => (
						<FeatureCard key={index} {...feature} />
					))}
				</div>
			</div>

			{/* Animated background effect */}
			<div
				className="absolute inset-0 bg-blue-500 opacity-10 blur-3xl transition-transform duration-300 ease-out"
				style={{
					transform: `translate(${mousePosition.x / 20}px, ${
						mousePosition.y / 20
					}px)`,
				}}></div>
		</section>
	);
};

export default FeaturesSection;
