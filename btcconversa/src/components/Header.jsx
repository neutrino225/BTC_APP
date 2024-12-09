import { useState, useEffect } from "react";
import logo from "../assets/Conversa.png";
import { useNavigate } from "react-router-dom";

const Header = () => {
	const navigate = useNavigate();

	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const [isScrolled, setIsScrolled] = useState(false);

	const toggleMenu = () => {
		setIsMenuOpen(!isMenuOpen);
		document.body.style.overflow = isMenuOpen ? "unset" : "hidden";
	};

	useEffect(() => {
		const handleScroll = () => {
			setIsScrolled(window.scrollY > 20);
		};

		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	// eslint-disable-next-line react/prop-types
	const NavLink = ({ href, children }) => {
		return (
			<a
				href={href}
				className="text-white transition-all duration-300 hover:text-blue-300 relative group">
				{children}
				<span className="absolute left-0 right-0 bottom-0 h-0.5 bg-blue-300 transform origin-left scale-x-0 transition-transform duration-300 group-hover:scale-x-100"></span>
			</a>
		);
	};

	return (
		<header
			className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
				isScrolled ? "backdrop-blur-3xl bg-blue-950/70" : "bg-transparent"
			}`}>
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex justify-between items-center py-4">
					{/* Logo */}
					<a
						className="flex-shrink-0 flex gap-2 justify-center items-center"
						onClick={() => navigate("/")}>
						<img className="h-8 w-auto" src={logo} alt="BTC Conversa Logo" />
						<p>
							<span className="text-lg text-white font-poppins tracking-wide font-extrabold">
								CONVERSA
							</span>
						</p>
					</a>

					{/* Desktop Navigation */}
					<nav className="hidden md:flex space-x-8">
						<NavLink href="#features">Features</NavLink>
						<NavLink href="#resources">Resources</NavLink>
						<NavLink href="#pricing">Pricing</NavLink>
					</nav>

					{/* Desktop Buttons */}
					<div className="hidden md:flex items-center space-x-4 gap-5">
						<button
							className="text-white hover:text-blue-300 transition-colors duration-300"
							onClick={() => navigate("/login")}>
							Login
						</button>
						<button
							onClick={() => navigate("/register")}
							className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-all duration-300 transform hover:scale-105 hover:shadow-lg">
							Get Started
						</button>
					</div>

					{/* Mobile Menu Button */}
					<div className="md:hidden">
						<button
							onClick={toggleMenu}
							className="text-white hover:text-blue-300 transition-colors duration-300">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 36 36"
								width="26"
								height="26"
								fill="none"
								stroke="currentColor"
								strokeWidth="3"
								strokeLinecap="round"
								strokeLinejoin="round"
								className="transition-transform duration-300 ease-in-out">
								<line x1="4" y1="8" x2="32" y2="8"></line>
								<line x1="4" y1="18" x2="32" y2="18"></line>
								<line x1="4" y1="28" x2="32" y2="28"></line>
							</svg>
						</button>
					</div>
				</div>
			</div>

			{/* Mobile Menu */}
			<div
				className={`fixed inset-0 bg-blue-950 z-40 transform ${
					isMenuOpen ? "translate-x-0" : "translate-x-full"
				} transition-transform duration-300 ease-in-out md:hidden`}>
				<div className="absolute top-4 right-4">
					<button
						onClick={toggleMenu}
						className="text-white text-2xl hover:text-blue-300 transition-colors duration-300">
						&times;
					</button>
				</div>
				<div className="flex flex-col h-full justify-center items-center space-y-8">
					<button onClick={toggleMenu}>
						<NavLink href="#features">Features</NavLink>
					</button>
					<hr className="border-white w-3/4" />
					<button onClick={toggleMenu}>
						<NavLink href="#resources">Resources</NavLink>
					</button>
					<hr className="border-white w-3/4" />
					<button onClick={toggleMenu}>
						<NavLink href="#pricing">Pricing</NavLink>
					</button>
					<hr className="border-white w-3/4" />
					<button
						className="text-lg text-white hover:text-blue-300 transition-colors duration-300"
						onClick={() => {
							navigate("/login");
						}}>
						Login
					</button>
					<hr className="border-white w-3/4" />
					<button
						className="bg-blue-500 text-white text-lg px-3 py-1.5 rounded-md hover:bg-blue-600 transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
						onClick={() => navigate("/register")}>
						Get Started
					</button>
				</div>
			</div>
		</header>
	);
};

export default Header;
