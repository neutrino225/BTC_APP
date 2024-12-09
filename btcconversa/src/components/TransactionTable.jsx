/* eslint-disable react/prop-types */

// TransactionCard Component
const TransactionCard = ({ transaction }) => {
	const getTypeColor = (type) => {
		return type === "Credit" ? "text-green-600" : "text-red-600";
	};

	return (
		<li className="flex justify-between items-center bg-white rounded-lg p-4">
			<div className="flex items-center">
				{/* Icon */}
				<div
					className={`w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 text-blue-500 mr-4`}>
					{transaction.type === "Debit" ? (
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							strokeWidth="1.5"
							stroke="currentColor"
							className="size-6">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="m4.5 19.5 15-15m0 0H8.25m11.25 0v11.25"
							/>
						</svg>
					) : (
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							strokeWidth="1.5"
							stroke="currentColor"
							className="size-6">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="m19.5 4.5-15 15m0 0h11.25m-11.25 0V8.25"
							/>
						</svg>
					)}
				</div>

				{/* Details */}
				<div>
					<p className="font-semibold text-gray-800">{transaction.to}</p>
					<p className="text-sm text-gray-500">{transaction.category}</p>
					<p className="text-sm text-gray-400">
						{transaction.dateTime.split(" ")[1]}
					</p>
				</div>
			</div>

			{/* Amount */}
			<div
				className={`font-semibold text-lg ${getTypeColor(transaction.type)}`}>
				{transaction.type === "Debit" ? "-" : "+"}$
				{parseFloat(transaction.amount).toFixed(2)}
			</div>
		</li>
	);
};

// TransactionList Component
const TransactionList = ({ transactions }) => {
	// Group transactions by date
	const groupByDate = (transactions) => {
		const groups = {};
		transactions.forEach((transaction) => {
			const [datePart] = transaction.dateTime.split(" ");
			if (!groups[datePart]) groups[datePart] = [];
			groups[datePart].push(transaction);
		});
		return groups;
	};

	const groupedTransactions = groupByDate(transactions);

	return (
		<div className="max-w-lg mx-auto p-4 relative rounded-lg">
			{/* Transaction List */}
			<div className="min-h-[120px] max-h-[500px] overflow-y-auto relative">
				{Object.entries(groupedTransactions).map(([date, transactions]) => (
					<div key={date}>
						{/* Date Section */}
						<h6 className="text-gray-700 font-bold mb-4">
							{date === new Date().toISOString().split("T")[0] ? "Today" : date}
						</h6>

						<div className="border-t border-gray-700 mb-1"></div>

						{/* Transactions */}
						<ul>
							{transactions.map((transaction) => (
								<TransactionCard
									key={transaction.reference_id}
									transaction={transaction}
								/>
							))}
						</ul>
					</div>
				))}
			</div>
			{/* Blur Mask */}
			<div className="absolute rounded-lg bottom-0 left-0 right-0 h-7 pointer-events-none bg-gradient-to-t from-gray-300 to-transparent"></div>{" "}
		</div>
	);
};

export default TransactionList;
