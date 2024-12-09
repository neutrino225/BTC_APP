from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet
from datetime import datetime,timedelta
from dateutil import parser
import random
import uuid
import string
import re


class ActionFetchMultipleDetails(Action):

    def name(self) -> Text:
        return "action_fetch_multiple_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract account number from session
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")

        if not account_number:
            dispatcher.utter_message(text="Account number not found. Please make sure you are logged in.")
            return []

        # Extract entities identified in the query
        entities = [entity["entity"] for entity in tracker.latest_message["entities"]]

        # Query the API for the requested details
        if entities:
            response = requests.get(f"http://127.0.0.1:5000/api/personal_info?account_number={account_number}&fields={','.join(entities)}")
            if response.status_code == 200:
                data = response.json()

                # Format the result with line breaks between details
                result = "<br>".join([f"<strong>{field.capitalize().replace('_', ' ')}:</strong> {value}" for field, value in data.items()])
                textout = f"Here are the details: \n\n {result} \n\n"
                print(textout)
                # Send the response to the user
                dispatcher.utter_message(text=f"Here are the details: <br><br>{result}</br></br>")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't fetch the details at this time.")
        else:
            dispatcher.utter_message(text="Please specify the details you want to know.")

        return []


class ActionGetBranchInfo(Action):

    def name(self) -> str:
        return "action_get_branch_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        # Extract relevant slots
        branch_name = tracker.get_slot('branch_name')
        column = tracker.get_slot('column')  # Could be a list of columns
        region = tracker.get_slot('region')
        sat_open = tracker.get_slot('sat_open')  # Slot for Saturday open

        # Base API URL
        api_base_url = "http://127.0.0.1:5000/api"

        # Column mapping
        column_map = {
            'contact': 4,
            'timings': 7,
            'address': 3,
            'type': 6
        }

        # Case 1: No branch name or region is provided
        if not branch_name and not region:
            dispatcher.utter_message(text="Which branch or region are you asking about?")
            return []

        # Case 2: User asks for Saturday-open branches
        if sat_open:
            if region:
                region = region.lower()
                url = f"{api_base_url}/branches?region={region}&sat_open=1"
            else:
                url = f"{api_base_url}/sat_open_branches"

            response = requests.get(url)

            if response.status_code == 200:
                branches = response.json()

                if branches:
                    branch_count = len(branches)
                    dispatcher.utter_message(
                        text=f"There are <strong>{branch_count}</strong> branches open on Saturday in {region or 'all regions'}:<br><br>")
                    for branch in branches:
                        dispatcher.utter_message(
                            text=f"<strong>{branch[2]}</strong><br><br>  <strong>Address:</strong> {branch[3]}<br> <strong>Timings:</strong> {branch[7]}<br><br>")
                else:
                    dispatcher.utter_message(text=f"No branches open on Saturday{' in ' + region if region else ''}.")
            else:
                dispatcher.utter_message(text="There was an error fetching the Saturday-open branch data.")
            return [SlotSet('sat_open', None), SlotSet('region', None)]

        # Case 3: User asks for branch info based on region
        if region:
            region = region.lower()
            url = f"{api_base_url}/branches?region={region}"
            response = requests.get(url)

            if response.status_code == 200:
                branches = response.json()

                if branches:
                    dispatcher.utter_message(text=f"Here are the branches in {region}:<br><br>")
                    for branch in branches:
                        dispatcher.utter_message(
                            text=f"<strong>{branch[2]}</strong><br><br> <strong>Address:</strong> {branch[3]} <br> <strong>Timings:</strong> {branch[7]}<br><br>")
                else:
                    dispatcher.utter_message(text=f"No branches found in {region}.")
            else:
                dispatcher.utter_message(text="There was an error fetching the branch data.")
            return [SlotSet('branch_name', None), SlotSet('region', None)]

        # Case 4: Multiple columns and branch name provided
        if column and branch_name:
            url = f"{api_base_url}/branch?identifier={branch_name}&is_code=false"
            response = requests.get(url)

            if response.status_code == 200:
                branch_info = response.json()

                if branch_info:
                    # Handle multiple columns
                    columns = column if isinstance(column, list) else [column]
                    response_text = f"Here are the details for <strong>{branch_name}</strong>:<br><br>"

                    for col in columns:
                        requested_column_index = column_map.get(col.lower())
                        if requested_column_index is not None:
                            requested_data = branch_info[requested_column_index]
                            response_text += f"<strong>{col.capitalize()}:</strong> {requested_data}<br>"
                        else:
                            response_text += f"<strong>{col.capitalize()}:</strong> Sorry, I don't have data for this column.<br>"

                    dispatcher.utter_message(text=response_text)
                else:
                    dispatcher.utter_message(text=f"Sorry, I don't have the information for {branch_name}.")
            else:
                dispatcher.utter_message(text="There was an error fetching the branch information.")
            return [SlotSet('branch_name', None), SlotSet('column', None)]

        # Case 5: General branch information without a specific column
        if branch_name:
            url = f"{api_base_url}/branch?identifier={branch_name}&is_code=false"
            response = requests.get(url)

            if response.status_code == 200:
                branch_info = response.json()

                if branch_info:
                    dispatcher.utter_message(text=f"<br><br><strong>Branch Info:</strong><br><br>\n"
                                                  f"<strong>Name:</strong> {branch_info[2]}<br>\n"
                                                  f"<strong>Address:</strong> {branch_info[3]}<br>\n"
                                                  f"<strong>Contact:</strong> {branch_info[4]}<br>\n"
                                                  f"<strong>Timings:</strong> {branch_info[7]}<br>\n"
                                                  f"<strong>Type:</strong> {branch_info[6]}<br>")
                else:
                    dispatcher.utter_message(text="Branch not found.")
            else:
                dispatcher.utter_message(text="There was an error fetching the branch information.")

        return [SlotSet('branch_name', None), SlotSet('column', None), SlotSet('sat_open', None)]


class ActionValidateAndAddPayee(Action):

    def name(self) -> Text:
        return "action_validate_and_add_payee"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Collect slots
        iban = tracker.get_slot('iban')
        payee_account_number = tracker.get_slot('payee_account_number')
        bank_name = tracker.get_slot('bank_name')
        payee_name = tracker.get_slot('payee_name')
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")  # User's account number
        confirmation_pending = tracker.get_slot('confirmation_pending')

        if not payee_name or len(payee_name.strip()) <= 1 or payee_name.isdigit():
            dispatcher.utter_message(text="Payee name must contain more than one character and cannot be just spaces or numbers. Payee Addition Failed!")
            return [SlotSet('payee_account_number', None), SlotSet('iban', None),SlotSet('bank_name', None),SlotSet('payee_name', None), SlotSet("confirmation_pending", False)]
        print(confirmation_pending)
        if not all([payee_account_number, bank_name]):
            dispatcher.utter_message(text="Some required information is missing.")
            return []

        # Prepare data payload for the API
        payload = {
            'iban': iban,
            'payee_account_number': payee_account_number,
            'bank_name': bank_name,
            'account_number': account_number,
            'payee_name' : payee_name
        }

        if confirmation_pending:
            # Handle User Confirmation
            confirmation = tracker.latest_message.get('intent').get('name')
            #confirmation = tracker.get_intent_of_latest_message()

            if confirmation == "affirm":
                # Call the Flask API
                response = requests.post('http://127.0.0.1:5000/api/add_payee', json=payload)
                result = response.json()

                if result['status'] == 'exists':
                    # If the payee exists, notify the user with the payee details
                    dispatcher.utter_message(result['message'])
                elif result['status'] == 'added':
                    # If the payee was successfully added, confirm it to the user
                    dispatcher.utter_message(result['message'])
                elif result['status'] == 'Not Found':
                    # If the payee was successfully added, confirm it to the user
                    dispatcher.utter_message(result['message'])
                else:
                    # Handle any errors
                    dispatcher.utter_message("An error occurred while processing your request. Please try again.")

            else:
                dispatcher.utter_message(text="Payee addition cancelled.")

            return [SlotSet('payee_account_number', None), SlotSet('iban', None), SlotSet('bank_name', None), SlotSet('payee_name', None), SlotSet("confirmation_pending", False)]

        response_check = requests.post('http://127.0.0.1:5000/api/check_payee', json=payload)
        result_check = response_check.json()

        if result_check['status'] == 'found':
            # Step 2: Prompt User for Confirmation
            dispatcher.utter_message(
                text=f"Payee found: {result_check['Account_Title']} with Account Number {result_check['Account_Number']}."
                     f"Do you want to add this payee?"
            )
            return [SlotSet("confirmation_pending", True)]
        elif result_check['status'] == 'not found':
            dispatcher.utter_message(result_check['message'])
            return [SlotSet('payee_account_number', None), SlotSet('iban', None),SlotSet('bank_name', None),SlotSet('payee_name', None), SlotSet("confirmation_pending", False)]


class ActionSubmitRemovePayee(Action):

    def name(self) -> Text:
        return "action_submit_remove_payee"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")  # User's account number
        payee_account_number = tracker.get_slot('payee_account_number')

        # Call the API to remove the payee
        payload = {
            'account_number': account_number,
            'payee_account_number': payee_account_number
        }
        response = requests.post('http://127.0.0.1:5000/api/remove_payee', json=payload)
        result = response.json()

        if result['status'] == 'removed':
            dispatcher.utter_message(result['message'])
        elif result['status'] == 'not found':
            dispatcher.utter_message(result['message'])
        else:
            dispatcher.utter_message("An error occurred. Please try again.")

        # Clear the slot
        return [SlotSet('payee_account_number', None)]


# class ActionFetchTransactions(Action):
#
#     def name(self) -> str:
#         return "action_fetch_transactions"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[str, Any]) -> List[Dict[str, Any]]:
#
#         account_number = tracker.latest_message.get('metadata', {}).get("account_number")
#         num_transactions = tracker.get_slot('num_transactions')
#
#         # Initialize variables
#         start_date, end_date, category = None, None, None
#
#         # Extract entities from user query
#         entities = tracker.latest_message.get("entities", [])
#         for entity in entities:
#             if entity["entity"] == "time":
#                 time_info = entity.get("additional_info", {})
#
#
#                 # Handle single date request (type: "value")
#                 if time_info.get("type") == "value":
#                     date_text = entity.get("text", "")
#                     try:
#                         # Try to parse the date in d/m/y format
#                         parsed_date = datetime.strptime(date_text, "%d/%m/%Y")
#                         start_date = end_date = parsed_date
#                     except ValueError:
#                         # If it fails, handle the other format (m/d/y)
#                         try:
#                             parsed_date = datetime.strptime(date_text, "%m/%d/%Y")
#                             # If it's in m/d/y, swap the day and month
#                             start_date = end_date = datetime(parsed_date.year, parsed_date.day, parsed_date.month)
#                         except ValueError:
#                             dispatcher.utter_message(
#                                 text="Sorry, I couldn't understand the date format. Please use dd/mm/yyyy format.")
#                             return []
#
#                 elif time_info.get("type") == "interval":
#                     # Extract start and end dates from the interval
#                     start_value = time_info.get("from", {}).get("value")  # This should be the ISO date string
#                     end_value = time_info.get("to", {}).get("value")  # This should be the ISO date string
#                     # Try parsing the start date
#                     if start_value:
#                         try:
#                             # Convert ISO string to datetime
#                             start_date = datetime.fromisoformat(start_value[:10])  # Get the date part (YYYY-MM-DD)
#                         except ValueError:
#                             dispatcher.utter_message(
#                                 text="Sorry, I couldn't understand the start date format in the interval. Please ensure it's correct."
#                             )
#                             return []
#
#                     # Try parsing the end date
#                     if end_value:
#                         try:
#                             # Convert ISO string to datetime
#                             end_date = datetime.fromisoformat(end_value[:10])  # Get the date part (YYYY-MM-DD)
#                         except ValueError:
#                             dispatcher.utter_message(
#                                 text="Sorry, I couldn't understand the end date format in the interval. "
#                                      "Please ensure it's correct."
#                             )
#                             return []
#
#             if entity["entity"] == "category":
#                 category = entity["value"]
#
#         print(entities)
#
#         # # Default date handling
#         # if start_date and not end_date:
#         #     end_date = datetime.now()
#         # elif end_date and not start_date:
#         #     start_date = end_date - timedelta(days=30)
#
#         if start_date==end_date:
#             end_date=None
#
#         formatted_start_date = start_date.strftime('%d/%m/%Y') if start_date else None
#         formatted_end_date = end_date.strftime('%d/%m/%Y') if end_date else None
#
#         # Prepare API query parameters
#         params = {"account_number": account_number}
#         if formatted_start_date:
#             params["start_date"] = formatted_start_date
#         if formatted_end_date:
#             params["end_date"] = formatted_end_date
#         if category:
#             params["category"] = category
#         if num_transactions:
#             params["limit"] = num_transactions
#
#         # Call the API
#         api_url = "http://127.0.0.1:5000/api/transactions"
#         response = requests.get(api_url, params=params)
#
#         # Process API response
#         if response.status_code == 200:
#             transactions = response.json()
#             message = "Here are your transactions:<br><br>" + "".join(
#                 f"<br><strong>Reference ID:</strong> {tx['reference_id']}<br>"
#                 f"<strong>From:</strong> {tx['from']}<br>"
#                 f"<strong>Amount:</strong> {float(tx['amount']):.2f}<br>"
#                 f"<strong>Type:</strong> {tx['type']}<br>"
#                 f"<strong>Date:</strong> {tx['dateTime']}<br>"
#                 f"<strong>Category:</strong> {tx['category']}<br><br>"
#                 for tx in transactions
#             )
#         else:
#             message = "No transactions found."
#
#         dispatcher.utter_message(text=message)
#         return [SlotSet('num_transactions', None), SlotSet('category', None)]

class ActionFetchTransactions(Action):

    def name(self) -> str:
        return "action_fetch_transactions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:

        # Extract account number and number of transactions
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        num_transactions = tracker.get_slot('num_transactions')

        # Initialize variables
        start_date, end_date, category = None, None, None

        # Extract entities from user query
        entities = tracker.latest_message.get("entities", [])
        for entity in entities:
            if entity["entity"] == "time":
                time_info = entity.get("additional_info", {})

                # Extracting the 'value' or 'from' and 'to' from Duckling entity
                if time_info.get("type") == "value":
                    iso_date = entity.get("value")
                    try:
                        # Parse date and convert to 'dd/mm/yyyy' format
                        parsed_date = datetime.fromisoformat(iso_date[:10])
                        start_date = end_date = parsed_date.strftime("%d/%m/%Y")
                    except ValueError:
                        dispatcher.utter_message(
                            text="Sorry, I couldn't understand the date format. Please use dd/mm/yyyy format.")
                        return []

                elif time_info.get("type") == "interval":
                    # Extract start and end dates from the interval
                    start_value = time_info.get("from", {}).get("value")
                    end_value = time_info.get("to", {}).get("value")

                    # Parse the start and end dates to 'dd/mm/yyyy' format
                    if start_value:
                        try:
                            start_date = datetime.fromisoformat(start_value[:10]).strftime("%d/%m/%Y")
                        except ValueError:
                            dispatcher.utter_message(
                                text="Sorry, I couldn't understand the start date format. Please ensure it's correct."
                            )
                            return []

                    if end_value:
                        try:
                            end_date = datetime.fromisoformat(end_value[:10]).strftime("%d/%m/%Y")
                        except ValueError:
                            dispatcher.utter_message(
                                text="Sorry, I couldn't understand the end date format. "
                                     "Please ensure it's correct."
                            )
                            return []

            if entity["entity"] == "category":
                category = entity["value"]

        # Handle default date range if 'last month' or 'last year' is given
        user_text = tracker.latest_message.get("text", "").lower()
        if "last month" in user_text:
            today = datetime.today()
            first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = (today.replace(day=1) - timedelta(days=1))
            start_date = first_day_last_month.strftime("%d/%m/%Y")
            end_date = last_day_last_month.strftime("%d/%m/%Y")
        elif "last year" in user_text:
            today = datetime.today()
            first_day_last_year = today.replace(year=today.year - 1, month=1, day=1)
            last_day_last_year = today.replace(year=today.year - 1, month=12, day=31)
            start_date = first_day_last_year.strftime("%d/%m/%Y")
            end_date = last_day_last_year.strftime("%d/%m/%Y")
        elif "last week" in user_text:
            # Get today's date
            today = datetime.today()
            # Calculate the start and end of the previous week
            # start_of_last_week = today - timedelta(days=today.weekday() + 7)
            # end_of_last_week = start_of_last_week + timedelta(days=6)
            # # Format dates as dd/mm/yyyy
            # start_date = start_of_last_week.strftime("%d/%m/%Y")
            # end_date = end_of_last_week.strftime("%d/%m/%Y")
            end_date = today.strftime("%d/%m/%Y")
            start_date = (today - timedelta(days=7)).strftime("%d/%m/%Y")

        # If only a single date is given, consider it as both start and end date
        if start_date and not end_date:
            end_date = start_date

        # Prepare API query parameters
        params = {"account_number": account_number}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if category:
            params["category"] = category
        if num_transactions:
            params["limit"] = num_transactions

        # Call the API
        api_url = "http://127.0.0.1:5000/api/transactions"
        response = requests.get(api_url, params=params)

        # Process API response
        if response.status_code == 200:
            transactions = response.json()
            if transactions:
                dispatcher.utter_message(json_message={
                    "type": "transactions",
                    "transactions": transactions
                })
            else:
                dispatcher.utter_message(json_message={
                    "type": "transactions",
                    "transactions": [],
                    "message": "No transactions for the given period."
                })
        else:
            dispatcher.utter_message(json_message={
                "type": "transactions",
                "transactions": [],
                "message": "Failed to fetch transactions. Please try again later."
            })

        return [SlotSet('num_transactions', None), SlotSet('category', None)]



# Check Payee Info in various sources
def _check_payee(from_account: str, to_account: str, dispatcher: CollectingDispatcher) -> bool:
    endpoints = [
        ("http://127.0.0.1:5000/api/check_payee_info", {"account_number": from_account, "payee_account_number": to_account})
        # ("http://127.0.0.1:5000/api/check_payee", {"payee_account_number": to_account}),
        # (f"http://127.0.0.1:5000/api/customer_info?account_number={to_account}", None),
        # (f"http://127.0.0.1:5000/api/centralized_data?account_number={to_account}", None),
    ]

    for url, payload in endpoints:
        try:
            response = requests.post(url, json=payload) if payload else requests.get(url)
            # print(url, payload)
            result = response.json()
            if response.status_code == 200 and result.get("status", "not_found") == "found":
                acc_no = result.get('account_number')
                title = result.get('account_title')
                bank = result.get('bank_name')
                dispatcher.utter_message(text=f"Account found: Account Number: {acc_no}, Account Title: {title}, Bank: {bank}. Proceeding...")
                print(result)
                return True
        except (requests.RequestException, ValueError):
            dispatcher.utter_message(text="Error accessing account information.")
            return False

    dispatcher.utter_message(text="Payee not found. Please Add the Payee first.")
    return False


# Generate OTP via API
def _generate_otp(from_account: str, dispatcher: CollectingDispatcher) -> str:
    try:
        response = requests.post("http://127.0.0.1:5000/api/generate_otp", json={"account_number": from_account})
        if response.status_code == 200:
            return response.json().get("otp")
    except requests.RequestException:
        dispatcher.utter_message(text="Failed to generate OTP. Please try again.")
    return ""


# Validate OTP via API
def _validate_otp(from_account: str, otp: str, dispatcher: CollectingDispatcher) -> bool:
    try:
        response = requests.post("http://127.0.0.1:5000/api/validate_otp", json={"account_number": from_account, "otp": otp})
        if response.status_code == 200 and response.json().get("status") == "success":
            return True
        dispatcher.utter_message(text="Invalid OTP. Please try again.")
    except requests.RequestException:
        dispatcher.utter_message(text="Error validating OTP.")
    return False


# Execute the Transfer via API
def _execute_transfer(from_account: str, to_account: str, amount: float, dispatcher: CollectingDispatcher) -> bool:
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/transfer",
            json={"from_account": from_account, "to_account": to_account, "amount": amount}
        )
        if response.status_code == 200 and response.json().get("status") == "success":
            dispatcher.utter_message(text=f"Transfer of {amount} to account {to_account} completed successfully.")
            return True
        dispatcher.utter_message(text="Transfer failed. Please try again.")
    except requests.RequestException:
        dispatcher.utter_message(text="Error executing transfer.")
    return False

'''
class ActionTransferFunds(Action):
    def name(self) -> Text:
        return "action_transfer_funds"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve slots and user message
        from_account = tracker.latest_message.get('metadata', {}).get("account_number")
        to_account = tracker.get_slot("to_account") or tracker.latest_message.get('text')
        transfer_amount = tracker.get_slot("transfer_amount")

        print("From: ", from_account,"\nTo: ", to_account,"\nAmount: ", transfer_amount)

        # Check Payee Information in different sources
        if not _check_payee(from_account, to_account, dispatcher):
            print("Payee not found")
            return []

        # Generate OTP
        otp = _generate_otp(from_account, dispatcher)
        if not otp:
            print("OTP cant be generated")
            return []

        dispatcher.utter_message(text=f"OTP generated: {otp}. Please provide it to proceed.")

        # Check if OTP is already in the slot (provided by user in previous turn)
        provided_otp = tracker.get_slot("otp")
        
        
        print(tracker.latest_message.get('text'))

        if not provided_otp:
            # Extract OTP from the latest message (if not already stored in slot)
            # provided_otp = tracker.latest_message.get('text', '').strip()
            print(f"Extracted OTP: {provided_otp}")

            # If OTP is not provided, prompt user to enter it
            if not provided_otp:
                dispatcher.utter_message(text="Please enter the OTP sent to you.")
                return [SlotSet("otp", None)]

            # Store the provided OTP in a slot for further use
            return [SlotSet("otp", provided_otp)]

        # Step 6: Validate OTP using API
        otp_valid = _validate_otp(from_account, provided_otp, dispatcher)
        print(provided_otp)

        if not otp_valid:
            dispatcher.utter_message(text="Invalid OTP. Please try again.")
            return [SlotSet("otp", None)]

        # Perform the transfer
        if not _execute_transfer(from_account, to_account, transfer_amount, dispatcher):
            print("Cant execute transfer")
            return []

        # Clear slots after successful transfer
        return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None)]
'''


class ActionTransferFunds(Action):
    def name(self) -> Text:
        return "action_transfer_funds"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve slots and user message
        from_account = tracker.latest_message.get('metadata', {}).get("account_number")
        to_account = tracker.get_slot("to_account") or tracker.latest_message.get('text')
        transfer_amount = tracker.get_slot("transfer_amount")
        waiting_otp = tracker.get_slot("waiting_for_otp")
        if transfer_amount:
            # Using regex to extract only numeric part (both integer and float) from the user input
            amount_match = re.findall(r'\d+\.?\d*', transfer_amount)
            if amount_match:
                transfer_amount = float(amount_match[0])
            else:
                dispatcher.utter_message(text="Invalid input. Please enter a valid amount for transfer.")
                return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None),
                        SlotSet("waiting_for_otp", False)]

        if int(transfer_amount) <= 0:
            dispatcher.utter_message(text=f"Wrong Input, Transfer failed. Please try again")
            return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None),
                    SlotSet("waiting_for_otp", False)]

        print("From: ", from_account, "\nTo: ", to_account, "\nAmount: ", transfer_amount)
        if not waiting_otp:
            # Check Payee Information in different sources
            if not _check_payee(from_account, to_account, dispatcher):
                print("Payee not found")
                return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None), SlotSet("waiting_for_otp",False)]

            # Generate OTP
            otp = _generate_otp(from_account, dispatcher)
            if not otp:
                print("OTP cant be generated")
                return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None), SlotSet("waiting_for_otp",False)]

            dispatcher.utter_message(text=f"OTP generated: {otp}. Please provide it to proceed.")
            return [SlotSet("waiting_for_otp",True)]
        if waiting_otp:
            # Check if OTP is already in the slot (provided by user in previous turn)
            provided_otp = tracker.get_slot('otp')

            print(tracker.latest_message.get('text'))

            if not provided_otp:
                # Extract OTP from the latest message (if not already stored in slot)
                # provided_otp = tracker.latest_message.get('text', '').strip()
                print(f"Extracted OTP: {provided_otp}")

                # If OTP is not provided, prompt user to enter it
                if not provided_otp:
                    dispatcher.utter_message(text="Please enter the OTP sent to you.")
                    return [SlotSet("otp", None)]

                # Store the provided OTP in a slot for further use
                return [SlotSet("otp", provided_otp)]

            # Step 6: Validate OTP using API
            otp_valid = _validate_otp(from_account, provided_otp, dispatcher)
            print(provided_otp)

            if not otp_valid:
                dispatcher.utter_message(text="Invalid OTP. Please try again.")
                return [SlotSet("otp", None)]

            # Perform the transfer
            if not _execute_transfer(from_account, to_account, transfer_amount, dispatcher):
                print("Cant execute transfer")
                return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None), SlotSet("waiting_for_otp",False)]

        # Clear slots after successful transfer
        return [SlotSet("otp", None), SlotSet("to_account", None), SlotSet("transfer_amount", None), SlotSet("waiting_for_otp",False)]

class ActionShowPayees(Action):
    def name(self) -> Text:
        return "action_show_payees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve account number from metadata or slots
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        if not account_number:
            dispatcher.utter_message(text="Account number is missing. Please log in to continue.")
            return []

        # API URL to fetch payees
        api_url = f"http://127.0.0.1:5000/api/get_payees?account_number={account_number}"

        try:
            # Make GET request to the API to fetch payees
            response = requests.get(api_url)

            # If the response status is OK (200), parse the payee details
            if response.status_code == 200:
                try:
                    # Attempt to parse the response as JSON
                    response_data = response.json()

                    # Verify the structure of the response
                    if "payees" in response_data and isinstance(response_data["payees"], list):
                        payees = response_data["payees"]

                        if not payees:
                            dispatcher.utter_message(text="No payees found for your account.")
                            return []

                        # Format the message with payee details
                        message = "<strong>Here are your payees:</strong><br><br>"
                        for payee in payees:
                            message += (f"<br><strong>Payee Name:</strong> {payee.get('payee_name', 'N/A')}<br>"
                                        f"<strong>Account Number:</strong> {payee.get('payee_account_number', 'N/A')}<br>"
                                        f"<strong>Bank Name:</strong> {payee.get('bank_name', 'N/A')}<br>"
                                        f"<strong>Nickname:</strong> {payee.get('nickname', 'N/A')}<br><br>")

                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text="Unexpected data format received from the server. Please try again later.")

                except ValueError:
                    dispatcher.utter_message(text="Failed to parse the response as JSON. Please try again later.")

            else:
                dispatcher.utter_message(text="Failed to retrieve payees. Please try again later.")

        except requests.RequestException as e:
            dispatcher.utter_message(text="An error occurred while retrieving payees. Please try again later.")
            print(f"RequestException: {str(e)}")

        return []


class ActionCheckComplaints(Action):
    def name(self) -> Text:
        return "action_check_complaints"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve account number from metadata or slots
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        if not account_number:
            dispatcher.utter_message(text="Account number is missing. Please log in to continue.")
            return []

        # API URL to check complaints
        api_url = f"http://127.0.0.1:5000/api/check_complaints?account_number={account_number}"

        try:
            # Make GET request to the API to fetch complaints
            response = requests.get(api_url)

            # If the response status is OK (200), parse the complaint details
            if response.status_code == 200:
                data = response.json()

                if data["status"] == "success":
                    complaints = data.get("complaints", [])

                    if not complaints:
                        dispatcher.utter_message(text="No complaints found for your account.")
                        return []

                    # Format the message with complaint details
                    message = "<strong>Here are your complaints:</strong><br><br>"
                    for complaint in complaints:
                        message += (f"<br><strong>Complaint ID:</strong> {complaint['complaint_id']}<br>"
                                    f"<strong>Description:</strong> {complaint['description']}<br>"
                                    f"<strong>Status:</strong> {complaint['status']}<br>")

                    dispatcher.utter_message(text=message)
                else:
                    dispatcher.utter_message(text=data.get("message", "Failed to retrieve complaints."))
            else:
                dispatcher.utter_message(text="Failed to retrieve complaints. Please try again later.")

        except requests.RequestException:
            dispatcher.utter_message(text="An error occurred while retrieving complaints. Please try again later.")

        return []

class ActionRegisterComplaint(Action):
    def name(self) -> Text:
        return "action_register_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the account number and complaint description from slots
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        complaint_description = tracker.get_slot("complaint_description")

        # Generate a unique complaint ID
        complaint_id = str(uuid.uuid4())

        # Prepare data to send to the API
        data = {
            "account_number": account_number,
            "complaint_id": complaint_id,
            "description": complaint_description,
            "status": "Active"
        }
        print(data)

        # Call the API to register the complaint
        response = requests.post("http://127.0.0.1:5000/api/register_complaint", json=data)

        # Handle the response from the API
        if response.status_code == 200:
            dispatcher.utter_message(text=f"Your complaint has been registered successfully with Complaint ID: {complaint_id}.")
        else:
            dispatcher.utter_message(text="There was an issue registering your complaint. Please try again later.")

        # Clear the slot after registering the complaint
        return [SlotSet("complaint_description", None)]


class ActionAddBill(Action):
    def name(self) -> Text:
        return "action_add_bill"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extracting required information from slots
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        main_category = tracker.get_slot("main_category")
        sub_category = tracker.get_slot("sub_category")
        bill_id = tracker.get_slot("bill_id")
        nickname = tracker.get_slot("bill_nickname")

        # Verify if all necessary slots are filled
        if not all([account_number, main_category, sub_category, bill_id, nickname]):
            dispatcher.utter_message(text="Missing information. Please provide all the necessary bill details.")
            return []

        # API to verify if the bill exists in bills_info
        verify_bill_url = "http://127.0.0.1:5000/api/verify_bill"
        response = requests.get(verify_bill_url, params={"bill_id": bill_id, "main_category": main_category, "sub_category": sub_category})

        # Check if the bill exists
        if response.status_code == 200:
            bill_data = response.json()
            if bill_data["status"] == "found":
                # The bill exists, ask user for confirmation to add it
                dispatcher.utter_message(
                    text=f"Bill found: {main_category} - {sub_category}, Bill ID: {bill_id}, Amount: {bill_data['amount']}. Do you want to add this bill?")
                return [SlotSet("bill_confirmation_pending", True), SlotSet("main_category", None), SlotSet("sub_category", None)]
            else:
                dispatcher.utter_message(text="The specified bill does not exist. Please check the details and try again.")
                return [
                    SlotSet("main_category", None),
                    SlotSet("sub_category", None),
                    SlotSet("bill_id", None),
                    SlotSet("bill_nickname", None),
                    SlotSet("bill_confirmation_pending", False)
                ]
        else:
            dispatcher.utter_message(text="Unable to verify bill details at the moment. Please try again later.")
            return [
                SlotSet("main_category", None),
                SlotSet("sub_category", None),
                SlotSet("bill_id", None),
                SlotSet("bill_nickname", None),
                SlotSet("bill_confirmation_pending", False)
            ]


class ActionValidateAndAddUserBill(Action):
    def name(self) -> Text:
        return "action_validate_and_add_user_bill"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        bill_id = tracker.get_slot("bill_id")
        nickname = tracker.get_slot("bill_nickname")


        # API endpoint to add the bill to user_bills
        add_bill_url = "http://127.0.0.1:5000/api/add_user_bill"
        payload = {
            "account_number": account_number,
            "bill_id": bill_id,
            "nickname": nickname
        }

        # Call the API
        response = requests.post(add_bill_url, json=payload)

        # Handle the response
        if response.status_code == 200:
            dispatcher.utter_message(text=f"Bill with ID {bill_id} and nickname '{nickname}' has been successfully added to your account.")
        else:
            dispatcher.utter_message(text="There was an error adding the bill to your account. Please try again later.")

        return [SlotSet("bill_confirmation_pending", False),
            SlotSet("bill_identifier", None),
            SlotSet("bill_nickname", None),
            SlotSet("main_category", None),
            SlotSet("sub_category", None),
            SlotSet("bill_id", None)
        ]



class ActionFetchBillDetails(Action):

    def name(self) -> Text:
        return "action_fetch_bill_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve the bill identifier (can be bill ID or nickname) from the slot
        bill_identifier = tracker.get_slot("bill_identifier")
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")

        if not bill_identifier:
            dispatcher.utter_message(text="Please provide a valid bill identifier (ID or nickname) to proceed.")
            return []

        # Determine if the identifier is a bill ID (numeric) or nickname
        params = {"account_number": account_number, "bill_identifier": bill_identifier}

        # Prepare the API request to fetch bill details
        api_url = "http://127.0.0.1:5000/api/fetch_bill_details"

        try:
            response = requests.get(api_url, params=params)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                # Extract bill details
                amount = response_data.get("amount")
                status = response_data.get("bill_status")
                main_category = response_data.get("main_category")
                sub_category = response_data.get("sub_category")

                # If the bill is already paid
                if status.lower() == "paid":
                    dispatcher.utter_message(text=f"The bill '{bill_identifier}' has already been paid.")
                    return []

                # Ask the user to confirm payment
                dispatcher.utter_message(
                    text=(f"Bill Details:\n"
                          f"Category: {main_category}\n"
                          f"Sub-Category: {sub_category}\n"
                          f"Amount Due: {amount}\n"
                          f"Do you want to proceed with payment?")
                )
                return [SlotSet("bill_amount", amount), SlotSet("waiting_for_bill_payment_confirmation", True)]

            else:
                dispatcher.utter_message(text=response_data.get("message", "Unable to fetch the bill details. Please try again."))

        except requests.RequestException as e:
            dispatcher.utter_message(text=f"An error occurred while communicating with the server: {e}")

        return []


class ActionPayBill(Action):

    def name(self) -> Text:
        return "action_pay_bill"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve the necessary information from slots
        account_number = tracker.latest_message.get('metadata', {}).get("account_number")
        bill_identifier = tracker.get_slot("bill_identifier")
        bill_amount = tracker.get_slot("bill_amount")

        # Validate bill identifier and bill amount
        if not bill_identifier:
            dispatcher.utter_message(text="Please provide a valid bill identifier (nickname or ID).")
            return []

        if not bill_amount:
            dispatcher.utter_message(text="Unable to retrieve the bill amount. Please try again.")
            return []

        # Check if bill identifier is numeric or nickname
        params = {"account_number": account_number, "bill_identifier": bill_identifier}

        # Prepare the API URL to pay the bill
        api_url = "http://127.0.0.1:5000/api/pay_bill"

        # Try to execute the payment
        try:
            response = requests.post(api_url, json=params)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                dispatcher.utter_message(
                    text=f"Payment of {bill_amount} for bill '{bill_identifier}' has been completed successfully.")
                # Clear the slots after successful payment
                return [SlotSet("bill_identifier", None), SlotSet("bill_amount", None),
                        SlotSet("waiting_for_bill_payment_confirmation", False)]

            else:
                dispatcher.utter_message(
                    text=response_data.get("message", "Unable to complete the payment. Please try again."))

        except requests.RequestException as e:
            dispatcher.utter_message(text=f"An error occurred while communicating with the server: {e}")

        # If payment fails, return empty slot values for retry purposes
        return [SlotSet("waiting_for_bill_payment_confirmation", False)]




