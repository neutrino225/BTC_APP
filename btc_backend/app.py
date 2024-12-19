from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    make_response,
)
import sqlite3
import uuid
from flask_session import Session
import logging
from fuzzywuzzy import process
from datetime import datetime
import random
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Configure Flask to use server-side sessions
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True if you're using HTTPS
app.secret_key = "your_secret_key"

Session(app)


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    conn = sqlite3.connect("users.db", isolation_level=None)
    return conn


@app.route("/")
def home():
    return render_template("home.html")


# This route handles both GET and POST requests
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Check user credentials in the database
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT account_number FROM customer_info WHERE username = ? AND password = ?",
            (username, password),
        )
        user = cursor.fetchone()

    if user:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        session["sender_id"] = session_id  # Store sender_id in session
        session["account_number"] = user[0]  # Store account number in session
        session["username"] = username  # Store username in session
        print(f"Session ID (sender_id) stored in session: {session_id}")
        print(f"Account number stored in session: {user[0]}")
        print(f"Username stored in session: {username}")

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "sender_id": session_id,
                    "account_number": user[0],
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in by validating the session
    sender_id = session.get("sender_id")
    account_number = session.get("account_number")

    if not sender_id or not account_number:
        return redirect(url_for("login"))

    # Assuming the username is also stored in session
    username = session.get(
        "username", "User"
    )  # Default to 'User' if username is not found

    print(f"Session ID (sender_id): {sender_id}")
    print(f"Account number: {account_number}")

    # Render dashboard.html with username and account number
    return render_template(
        "dashboard.html", username=username, account_number=account_number
    )


@app.route("/api/balance", methods=["GET"])
def get_balance():
    # Retrieve sender_id and account_number from the request
    sender_id = request.args.get("sender_id")
    account_number_from_request = request.args.get("account_number")
    print("Rasa Request Session ID: ", sender_id)
    print("Rasa Request Account Number: ", account_number_from_request)
    print("Flask Session ID:", session.get("sender_id"))
    # Check if sender_id in session matches the one provided
    if "sender_id" in session and session["sender_id"] == sender_id:
        account_number = session.get("account_number")
        if account_number:
            return fetch_balance_from_db(account_number)
    else:
        # If session sender_id does not match, use the account_number from the request
        if account_number_from_request:
            return fetch_balance_from_db(account_number_from_request)

    return jsonify({"message": "Invalid session or not logged in"}), 403


def fetch_balance_from_db(account_number):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT outstanding_balance FROM customer_info WHERE account_number = ?",
            (account_number,),
        )
        result = cursor.fetchone()

        if result:
            balance = result[0]
            return jsonify({"balance": balance}), 200
        else:
            return jsonify({"message": "Account not found"}), 404


@app.route("/api/user_data", methods=["GET"])
def get_user_data():

    # Get the column and account_number from query parameters
    column = request.args.get("column")
    account_number = request.args.get("account_number")

    # Log the received data
    logger.info(f"Received column: {column}, account_number: {account_number}")

    if not column or not account_number:
        return jsonify({"error": "Column and account_number are required"}), 400

    # Whitelist of allowed columns
    allowed_columns = [
        "username",
        "cnic",
        "account_number",
        "account_title",
        "customer_name",
        "contact_number",
        "email",
        "ntn",
        "cif",
        "account_type_name",
        "account_type_code",
        "outstanding_balance",
        "date_of_birth",
        "address",
        "nationality",
        "city_residential",
        "registration_number",
        "father_name",
        "reward_points",
    ]

    # Check if the requested column is allowed
    if column not in allowed_columns:
        return jsonify({"error": "Invalid column"}), 400

    # Query the database
    try:
        conn = init_db()
        cursor = conn.cursor()
        query = f"SELECT {column} FROM customer_info WHERE account_number = ?"
        cursor.execute(query, (account_number,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify({column: result[0]})
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        logger.error(f"Database query error: {e}")
        return jsonify({"error": "Internal server error"}), 500


def query_user_info(account_number, fields):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()

        query = (
            f"SELECT {', '.join(fields)} FROM customer_info WHERE account_number = ?"
        )
        cursor.execute(query, (account_number,))
        result = cursor.fetchone()

        if result:
            return dict(zip(fields, result))
        else:
            return {}


@app.route("/api/personal_info", methods=["GET"])
def get_personal_info():
    account_number = request.args.get("account_number")
    fields = request.args.get("fields").split(",")

    if not account_number or not fields:
        return jsonify({"error": "Missing account number or fields"}), 400

    data = query_user_info(account_number, fields)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({"error": "No data found"}), 404


# Fetch all branch names from the database
def fetch_all_branch_names():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM branch_info LIMIT 5")
    branch_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return branch_names


# Fetch branch info by identifier (using fuzzy matching if needed)
def fetch_branch_info(identifier, is_code=True):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if is_code:
        query = "SELECT * FROM branch_info WHERE code = ? LIMIT 5"
        cursor.execute(query, (identifier,))
    else:
        # Fuzzy match with branch names from the database
        branch_names = fetch_all_branch_names()
        closest_match = process.extractOne(identifier, branch_names)

        if closest_match:
            query = "SELECT * FROM branch_info WHERE name = ? LIMIT 5"
            cursor.execute(query, (closest_match[0],))
        else:
            conn.close()
            return None

    result = cursor.fetchone()
    conn.close()
    return result


# API endpoint to get a particular branch info
@app.route("/api/branch", methods=["GET"])
def get_branch_info():
    identifier = request.args.get("identifier")
    is_code = request.args.get("is_code", "true").lower() == "true"
    branch_info = fetch_branch_info(identifier, is_code)
    if branch_info:
        return jsonify(branch_info)
    else:
        return jsonify({"error": "Branch not found"}), 404


# Fetch branches by region
def fetch_branches_by_region(region, sat_open=None):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if sat_open:
        query = "SELECT * FROM branch_info WHERE region = ? AND sat_open = ? LIMIT 5"
        cursor.execute(query, (region, sat_open))
    else:
        query = "SELECT * FROM branch_info WHERE region = ? LIMIT 5"
        cursor.execute(query, (region,))

    branches = cursor.fetchall()
    conn.close()
    return branches


# API endpoint to get branches by region
@app.route("/api/branches", methods=["GET"])
def get_branches_by_region():
    region = request.args.get("region")
    sat_open = request.args.get("sat_open", None)
    branches = fetch_branches_by_region(region, sat_open)
    if branches:
        return jsonify(branches)
    else:
        return jsonify({"error": "No branches found"}), 404


# Fetch all branches open on Saturday
def fetch_all_sat_open_branches():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM branch_info WHERE sat_open = ? LIMIT 5"
    cursor.execute(query, (1,))
    branches = cursor.fetchall()
    conn.close()
    return branches


# API endpoint to get all Saturday-open branches
@app.route("/api/sat_open_branches", methods=["GET"])
def get_sat_open_branches():
    branches = fetch_all_sat_open_branches()
    return jsonify(branches)


@app.route("/api/check_payee", methods=["POST"])
def check_payee():
    data = request.json
    payee_account_number = data.get("payee_account_number")
    bank_name = data.get("bank_name")
    if not bank_name:
        bank_name = "allied bank"
    bank_name = fuzzy_match_bank_name(bank_name)
    conn = init_db()
    cursor = conn.cursor()
    print(bank_name)
    print(payee_account_number)
    # Check in Allied Bank if provided bank name is 'Allied Bank'
    if bank_name.lower() == "allied bank":
        result = cursor.execute(
            "SELECT account_title, account_number FROM customer_info WHERE account_number=?",
            (payee_account_number,),
        ).fetchone()
    else:
        # Check in centralised_banking for other banks
        result = cursor.execute(
            "SELECT name, account_number FROM centralized_banking WHERE account_number=? AND bank_name=?",
            (payee_account_number, bank_name),
        ).fetchone()

    conn.close()

    if result:
        return (
            jsonify(
                {
                    "status": "found",
                    "Account_Title": result[0],
                    "Account_Number": result[1],
                }
            ),
            200,
        )
    else:
        return jsonify({"status": "not found", "message": "Payee not found."}), 404


# API to handle Add Payee request
@app.route("/api/add_payee", methods=["POST"])
def add_payee():
    data = request.json

    # Extract data from the request
    iban = data.get("iban")
    payee_account_number = data.get("payee_account_number")
    bank_name = data.get("bank_name")
    account_number = data.get("account_number")  # User's account number
    nickname = data.get("payee_name")

    print(payee_account_number)

    # if iban:
    #     # Extract bank code and account number from IBAN
    #     bank_code = iban[4:8]
    #     payee_account_number = iban[8:]
    #     bank_name = get_bank_name_from_code(bank_code)

    bank_name = fuzzy_match_bank_name(bank_name)
    print(bank_name)
    # Validate required fields
    if not payee_account_number or not bank_name:
        return (
            jsonify({"status": "error", "message": "Missing required information"}),
            400,
        )

    conn = init_db()
    cursor = conn.cursor()

    # Check if payee already exists
    cursor.execute(
        "SELECT * FROM payees_info WHERE account_number = ? AND payee_account_number = ?",
        (account_number, payee_account_number),
    )
    payee = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM payees_info WHERE account_number = ? AND nickname = ?",
        (account_number, nickname),
    )
    payee2 = cursor.fetchone()
    if payee2:
        # Payee already exists, return details
        return (
            jsonify(
                {
                    "status": "exists",
                    "message": f"Nickname already exists with this account: {payee2[1]}, Account Number: {payee2[2]}, Bank: {payee2[4]}",
                }
            ),
            200,
        )

    if payee:
        # Payee already exists, return details
        return (
            jsonify(
                {
                    "status": "exists",
                    "message": f"Payee already exists: {payee[1]}, Account Number: {payee[2]}, Bank: {payee[4]}",
                }
            ),
            200,
        )
    else:
        if bank_name.lower() == "allied bank":
            payee_name = cursor.execute(
                "SELECT account_title FROM customer_info WHERE account_number=?",
                (payee_account_number,),
            ).fetchone()
            payee_name = payee_name[0] if payee_name else None
            # Insert new payee
            if payee_name:
                cursor.execute(
                    "INSERT INTO payees_info (account_number, payee_name, payee_account_number, iban, bank_name, nickname) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        account_number,
                        payee_name,
                        payee_account_number,
                        iban,
                        bank_name,
                        nickname,
                    ),
                )
                conn.commit()
                conn.close()
                return (
                    jsonify(
                        {
                            "status": "added",
                            "message": f"Payee {payee_name} has been successfully added",
                        }
                    ),
                    201,
                )

            else:
                return (
                    jsonify(
                        {
                            "status": "Not Found",
                            "message": f"Payee is not present in Allied Bank Database.",
                        }
                    ),
                    200,
                )
        else:
            print("PAYEE", payee_account_number)
            query = "SELECT name,iban FROM centralized_banking WHERE account_number=?"
            cursor.execute(query, (payee_account_number,))
            result = cursor.fetchone()
            payee_name = result[0] if result else None
            iban = result[1] if result else None
            if payee_name:
                cursor.execute(
                    "INSERT INTO payees_info (account_number, payee_name, payee_account_number, iban, bank_name, nickname) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        account_number,
                        payee_name,
                        payee_account_number,
                        iban,
                        bank_name,
                        nickname,
                    ),
                )
                conn.commit()
                conn.close()
                return (
                    jsonify(
                        {
                            "status": "added",
                            "message": f"Payee {payee_name} has been successfully added",
                        }
                    ),
                    201,
                )
            else:
                return (
                    jsonify(
                        {
                            "status": "Not Found",
                            "message": f"Payee is not present, you entered wrong details.",
                        }
                    ),
                    200,
                )


def get_bank_name_from_code(bank_code):
    # Map bank codes to bank names for Pakistani banks
    bank_code_map = {
        "HABL": "Habib Bank Limited",
        "UNBL": "United Bank Limited",
        "ALBL": "Allied Bank",
        "NBPK": "National Bank of Pakistan",
        "BAFL": "Bank Alfalah",
        "MCBL": "MCB Bank",
        "FAYB": "Faysal Bank",
        "MZNB": "Meezan Bank",
        "BOPK": "Bank of Punjab",
        "SCPK": "Standard Chartered Pakistan",
    }
    return bank_code_map.get(bank_code, "Unknown Bank")


def fuzzy_match_bank_name(input_bank_name):
    # List of valid bank names
    bank_names = [
        "Habib Bank Limited",
        "United Bank Limited",
        "Allied Bank",
        "National Bank of Pakistan",
        "Bank Alfalah",
        "MCB Bank",
        "Faysal Bank",
        "Meezan Bank",
        "Bank of Punjab",
        "Standard Chartered Pakistan",
    ]

    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(input_bank_name, bank_names)

    # Set a threshold for an acceptable match score
    if score >= 90:
        return best_match
    else:
        return "Unknown Bank"


@app.route("/api/remove_payee", methods=["POST"])
def remove_payee():
    data = request.json

    # Extract data from the request
    account_number = data.get("account_number")
    payee_account_number = data.get("payee_account_number")

    if not account_number or not payee_account_number:
        return (
            jsonify({"status": "error", "message": "Missing required information"}),
            400,
        )

    conn = init_db()
    cursor = conn.cursor()

    # Check if the payee exists
    cursor.execute(
        "SELECT * FROM payees_info WHERE account_number = ? AND payee_account_number = ?",
        (account_number, payee_account_number),
    )
    payee = cursor.fetchone()

    if payee:
        cursor.execute(
            "DELETE FROM payees_info WHERE account_number = ? AND payee_account_number = ?",
            (account_number, payee_account_number),
        )
        conn.commit()
        conn.close()
        return (
            jsonify(
                {
                    "status": "removed",
                    "message": f"Payee {payee[1]} has been successfully added",
                }
            ),
            200,
        )
    else:
        conn.close()
        return jsonify({"status": "not found", "message": "Payee not found."}), 404


# def get_transactions(account_number, limit=None, start_date=None, end_date=None, category=None):
#     conn = sqlite3.connect('users.db')
#     cursor = conn.cursor()
#
#     # Base query
#     query = """
#     SELECT reference_id, "from", "to", amount, type, dateTime, category
#     FROM transactions_info
#     WHERE ("from" = ? OR "to" = ?)
#     """
#     params = [account_number, account_number]
#
#
#     # Add category filter if provided
#     if category:
#         query += " AND category = ?"
#         params.append(category)
#
#     # Execute the query
#     cursor.execute(query, params)
#     transactions = cursor.fetchall()
#     conn.close()
#
#     # Filter by dates
#     transactions = [
#         tx for tx in transactions
#         if (not start_date or datetime.strptime(tx[5], '%d/%m/%Y %H:%M:%S') >= datetime.strptime(start_date, '%d/%m/%Y')) and
#            (not end_date or datetime.strptime(tx[5], '%d/%m/%Y %H:%M:%S') <= datetime.strptime(end_date, '%d/%m/%Y'))
#     ]
#
#     # Sort and apply limit
#     transactions = sorted(transactions, key=lambda x: datetime.strptime(x[5], '%d/%m/%Y %H:%M:%S'), reverse=True)
#     if limit:
#         transactions = transactions[:limit]
#
#     return transactions
#
#
# @app.route('/api/transactions', methods=['GET'])
# def fetch_transactions():
#     account_number = request.args.get('account_number')
#     start_date = request.args.get('start_date', default=None)
#     end_date = request.args.get('end_date', default=None)
#     limit = request.args.get('limit', default=None, type=int)
#     category = request.args.get('category', default=None)
#
#     if not account_number:
#         return jsonify({'error': 'Account number is required'}), 400
#
#     # Call get_transactions with all parameters
#     transactions = get_transactions(account_number, limit, start_date, end_date, category)
#
#     if not transactions:
#         return jsonify({'message': 'No transactions found'}), 404
#
#     # Convert transactions to dictionary format
#     transactions_list = [
#         {
#             'reference_id': tx[0],
#             'from': tx[1],
#             'to': tx[2],
#             'amount': tx[3],
#             'type': tx[4],
#             'dateTime': tx[5],
#             'category': tx[6]
#         }
#         for tx in transactions
#     ]
#
#     return jsonify(transactions_list)


def get_transactions(
    account_number, limit=None, start_date=None, end_date=None, category=None
):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Base query
    query = """
    SELECT reference_id, "from", "to", amount, type, dateTime, category 
    FROM transactions_info 
    WHERE ("from" = ? OR "to" = ?)
    """
    params = [account_number, account_number]

    # Add date filters if provided
    if start_date and end_date:
        query += " AND dateTime BETWEEN ? AND ?"
        start_date_formatted = f"{start_date} 00:00:00"
        end_date_formatted = f"{end_date} 23:59:59"
        params.extend([start_date_formatted, end_date_formatted])
    elif start_date:
        query += " AND dateTime >= ?"
        start_date_formatted = f"{start_date} 00:00:00"
        params.append(start_date_formatted)
    elif end_date:
        query += " AND dateTime <= ?"
        end_date_formatted = f"{end_date} 23:59:59"
        params.append(end_date_formatted)

    # Add category filter if provided
    if category:
        query += " AND category = ?"
        params.append(category)

    # Execute the query
    print(f"Executing SQL Query: {query} with params: {params}")
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()

    transactions = [
        tx
        for tx in transactions
        if (
            not start_date
            or datetime.strptime(tx[5], "%d/%m/%Y %H:%M:%S")
            >= datetime.strptime(start_date_formatted, "%d/%m/%Y %H:%M:%S")
        )
        and (
            not end_date
            or datetime.strptime(tx[5], "%d/%m/%Y %H:%M:%S")
            <= datetime.strptime(end_date_formatted, "%d/%m/%Y %H:%M:%S")
        )
    ]

    # Sort and apply limit
    transactions = sorted(
        transactions,
        key=lambda x: datetime.strptime(x[5], "%d/%m/%Y %H:%M:%S"),
        reverse=True,
    )
    if limit:
        transactions = transactions[:limit]

    return transactions


@app.route("/api/transactions", methods=["GET"])
def fetch_transactions():
    account_number = request.args.get("account_number")
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    limit = request.args.get("limit", default=None, type=int)
    category = request.args.get("category", default=None)

    print(f"Start Date: {start_date}, End Date: {end_date}")

    if not account_number:
        return jsonify({"error": "Account number is required"}), 400

    # Call get_transactions with all parameters
    transactions = get_transactions(
        account_number, limit, start_date, end_date, category
    )

    if not transactions:
        return jsonify({"message": "No transactions found"}), 200

    # Convert transactions to dictionary format
    transactions_list = [
        {
            "reference_id": tx[0],
            "from": tx[1],
            "to": tx[2],
            "amount": tx[3],
            "type": tx[4],
            "dateTime": tx[5],
            "category": tx[6],
        }
        for tx in transactions
    ]

    return jsonify(transactions_list)


# Database connection helper
def connect_db():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS otp (
                account_number TEXT PRIMARY KEY,
                otp INTEGER
            )
        """
    )
    conn.commit()
    return conn


# @app.route('/api/check_payee_info', methods=['POST'])
# def check_payee_info():
#     account_number = request.json.get("account_number")
#     payee_number = request.json.get("payee_account_number")
#
#     conn = connect_db()
#     cursor = conn.cursor()
#
#     # Check if payee exists for the given account number and nickname
#     cursor.execute("""
#         SELECT payee_account_number, payee_name, bank_name
#         FROM payees_info
#         WHERE account_number = ?  AND payee_account_number = ?
#     """, (account_number, payee_number))
#
#     payee = cursor.fetchone()
#     conn.close()
#
#     if payee:
#         return jsonify({
#             "status": "found",
#             "account_title": payee[1],
#             "account_number": payee[0],
#             "bank_name": payee[2]
#         })
#     else:
#         return jsonify({"status": "not_found", "message": "No payee found with this nickname."})


@app.route("/api/check_payee_info", methods=["POST"])
def check_payee_info():
    account_number = request.json.get("account_number")
    to_account = request.json.get("payee_account_number")

    conn = connect_db()
    cursor = conn.cursor()

    if to_account.isdigit():  # Check if 'to_account' is numeric
        # If numeric, use the existing logic to find by account number
        cursor.execute(
            """
            SELECT payee_account_number, payee_name, bank_name
            FROM payees_info
            WHERE account_number = ? AND payee_account_number = ?
        """,
            (account_number, to_account),
        )
    else:
        # If it's a string, use the nickname to find the payee
        cursor.execute(
            """
            SELECT payee_account_number, payee_name, bank_name
            FROM payees_info
            WHERE account_number = ? AND nickname = ?
        """,
            (account_number, to_account),
        )

    payee = cursor.fetchone()
    conn.close()

    if payee:
        return jsonify(
            {
                "status": "found",
                "account_title": payee[1],
                "account_number": payee[0],
                "bank_name": payee[2],
            }
        )
    else:
        return jsonify(
            {
                "status": "not_found",
                "message": "No payee found with this account number or nickname.",
            }
        )


@app.route("/api/customer_info", methods=["GET"])
def get_customer_info():
    account_number = request.args.get("to_account")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_name FROM customer_info WHERE account_number = ?",
        (account_number,),
    )
    customer = cursor.fetchone()
    conn.close()

    if customer:
        return jsonify({"customer_name": customer[0]})
    return jsonify({"error": "Account not found"}), 404


@app.route("/api/centralized_data", methods=["GET"])
def get_centralized_data():
    account_number = request.args.get("to_account")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM centralized_banking WHERE account_number = ?",
        (account_number,),
    )
    data = cursor.fetchone()
    conn.close()

    if data:
        return jsonify({"name": data[0]})
    return jsonify({"error": "Account not found"}), 404


@app.route("/api/generate_otp", methods=["POST"])
def generate_otp():
    account_number = request.json.get("account_number")
    otp = random.randint(1000, 9999)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
                CREATE TABLE IF NOT EXISTS otp (
                    account_number TEXT PRIMARY KEY,
                    otp INTEGER
                )
            """
    )
    cursor.execute(
        "INSERT OR REPLACE INTO otp (account_number, otp) VALUES (?, ?)",
        (account_number, otp),
    )
    conn.commit()
    conn.close()
    return jsonify({"otp": otp, "message": "OTP generated successfully."})


@app.route("/api/validate_otp", methods=["POST"])
def validate_otp():
    account_number = request.json.get("account_number")
    user_otp = request.json.get("otp")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT otp FROM otp WHERE account_number = ?", (account_number,))
    row = cursor.fetchone()
    conn.close()

    if row and str(row[0]) == str(user_otp):
        return jsonify({"status": "success", "message": "OTP validated successfully."})
    return jsonify({"status": "failure", "message": "Invalid OTP."})


@app.route("/api/transfer", methods=["POST"])
def transfer_funds():
    from_account = request.json.get("from_account")
    to_account = request.json.get("to_account")
    amount = float(request.json.get("amount"))

    conn = connect_db()
    cursor = conn.cursor()

    # Check sender's balance
    cursor.execute(
        "SELECT outstanding_balance FROM customer_info WHERE account_number = ?",
        (from_account,),
    )
    sender_balance = cursor.fetchone()

    if not sender_balance or sender_balance[0] < amount:
        conn.close()
        return jsonify({"status": "failure", "message": "Insufficient balance."})

    if to_account.isdigit():  # Check if 'to_account' is numeric
        # If numeric, use the existing logic to find by account number
        cursor.execute(
            """
                SELECT payee_account_number, payee_name, bank_name
                FROM payees_info
                WHERE account_number = ? AND payee_account_number = ?
            """,
            (from_account, to_account),
        )
    else:
        # If it's a string, use the nickname to find the payee
        cursor.execute(
            """
                SELECT payee_account_number, payee_name, bank_name
                FROM payees_info
                WHERE account_number = ? AND nickname = ?
            """,
            (from_account, to_account),
        )

    payee = cursor.fetchone()
    to_account = payee[0]
    # Perform the transfer
    cursor.execute(
        "UPDATE customer_info SET outstanding_balance = outstanding_balance - ? WHERE account_number = ?",
        (amount, from_account),
    )
    cursor.execute(
        "UPDATE customer_info SET outstanding_balance = outstanding_balance + ? WHERE account_number = ?",
        (amount, to_account),
    )

    # Log the transaction
    cursor.execute("SELECT MAX(sr) FROM transactions_info")
    max_sr = cursor.fetchone()[0]
    new_sr = (int(max_sr) + 1) if max_sr is not None else 1

    reference_id = str(
        random.randint(1000000000, 9999999999)
    )  # Generate random 10-digit reference ID
    transaction_type = "Debit"
    dateTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    category = "IBFT"
    description = f"IBFT transfer to account {to_account}"

    # Log the transaction
    cursor.execute(
        """INSERT INTO transactions_info (sr, reference_id, `from`, `to`, amount, type, dateTime, category, description)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            new_sr,
            reference_id,
            from_account,
            to_account,
            -amount,
            transaction_type,
            dateTime,
            category,
            description,
        ),
    )
    conn.commit()
    conn.close()

    return jsonify(
        {
            "status": "success",
            "message": f"Transfer of {amount} completed successfully.",
        }
    )


@app.route("/api/get_payees", methods=["GET"])
def get_payees():
    account_number = request.args.get("account_number")

    if not account_number:
        return jsonify({"error": "Account number is required"}), 400

    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row  # Allow us to fetch rows as dictionaries
        cursor = conn.cursor()

        # Query to get all payees associated with the given account number
        cursor.execute(
            """
            SELECT payee_name, payee_account_number, bank_name, nickname
            FROM payees_info
            WHERE account_number = ?
        """,
            (account_number,),
        )

        payees = cursor.fetchall()
        conn.close()

        if not payees:
            return jsonify({"message": "No payees found for this account."}), 404

        # Format the payees as a list of dictionaries
        payee_list = [dict(payee) for payee in payees]
        return jsonify({"status": "success", "payees": payee_list}), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/check_complaints", methods=["GET"])
def check_complaints():
    # Get the account number from the request arguments
    account_number = request.args.get("account_number")

    if not account_number:
        return (
            jsonify({"status": "failure", "message": "Account number is required."}),
            400,
        )

    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Query to get complaints for the provided account number
        cursor.execute(
            """
            SELECT complaint_id, description, status
            FROM complaints
            WHERE account_number = ?
        """,
            (account_number,),
        )

        # Fetch all complaints
        complaints = cursor.fetchall()

        # Close the connection
        conn.close()

        # Check if any complaints were found
        if not complaints:
            return jsonify(
                {
                    "status": "success",
                    "message": "No complaints found for this account.",
                }
            )

        # Format the response
        complaints_list = []
        for complaint in complaints:
            complaints_list.append(
                {
                    "complaint_id": complaint[0],
                    "description": complaint[1],
                    "status": complaint[2],
                }
            )

        return jsonify({"status": "success", "complaints": complaints_list})

    except sqlite3.Error as e:
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


@app.route("/api/register_complaint", methods=["POST"])
def register_complaint():
    # Get the account number and description from the request JSON
    data = request.get_json()
    account_number = data.get("account_number")
    description = data.get("description")

    if not account_number or not description:
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "Account number and description are required.",
                }
            ),
            400,
        )

    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Generate a new complaint ID if not provided
        complaint_id = data.get("complaint_id") or str(uuid.uuid4())
        status = "Active"

        # Debug prints to verify data
        print(
            f"Inserting Complaint: ID: {complaint_id}, Account: {account_number}, Description: {description}, Status: {status}"
        )

        # Insert the new complaint into the database
        cursor.execute(
            """
            INSERT INTO complaints (complaint_id, account_number, description, status)
            VALUES (?, ?, ?, ?)
        """,
            (complaint_id, account_number, description, status),
        )

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return jsonify(
            {
                "status": "success",
                "message": "Complaint registered successfully.",
                "complaint_id": complaint_id,
            }
        )

    except sqlite3.Error as e:
        # Log the error for debugging
        print(f"SQLite Error: {e}")
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


@app.route("/api/add_user_bill", methods=["POST"])
def add_user_bill():
    # Extract data from the request JSON
    data = request.get_json()
    account_number = data.get("account_number")
    bill_id = data.get("bill_id")
    nickname = data.get("nickname")

    # Validate that required fields are present
    if not all([account_number, bill_id, nickname]):
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "Account Number, Bill ID, and Nickname are required.",
                }
            ),
            400,
        )

    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Check if a bill with the same nickname is already added for the user
        cursor.execute(
            """
                    SELECT COUNT(*)
                    FROM user_bills
                    WHERE account_number = ? AND nickname = ?
                """,
            (account_number, nickname),
        )

        existing_bill_count = cursor.fetchone()[0]

        if existing_bill_count > 0:
            # If a bill with the same nickname already exists
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": f"A bill with the nickname '{nickname}' is already added. Please use a different nickname.",
                    }
                ),
                400,
            )

        # Insert the bill into user_bills table
        cursor.execute(
            """
            INSERT INTO user_bills (account_number, bill_id, nickname)
            VALUES (?, ?, ?)
        """,
            (account_number, bill_id, nickname),
        )

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return jsonify(
            {"status": "success", "message": "User bill added successfully."}
        )

    except sqlite3.Error as e:
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


@app.route("/api/pay_bill", methods=["POST"])
def pay_bill():
    try:
        # Get the request data
        data = request.get_json()
        account_number = data.get("account_number")
        bill_identifier = data.get("bill_identifier")

        if not account_number or not bill_identifier:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "Account number and bill identifier are required.",
                    }
                ),
                400,
            )

        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Determine if the identifier is a bill ID or a nickname
        if bill_identifier.isdigit():
            # Fetch bill information using the bill ID
            cursor.execute(
                """
                SELECT b.bill_id, b.amount, b.status, u.nickname, b.subcategory_account_number
                FROM bills_info b
                JOIN user_bills u ON b.bill_id = u.bill_id
                WHERE b.bill_id = ? AND u.account_number = ?
            """,
                (bill_identifier, account_number),
            )
        else:
            # Fetch bill information using the nickname
            cursor.execute(
                """
                SELECT b.bill_id, b.amount, b.status, u.nickname, b.subcategory_account_number
                FROM bills_info b
                JOIN user_bills u ON b.bill_id = u.bill_id
                WHERE u.nickname = ? AND u.account_number = ?
            """,
                (bill_identifier, account_number),
            )

        # Fetch the bill data
        bill = cursor.fetchone()

        # If no bill is found, return failure
        if not bill:
            conn.close()
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "Bill not found or incorrect account number.",
                    }
                ),
                404,
            )

        # Extract details from the fetched bill record
        bill_id, amount, status, nickname, subcategory_account_number = bill

        # Check if the bill is already paid
        if status.lower() == "paid":
            conn.close()
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": f"The bill with ID {bill_id} has already been paid.",
                    }
                ),
                400,
            )

        # Check if the user's account has enough balance
        cursor.execute(
            """
            SELECT outstanding_balance FROM customer_info WHERE account_number = ?
        """,
            (account_number,),
        )
        user_balance = cursor.fetchone()

        if not user_balance or user_balance[0] < amount:
            conn.close()
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "Insufficient balance to pay the bill.",
                    }
                ),
                400,
            )

        # Deduct the amount from the user's balance
        cursor.execute(
            """
            UPDATE customer_info
            SET outstanding_balance = outstanding_balance - ?
            WHERE account_number = ?
        """,
            (amount, account_number),
        )

        # Update the status of the bill to 'Paid'
        cursor.execute(
            """
            UPDATE bills_info
            SET status = 'Paid'
            WHERE bill_id = ?
        """,
            (bill_id,),
        )

        # Log the payment in the transactions table to maintain consistency with other entries
        transaction_id = str(uuid.uuid4())[
            :8
        ]  # Generating a simple 8 character transaction ID
        current_timestamp = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )  # Current timestamp in a readable format
        cursor.execute(
            """
                    SELECT MAX(sr) FROM transactions_info
                """
        )
        last_sr = cursor.fetchone()[0]
        new_sr = int(last_sr) + 1 if last_sr is not None else 1
        cursor.execute(
            """
            INSERT INTO transactions_info (sr, reference_id, `from`, `to`, amount, type, dateTime, category, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                new_sr,
                transaction_id,  # reference_id
                account_number,  # from_account
                subcategory_account_number,  # to_account (updated to use subcategory_account_number)
                amount,  # amount
                "Debit",  # type of transaction
                current_timestamp,  # dateTime of transaction
                "Bill Payment",  # category
                f"Bill Payment to {nickname}",  # description of the payment
            ),
        )

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        return jsonify(
            {
                "status": "success",
                "message": f"Payment of {amount} for bill '{nickname}' (ID: {bill_id}) has been completed successfully.",
                "transaction_id": transaction_id,
            }
        )

    except sqlite3.Error as e:
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


@app.route("/api/verify_bill", methods=["GET"])
def verify_bill():
    # Extract parameters from the request
    bill_id = request.args.get("bill_id")
    main_category = request.args.get("main_category")
    sub_category = request.args.get("sub_category")

    # Validate that the required parameters are present
    if not all([bill_id, main_category, sub_category]):
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "Bill ID, Main Category, and Sub Category are required.",
                }
            ),
            400,
        )

    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Query to verify the bill in the bills_info table
        cursor.execute(
            """
            SELECT amount, status
            FROM bills_info
            WHERE bill_id = ? AND main_category = ? AND sub_category = ?
        """,
            (bill_id, main_category, sub_category),
        )

        # Fetch bill information
        bill = cursor.fetchone()
        conn.close()

        if bill:
            # If the bill exists, return its details
            return jsonify(
                {"status": "found", "amount": bill[0], "bill_status": bill[1]}
            )
        else:
            return jsonify(
                {"status": "not_found", "message": "Bill not found in the database."}
            )

    except sqlite3.Error as e:
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


@app.route("/api/fetch_bill_details", methods=["GET"])
def fetch_bill_details():
    # Get the account number and bill identifier (can be bill_id or nickname) from the request arguments
    account_number = request.args.get("account_number")
    bill_identifier = request.args.get(
        "bill_identifier"
    )  # This could be either the bill ID or the nickname

    if not account_number or not bill_identifier:
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "Account number and bill identifier are required.",
                }
            ),
            400,
        )

    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Check if the bill_identifier is numeric (indicating it's likely a bill ID)
        if bill_identifier.isdigit():
            # Query to check if a bill exists for the provided account number and bill ID
            cursor.execute(
                """
                SELECT ub.bill_id, bi.main_category, bi.sub_category, bi.amount, bi.status
                FROM user_bills ub
                JOIN bills_info bi ON ub.bill_id = bi.bill_id
                WHERE ub.account_number = ? AND ub.bill_id = ?
            """,
                (account_number, bill_identifier),
            )

        else:
            # Query to check if a bill exists for the provided account number and bill nickname
            cursor.execute(
                """
                SELECT ub.bill_id, bi.main_category, bi.sub_category, bi.amount, bi.status
                FROM user_bills ub
                JOIN bills_info bi ON ub.bill_id = bi.bill_id
                WHERE ub.account_number = ? AND ub.nickname = ?
            """,
                (account_number, bill_identifier),
            )

        # Fetch the bill details
        bill_details = cursor.fetchone()
        conn.close()

        # Check if the bill was found
        if not bill_details:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "No bill found with the given identifier.",
                    }
                ),
                404,
            )

        # Format the response
        bill_id, main_category, sub_category, amount, status = bill_details
        response_data = {
            "status": "success",
            "bill_id": bill_id,
            "main_category": main_category,
            "sub_category": sub_category,
            "amount": amount,
            "bill_status": status,
        }

        return jsonify(response_data)

    except sqlite3.Error as e:
        return jsonify({"status": "failure", "message": f"An error occurred: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
