import React from "react";

const Footer = () => {
	return (
		<footer className="bg-[#101212] text-white py-10 w-full">
			<div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
				{/* Footer Top Section */}
				<div className="flex flex-col md:flex-row gap-10 justify-between items-center mb-8">
					{/* Footer Navigation */}
					<div className="flex space-x-10">
						<a
							href="#features"
							className="text-base text-white transition-all duration-200 hover:text-blue-400">
							Features
						</a>
						<a
							href="#solutions"
							className="text-base text-white transition-all duration-200 hover:text-blue-400">
							Solutions
						</a>
						<a
							href="#resources"
							className="text-base text-white transition-all duration-200 hover:text-blue-400">
							Resources
						</a>
						<a
							href="#pricing"
							className="text-base text-white transition-all duration-200 hover:text-blue-400">
							Pricing
						</a>
					</div>

					{/* Powered by BTC Conversa */}
					<div className="text-center text-sm">
						<p className="text-gray-300">Powered by Blutech Consulting</p>
					</div>
				</div>

				{/* Footer Bottom Section */}
				<div className="mt-8 text-center text-sm text-gray-400">
					<p>
						&copy; {new Date().getFullYear()} BTC Conversa. All rights reserved.
					</p>
				</div>
			</div>
		</footer>
	);
};

export default Footer;
