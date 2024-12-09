/* eslint-disable react/prop-types */
import { useState } from "react";
import { ChevronDown } from "lucide-react";

const BankSelector = ({ banks = [], onSubmit }) => {
	const [selectedBank, setSelectedBank] = useState("");

	const handleSubmit = () => {
		if (selectedBank) {
			onSubmit(selectedBank); // Pass the selected bank to the parent callback
		}
	};

	return (
		<div
			className="w-full max-w-md bg-white backdrop-blur-lg border border-white/20 rounded-2xl shadow-2xl p-6 
				transition-all duration-300 hover:shadow-3xl sm:w-96 md:w-full lg:w-96">
			<div className="flex flex-col space-y-4">
				<label
					htmlFor="banks"
					className="text-blue-900 font-semibold text-lg text-center">
					Select Your Bank
				</label>

				<div className="relative">
					<select
						name="banks"
						id="banks"
						value={selectedBank}
						onChange={(e) => setSelectedBank(e.target.value)}
						className="w-full appearance-none bg-white/40 backdrop-blur-md border border-blue-200/50 text-blue-900 
							py-3 px-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 
							transition-all duration-300 cursor-pointer text-base sm:text-sm"
						aria-label="Choose your bank">
						<option value="" disabled className="text-gray-400">
							Choose a Bank
						</option>
						{banks.map((bank, index) => (
							<option
								key={index}
								value={bank}
								className="bg-white text-blue-900">
								{bank}
							</option>
						))}
					</select>

					<div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-blue-800">
						<ChevronDown size={20} />
					</div>
				</div>

				<button
					onClick={handleSubmit}
					className={`w-full bg-blue-600/80 backdrop-blur-md text-white py-3 rounded-xl 
						hover:bg-blue-700/90 transition-all duration-300 
						focus:outline-none focus:ring-2 focus:ring-blue-500/50 
						transform hover:scale-[1.02] active:scale-[0.98]
						text-base sm:text-sm ${
							selectedBank ? "opacity-100" : "opacity-50 cursor-not-allowed"
						}`}
					disabled={!selectedBank}>
					Submit
				</button>
			</div>
		</div>
	);
};

export default BankSelector;
