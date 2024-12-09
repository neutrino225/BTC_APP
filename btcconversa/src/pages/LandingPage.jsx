import Header from "../components/Header";
import Footer from "../components/Footer";
import FeaturesSection from "../components/Features";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import logo from "../assets/Conversa.png";

const LandingPage = () => {
	const navigate = useNavigate();
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const timer = setTimeout(() => {
			setIsLoading(false);
		}, 3400);

		return () => clearTimeout(timer);
	}, []);

	// Variants for animations
	const heroTextVariants = {
		hidden: { opacity: 0, y: 20 },
		visible: {
			opacity: 1,
			y: 0,
			transition: { duration: 1, staggerChildren: 0.2, delayChildren: 0.3 },
		},
	};

	const heroButtonVariants = {
		hidden: { opacity: 0, scale: 0.9 },
		visible: {
			opacity: 1,
			scale: 1,
			transition: { duration: 0.6, ease: "easeOut", delay: 1.2 },
		},
	};

	const featureVariants = {
		hidden: { opacity: 0, y: 40 },
		visible: {
			opacity: 1,
			y: 0,
			transition: { duration: 0.9, ease: "easeOut", delay: 0.2 },
		},
	};

	return (
		<main className="relative w-full min-h-screen overflow-hidden">
			{/* Loading Screen */}
			<motion.div
				className={`absolute top-0 left-0 w-full h-full flex justify-center items-center bg-black ${
					!isLoading ? "pointer-events-none" : ""
				}`}
				initial={{ opacity: 1, scale: 1 }}
				animate={{ opacity: isLoading ? 1 : 0, scale: isLoading ? 1 : 0 }}
				transition={{ duration: 2 }}
				style={{ zIndex: isLoading ? 50 : -1 }}>
				<div className="loader-container">
					<div className="absolute animate-spin rounded-full h-28 w-28 border-t-4 border-b-4 border-blue-500"></div>
					<img src={logo} className="rounded-full h-20 w-20 animate-pulse" />
				</div>
			</motion.div>

			{/* Landing Page Content */}
			<motion.div
				className="relative w-full min-h-screen flex flex-col justify-start items-start bg-gradient-to-b from-[#00274d] to-[#537895] bg-no-repeat bg-cover bg-fixed"
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: isLoading ? 0 : 1, y: isLoading ? 20 : 0 }}
				transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
				style={{ zIndex: isLoading ? 40 : 50 }}>
				<Header />

				{/* Hero Section */}
				<section className="w-full min-h-screen px-4 md:px-10 flex justify-center items-center">
					<motion.div
						className="w-full px-4 z-20"
						variants={heroTextVariants}
						initial="hidden"
						animate="visible">
						<div className="max-w-2xl mx-auto text-center">
							<motion.h1
								className="text-4xl font-bold sm:text-7xl mb-4"
								initial={{ opacity: 0, scale: 0.8 }}
								animate={{ opacity: 1, scale: 1 }}
								transition={{ duration: 1.2, delay: 0.4, ease: "easeInOut" }}>
								<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-white">
									Your Personalized Banking Assistant
								</span>
							</motion.h1>
							<motion.p
								className="mt-5 text-base text-white sm:text-lg"
								variants={heroTextVariants}
								initial="hidden"
								animate="visible"
								transition={{ delay: 0.6, duration: 1.2 }}>
								{`BTC Conversa uses conversational AI to simplify your banking experience.
          Manage your account, view transactions, and get personalized insights—effortlessly.`}
							</motion.p>

							<motion.a
								className="flex items-center justify-center mt-14"
								variants={heroButtonVariants}
								initial="hidden"
								animate="visible"
								onClick={() => navigate("/register")}>
								<div className="relative group">
									<button className="relative inline-block p-px font-semibold leading-6 text-white bg-gray-800 shadow-2xl cursor-pointer rounded-xl shadow-zinc-900 transition-transform duration-300 ease-in-out hover:scale-105 active:scale-95">
										<span className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-400 via-blue-500 to-purple-500 p-[2px] opacity-0 transition-opacity duration-500 group-hover:opacity-100"></span>

										<span className="relative z-10 block px-6 py-3 rounded-xl bg-gray-950">
											<div className="relative z-10 flex items-center space-x-2">
												<span className="transition-all duration-500 group-hover:translate-x-1">
													Get Started
												</span>
												<svg
													className="w-6 h-6 transition-transform duration-500 group-hover:translate-x-1"
													aria-hidden="true"
													fill="white"
													viewBox="0 0 20 20"
													xmlns="http://www.w3.org/2000/svg">
													<path
														clipRule="evenodd"
														d="M8.22 5.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 0 1 0-1.06Z"
														fillRule="evenodd"
													/>
												</svg>
											</div>
										</span>
									</button>
								</div>
							</motion.a>
						</div>
					</motion.div>
				</section>

				{/* Features Section */}
				<motion.section
					className="w-full px-4 md:px-10 py-2 md:py-10"
					initial="hidden"
					whileInView="visible"
					viewport={{ once: true, amount: 0.2 }}
					variants={featureVariants}>
					<FeaturesSection />
				</motion.section>

				{/* Footer */}
				<Footer />
			</motion.div>
		</main>
	);
};

export default LandingPage;
