from decimal import Decimal, InvalidOperation


class BusinessValidation:
    def __init__(self, response):
        self.response = response

    def parse_amount(self, value):

        if value is None:
            return None
        try:
            cleaned_value = str(value).replace("$", "").replace(",", "").strip()
            return Decimal(cleaned_value)
        except InvalidOperation:
            return None

    def check_total_calc(self, financial_details):
        errors = []
        subtotal = self.parse_amount(financial_details.get("subtotal"))
        discount = self.parse_amount(financial_details.get("discount"))
        tax_amount = self.parse_amount(financial_details.get("tax_amount"))
        total_amount = self.parse_amount(financial_details.get("total_amount"))
        amount_paid = self.parse_amount(financial_details.get("amount_paid"))
        balance_due = self.parse_amount(financial_details.get("balance_due"))
        shipping_charges = self.parse_amount(financial_details.get("shipping_charges"))

        # Validate subtotal and total amount
        if subtotal is not None and total_amount is not None:
            if total_amount < 0 or subtotal < 0:
                errors.append("Invalid financial amount")

        # Validate discount
        if discount is not None and subtotal is not None:
            if discount > subtotal:
                errors.append("Discount cannot exceed subtotal")

        # Validate payment
        if amount_paid is not None and total_amount is not None:
            if amount_paid > total_amount:
                errors.append("Amount paid exceeds total amount")

        # Validate balance
        if (
            balance_due is not None
            and total_amount is not None
            and amount_paid is not None
        ):
            if amount_paid + balance_due != total_amount:
                errors.append("Payment balance mismatch")
            # Validate total amount calculation
        if subtotal is not None and total_amount is not None:

            expected_total = subtotal

            if discount is not None:
                expected_total -= discount

            if tax_amount is not None:
                expected_total += tax_amount

            if shipping_charges is not None:
                expected_total += shipping_charges

            if abs(expected_total - total_amount) > Decimal("0.01"):
                errors.append("Total amount calculation mismatch")
        return errors

    def check(self):
        errors = self.check_total_calc(self.response["financial_details"])

        return {"is_valid": len(errors) == 0, "errors": errors}
