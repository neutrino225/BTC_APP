/** @type {import('tailwindcss').Config} */
export default {
	content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
	theme: {
		extend: {
			fontFamily: {
				poppins: ["Poppins", "sans-serif"],
				raleway: ["Raleway", "sans-serif"],
			},
			boxShadow: {
				neumorphism:
					"9px 9px 15px rgba(0, 0, 0, 0.2), -9px -9px 15px rgba(255, 255, 255, 0.1)",
			},
		},
	},
	plugins: [],
};
