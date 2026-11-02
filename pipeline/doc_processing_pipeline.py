import json

import pymupdf

import pymupdf4llm

from pymupdf4llm.ocr import rapidtess_api

from langchain_groq import ChatGroq

from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage

import os

load_dotenv()


class DocProcessPipeline:

    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.0,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def process(self, file_bytes, extension):
        # print("---file----",self.file_bytes)

        # print("extension", extension)

        if extension == "pdf":
            with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
                markdown_context = pymupdf4llm.to_markdown(
                    doc, ocr_function=rapidtess_api.exec_ocr
                )
        else:

            image_doc = pymupdf.open(stream=file_bytes, filetype=extension)
            pdf_bytes = image_doc.convert_to_pdf()
            with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf_doc:
                markdown_context = pymupdf4llm.to_markdown(
                    pdf_doc, ocr_function=rapidtess_api.exec_ocr, force_ocr=True
                )

        # print("markdown_context", markdown_context)

        system_message = SystemMessage(content="""
You are an Intelligent Document Processing (IDP) assistant
specialized in extracting and classifying information from
invoices, bills, receipts and other expense documents.

Your responsibility is to extract accurate, structured information
from OCR-extracted document content.

GENERAL EXTRACTION RULES:

1. Identify the document type based on its content.
2. Identify the expense category based on the actual purpose
   of the expense.
3. Extract only information explicitly available in the document.
4. Never hallucinate, assume, calculate or infer missing values.
5. Preserve the original extracted values.
6. Maintain the exact JSON schema provided below.
7. Use null for missing scalar values.
8. Use an empty array when no line items are available.
9. Use an empty object when no additional details are available.
10. Do not add, remove or rename schema fields.
11. Return only valid JSON without Markdown or explanations.

EXPENSE CLASSIFICATION:

Classify expenses based on their actual purpose.

Examples:
- Restaurant bills: Meals & Entertainment
- Hotel receipts: Accommodation
- Flight or train tickets: Travel
- Taxi receipts: Local Transportation
- Fuel receipts: Fuel & Transportation
- Office supplies: Office Expenses
- Medical bills: Medical Expenses
- Freelance service invoices: Professional Services
- Utility bills: Utilities

These are examples, not mandatory mappings.
Return null if the expense category cannot be determined reliably.

MERCHANT DETAILS:

Extract the merchant, seller, service provider or vendor details.
Do not confuse merchant information with customer or employee details.

TRANSACTION DETAILS:

Extract document number, document date, due date, currency,
payment method and transaction reference wherever available.

FINANCIAL DETAILS:

Extract subtotal, discount, tax amount, total amount,
amount paid and balance due.

Preserve original monetary values and currency symbols.
Do not calculate missing financial values.
Do not assume missing tax or discount values are zero.

LINE ITEM EXTRACTION:

Extract each individual product, service or charge listed
in the document.

Use the following standard structure for every line item:

- description: Product, service or charge description.
- item_code: Product SKU, item code or service code.
- quantity: Number of products, units, hours, nights or other
  explicitly stated quantities.
- unit: Unit of measurement, such as pieces, kg, hours or nights.
- unit_price: Price per individual unit.
- discount: Discount applied to the individual line item.
- tax_amount: Tax associated with the individual line item.
- total_amount: Total amount associated with that line item.

LINE ITEM RULES:

1. Extract all identifiable line items.
2. Map values according to their actual meaning in the document,
   regardless of the original column names.
3. Associate each product or service with its corresponding
   quantity, unit price, discount, tax and total amount.
4. If only one product price is available, map it to unit_price
   when it clearly represents the individual product price.
5. If a line-item total is explicitly available, map it to
   total_amount.
6. If both unit price and total amount are available,
   extract both separately.
7. Do not confuse line-item amounts with invoice subtotal,
   overall tax, shipping charges or grand total.
8. Never calculate missing prices or amounts.
9. Do not leave a field null when its corresponding value
   is clearly available in the OCR content.
10. Use null when a value is genuinely unavailable or unreadable.

ADDITIONAL DETAILS:

Extract document-specific information that does not fit
into the predefined schema.

Examples:
- Hotel: check-in date, check-out date, room number.
- Flight: airline, flight number, departure, destination.
- Fuel: vehicle registration, fuel type.
- Restaurant: table number, guest count.

Only include explicitly available information.
Return an empty object if no additional information is available.

OUTPUT JSON SCHEMA:

{
    "document_type": null,
    "expense_category": null,
    "merchant_details": {
        "merchant_name": null,
        "merchant_address": null,
        "merchant_contact": null,
        "tax_registration_number": null
    },
    "transaction_details": {
        "document_number": null,
        "document_date": null,
        "due_date": null,
        "currency": null,
        "payment_method": null,
        "transaction_reference": null
    },
    "financial_details": {
        "subtotal": null,
        "discount": null,
        "tax_amount": null,
        "total_amount": null,
        "amount_paid": null,
        "balance_due": null
    },
    "line_items": [
        {
            "description": null,
            "item_code": null,
            "quantity": null,
            "unit": null,
            "unit_price": null,
            "discount": null,
            "tax_amount": null,
            "total_amount": null
        }
    ],
    "additional_details": {}
}

FINAL VALIDATION:

1. Verify that all identifiable line items are extracted.
2. Verify that available prices and quantities are mapped correctly.
3. Verify that financial values are mapped to the correct fields.
4. Ensure all required JSON keys are present.
5. Ensure the output is valid JSON.
6. Return only the JSON object.
""")

        human_message = HumanMessage(content=f"""
Extract and classify all available information from the
following OCR-extracted document content.

DOCUMENT CONTENT:

{markdown_context}
""")

        response = self.llm.invoke([system_message, human_message])

        serialized_response = json.loads(response.content)


        # print("serialized_response", serialized_response)

        return serialized_response
