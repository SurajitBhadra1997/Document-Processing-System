## Intelligent Document Processing (IDP) – Employee Expense Management

An AI-powered document processing system that automates the extraction of structured information from employee-submitted expense documents such as invoices, restaurant bills, hotel receipts, flight tickets, and fuel bills.

The system uses OCR (Optical Character Recognition) to extract text from PDF and image-based documents, followed by an LLM (Groq) to identify, classify, and map the extracted information into a predefined JSON schema. The schema ensures consistent data output across different document types.

The extracted information includes employee details, merchant information, transaction details, financial information, line items, and document-specific attributes.

Technology stack:

- Python and FastAPI – Backend and API development
- PyMuPDF and PyMuPDF4LLM – PDF processing and Markdown extraction
- RapidOCR – OCR for image-based and scanned documents
- Groq LLM – Intelligent information extraction and schema mapping
- JSON – Standardized structured output

Key objective: Reduce manual data entry and provide a consistent foundation for automated employee expense processing, validation, and future human-in-the-loop review.
