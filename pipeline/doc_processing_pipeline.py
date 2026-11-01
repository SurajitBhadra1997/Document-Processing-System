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
specialized in employee expense document extraction.

Your responsibility is to extract structured information
from OCR-extracted document content.

Follow these rules:

1. Identify the document type and expense category based on the document content.
2. Extract only information explicitly available in the document.
3. Never hallucinate, assume, calculate, or infer missing values.
4. Map extracted information into the predefined JSON schema.
5. Maintain the exact schema for every document type.
6. Use null for missing scalar values.
7. Use an empty array when no line items are available.
8. Use an empty object when no additional details are available.
9. Preserve the original extracted values.
10. Do not add, remove, or rename schema fields.
11. Return only valid JSON without Markdown or explanations.

Always use this JSON structure:

{
    "document_type": null,
    "expense_category": null,
    "employee_details": {
        "employee_name": null,
        "employee_id": null,
        "department": null
    },
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
    "line_items": [],
    "additional_details": {}
}
""")

        human_message = HumanMessage(content=f"""
Extract structured information from the following
OCR-extracted document content.

Document Content:

{markdown_context}
""")

        response = self.llm.invoke([system_message, human_message])

        serialized_response = json.loads(response.content)

        # print("serialized_response", serialized_response)

        return serialized_response
