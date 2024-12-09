import React, { useState } from "react";

const Register = () => {
	const [formData, setFormData] = useState({
		firstName: "",
		lastName: "",
		email: "",
		password: "",
		confirmPassword: "",
		// Add more fields here as needed
	});

	const handleChange = (e) => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		// Handle signup logic here
		console.log("Signup attempt with:", formData);
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#537895] to-[#09203f] py-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-md w-full space-y-8 bg-[#1E2A2A] bg-opacity-60 backdrop-blur-lg border border-white/20 rounded-xl shadow-neumorphism p-10">
				<div>
					<h2 className="mt-6 text-center text-3xl font-extrabold text-white">
						Create your account
					</h2>
				</div>
				<form className="mt-8 space-y-6" onSubmit={handleSubmit}>
					<div className="rounded-md shadow-sm -space-y-px flex flex-col gap-3">
						<div className="neumorphism bg-[#1E2A2A] p-4 rounded-md">
							<label htmlFor="first-name" className="sr-only">
								First Name
							</label>
							<input
								id="first-name"
								name="firstName"
								type="text"
								required
								className="appearance-none rounded-md relative block w-full px-3 py-2 border border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:z-10 sm:text-sm bg-transparent"
								placeholder="First Name"
								value={formData.firstName}
								onChange={handleChange}
							/>
						</div>

						<div className="neumorphism bg-[#1E2A2A] p-4 rounded-md mt-4">
							<label htmlFor="last-name" className="sr-only">
								Last Name
							</label>
							<input
								id="last-name"
								name="lastName"
								type="text"
								required
								className="appearance-none rounded-md relative block w-full px-3 py-2 border border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:z-10 sm:text-sm bg-transparent"
								placeholder="Last Name"
								value={formData.lastName}
								onChange={handleChange}
							/>
						</div>

						<div className="neumorphism bg-[#1E2A2A] p-4 rounded-md mt-4">
							<label htmlFor="email-address" className="sr-only">
								Email address
							</label>
							<input
								id="email-address"
								name="email"
								type="email"
								autoComplete="email"
								required
								className="appearance-none rounded-md relative block w-full px-3 py-2 border border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:z-10 sm:text-sm bg-transparent"
								placeholder="Email address"
								value={formData.email}
								onChange={handleChange}
							/>
						</div>

						<div className="neumorphism bg-[#1E2A2A] p-4 rounded-md mt-4">
							<label htmlFor="password" className="sr-only">
								Password
							</label>
							<input
								id="password"
								name="password"
								type="password"
								autoComplete="new-password"
								required
								className="appearance-none rounded-md relative block w-full px-3 py-2 border border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:z-10 sm:text-sm bg-transparent"
								placeholder="Password"
								value={formData.password}
								onChange={handleChange}
							/>
						</div>

						<div className="neumorphism bg-[#1E2A2A] p-4 rounded-md mt-4">
							<label htmlFor="confirm-password" className="sr-only">
								Confirm Password
							</label>
							<input
								id="confirm-password"
								name="confirmPassword"
								type="password"
								autoComplete="new-password"
								required
								className="appearance-none rounded-md relative block w-full px-3 py-2 border border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:z-10 sm:text-sm bg-transparent"
								placeholder="Confirm Password"
								value={formData.confirmPassword}
								onChange={handleChange}
							/>
						</div>
					</div>

					<div>
						<button
							type="submit"
							className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-150 ease-in-out">
							Sign up
						</button>
					</div>
				</form>
				<div className="text-center">
					<p className="mt-2 text-sm text-gray-400">
						Already have an account?{" "}
						<a
							href="/login"
							className="font-medium text-blue-400 hover:text-blue-300">
							Sign in
						</a>
					</p>
				</div>
			</div>
		</div>
	);
};

export default Register;
