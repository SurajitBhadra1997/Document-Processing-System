import json

import pymupdf

import pymupdf4llm

from pymupdf4llm.ocr import rapidtess_api

from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()


class DocProcessPipeline:

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

        JSON_EXTRACTION_PROMPT = f"""You are an Intelligent Document Processing (IDP) system
designed to process employee-submitted expense documents.

Employees may submit different types of financial documents, including:

- Purchase invoices
- Restaurant bills
- Hotel bills
- Flight tickets
- Train tickets
- Taxi receipts
- Fuel receipts
- Medical bills
- Office supply receipts
- Utility bills
- Other business expense documents

Your task is to analyze the provided Markdown content and map all
available information into the predefined JSON schema below.

IMPORTANT:
Regardless of the uploaded document type, ALWAYS return the
same predefined JSON schema. Never change the schema structure.

PREDEFINED JSON SCHEMA:

{{
    "document_type": null,
    "expense_category": null,

    "employee_details": {{
        "employee_name": null,
        "employee_id": null,
        "department": null
    }},

    "merchant_details": {{
        "merchant_name": null,
        "merchant_address": null,
        "merchant_contact": null,
        "tax_registration_number": null
    }},

    "transaction_details": {{
        "document_number": null,
        "document_date": null,
        "due_date": null,
        "currency": null,
        "payment_method": null,
        "transaction_reference": null
    }},

    "financial_details": {{
        "subtotal": null,
        "discount": null,
        "tax_amount": null,
        "total_amount": null,
        "amount_paid": null,
        "balance_due": null
    }},

    "line_items": [],

    "additional_details": {{}}
}}

EXTRACTION RULES:

1. Extract only information explicitly available in the
   provided Markdown content.

2. Do not hallucinate, assume, calculate, or generate missing values.

3. Dynamically identify the document type and expense category
   based on the document content.

4. Always map extracted information into the corresponding
   predefined schema fields.

5. Do not change field names, remove fields, or add new
   top-level fields.

6. EMPLOYEE DETAILS:
   - Extract employee information only when explicitly available.
   - Do not assume the employee is the person named on the bill.
   - Use null when unavailable.

7. MERCHANT DETAILS:
   - Extract vendor, seller, restaurant, hotel or service provider
     information into merchant_details.

8. TRANSACTION DETAILS:
   - Map invoice numbers, receipt numbers, ticket numbers and
     transaction identifiers into document_number.
   - Extract document_date, due_date, currency, payment_method
     and transaction_reference when available.
   - Use null when unavailable.

9. FINANCIAL DETAILS:
   - Extract subtotal, discount, tax_amount, total_amount,
     amount_paid and balance_due.
   - Never calculate missing financial values.
   - Do not assume tax is zero when it is not mentioned.

10. LINE ITEMS:
    - Extract available purchased products, services, travel
      segments or other billable items.
    - Use this structure for each item:

      {{
          "description": null,
          "quantity": null,
          "unit_price": null,
          "amount": null
      }}

    - Use null for unavailable item-level values.
    - Return an empty list when no line items are available.

11. ADDITIONAL DETAILS:
    - Store document-specific information that does not fit
      into the predefined fields.
    - Examples:
        Hotel: check_in_date, check_out_date, room_number,
               number_of_nights.
        Flight: airline, flight_number, departure, destination,
                travel_date, passenger_name.
        Fuel: vehicle_number, fuel_type, fuel_quantity,
              price_per_unit.
        Restaurant: table_number, number_of_guests.
    - Only include information explicitly available.
    - Return an empty object when no additional details exist.

12. MISSING VALUES:
    - Use null for unavailable scalar fields.
    - Use an empty list for unavailable line_items.
    - Use an empty object for unavailable additional_details.
    - Do not omit any predefined schema fields.

13. DATA ACCURACY:
    - Preserve the original meaning and values.
    - Do not infer or correct unclear OCR text.
    - Do not introduce unsupported information.
    - Preserve the source values without performing calculations.

14. OUTPUT:
    - Return only valid JSON.
    - Do not include explanations, Markdown code blocks or comments.
    - Always follow the predefined schema.

INPUT:

DOCUMENT_MARKDOWN:
{markdown_context}

Extract the available information and return the structured JSON.
"""

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.0,
            max_retries=2,
        )

        response = llm.invoke(JSON_EXTRACTION_PROMPT)

        serialized_response = json.loads(response.content)

        # print("serialized_response", serialized_response)

        return serialized_response
