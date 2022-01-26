from bank_sync.Resources.resource import Resource
from bank_sync.APIs.utils.generate_code import get_code
from datetime import datetime


class Accounts(Resource):

    urls = {}

    def set_bank_id(self, bank_id):
        super().set_bank_id(bank_id)
        return self._set_urls()

    def _set_urls(self):

        self.urls = {
            "read": f"/accounts/{super().get_bank_id()}"
        }

        super().set_urls(self.urls)

        return self

    def balance(self, payload=None, endpoint='/get_balance'):

        return super().read(payload=payload, endpoint=f'{self.urls["read"]}{endpoint}')

    def mini_statement(self, payload=None, endpoint='/get_mini_statement'):

        return super().read(payload=payload, endpoint=f'{self.urls["read"]}{endpoint}')

    def full_statement(self, payload=None, endpoint='/get_full_statement'):

        return super().read(payload=payload, endpoint=f'{self.urls["read"]}{endpoint}')

    def account_validation(self, payload=None, endpoint='/get_validation'):

        return super().read(payload=payload, endpoint=f'{self.urls["read"]}{endpoint}')

    def account_transactions(self, payload=None, endpoint='/get_transactions'):

        return super().read(payload=payload, endpoint=f'{self.urls["read"]}{endpoint}')

    def serialize(self, payload=None, operation=None):

        super().set_operation(operation)

        data = {}

        if operation is None:
            return "Specify the operation: Resource.BALANCE, Resource.MINI_STATEMENT, Resource.FULL_STATEMENT, Resource.ACCOUNT_VALIDATION or Resource.ACCOUNT_TRANSACTIONS"

        if operation == super().BALANCE or operation == super().MINI_STATEMENT or operation == super().ACCOUNT_VALIDATION:

            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": f'{get_code(length=14)}'
                })
                data.update({
                    "AccountNumber": f'{payload.get("account_number", "")}'
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                data.update({
                    "country_code": payload.get("country_code", "")
                })
                data.update({
                    "account_number": payload.get("account_number", "")
                })
            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass

        elif operation == super().FULL_STATEMENT:
            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": f'{get_code(length=14)}'
                })
                data.update({
                    "AccountNumber": f'{payload.get("account_number", "")}'
                })
                data.update({
                    "StartDate": payload.get("start_date", "")
                })
                data.update({
                    "EndDate": payload.get("end_date", "")
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                data.update({
                    "country_code": payload.get("country_code", "")
                })
                data.update({
                    "account_number": f'{payload.get("account_number", "")}'
                })
                data.update({
                    "start_date": payload.get("start_date", "")
                })
                data.update({
                    "end_date": payload.get("end_date", "")
                })
                data.update({
                    "limit": payload.get("limit", 3)
                })
            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass

        elif operation == super().ACCOUNT_TRANSACTIONS:
            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": f'{get_code(length=14)}'
                })
                data.update({
                    "AccountNumber": f'{payload.get("account_number", "")}'
                })
                data.update({
                    "NoOfTransactions": f'{payload.get("limit", "")}'
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                pass

            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass

        data.update(payload.get("additional_properties", {}))

        return data

    def response(self):

        data = {}

        response_data = super().response()

        if super().get_operation() == super().BALANCE:

            if super().get_bank_id() == super().COOP:

                data["message"] = response_data.get("MessageDescription", "")
                data["code"] = response_data.get("MessageCode", "-1111111")
                data["reference"] = response_data.get("MessageReference", "")
                data["balance"] = response_data.get("AvailableBalance", "")

        elif super().get_operation() == super().MINI_STATEMENT or super().get_operation() == super().ACCOUNT_TRANSACTIONS:
             
            if super().get_bank_id() == super().COOP:

                data["message"] = response_data.get("MessageDescription", "")
                data["code"] = response_data.get("MessageCode", "-1111111")
                data["transactions"] = []

                transactions = response_data.get("Transactions", [])

                for i in range(len(transactions)):
                    transaction = {
                        "date": transactions[i].get("TransactionDate", ""),
                        "description": transactions[i].get("Narration", ""),
                    }

                    if transactions[i].get("TransactionType", "") == "D":
                        transaction["amount"] = transactions[i].get(
                            "DebitAmount", "")
                        transaction["type"] = "Debit"

                    elif transactions[i].get("TransactionType", "") == "C":
                        transaction["amount"] = transactions[i].get(
                            "CreditAmount", "")
                        transaction["type"] = "Credit"

                    data["transactions"].append(transaction)

            if super().get_operation() == super().MINI_STATEMENT:

                if super().get_bank_id() == super().EQUITY:

                    data["message"] = response_data.get("message", "")
                    data["code"] = f'{response_data.get("code", -111111)}'
                    data["transactions"] = []

                    transactions = response_data.get(
                        "data", {}).get("transactions", [])

                    for i in range(len(transactions)):

                        transaction = {
                            "date": datetime.fromisoformat(
                                transactions[i].get("date", "") + '+00:00'
                            ).strftime('%Y-%m-%d %H:%M:%S'),
                            "description": transactions[i].get("description", ""),
                            "amount":  transactions[i].get("amount", ""),
                            "type":  transactions[i].get("type", "")
                        }

                        data["transactions"].append(transaction)

        elif super().get_operation() == super().ACCOUNT_VALIDATION:

            if super().get_bank_id() == super().COOP:

                data["message"] = response_data.get("MessageDescription", "")
                data["code"] = response_data.get("MessageCode", "-1111111")

            elif super().get_bank_id() == super().EQUITY:

                data["message"] = response_data.get("message", "")
                data["code"] = f'{response_data.get("code", -111111)}'

        elif super().get_operation() == super().FULL_STATEMENT:

            if super().get_bank_id() == super().COOP:

                data["message"] = response_data.get("MessageDescription", "")
                data["code"] = response_data.get("MessageCode", "-1111111")
                data["transactions"] = []

                transactions = response_data.get("Transactions", [])

                for i in range(len(transactions)):
                    transaction = {
                        "date": transactions[i].get("TransactionDate", ""),
                        "description": transactions[i].get("Narration", ""),
                    }

                    if transactions[i].get("TransactionType", "") == "D":
                        transaction["amount"] = transactions[i].get(
                            "DebitAmount", "")
                        transaction["type"] = "Debit"

                    elif transactions[i].get("TransactionType", "") == "C":
                        transaction["amount"] = transactions[i].get(
                            "CreditAmount", "")
                        transaction["type"] = "Credit"
                    
                    transaction["reference"] = transactions[i].get("TransactionReference", "")
                    transaction["running_balance"] = transactions[i].get("RunningClearedBalance", "")

                    data["transactions"].append(transaction)

            elif super().get_bank_id() == super().EQUITY:

                data["message"] = response_data.get("message", "")
                data["code"] = f'{response_data.get("code", -111111)}'
                data["transactions"] = []

                transactions = response_data.get(
                    "data", {}).get("transactions", [])

                for i in range(len(transactions)):

                    transaction = {
                        "date": datetime.fromisoformat(
                            transactions[i].get("date", "") + '+00:00'
                        ).strftime('%Y-%m-%d %H:%M:%S'),
                        "description": transactions[i].get("description", ""),
                        "amount":  f'{transactions[i].get("amount", "")}',
                        "type":  transactions[i].get("type", ""),
                        "reference":  transactions[i].get("reference", ""),
                        "running_balance":  f'{transactions[i].get("runningBalance", {}).get("amount", "")}'
                    }

                    data["transactions"].append(transaction)


        if bool(data):
            return data

        return super().response()
