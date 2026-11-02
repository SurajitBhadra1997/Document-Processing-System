from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from dependencies.doc_process import DocProcess
from schemas.doc_process import DocProcessResponse
from validation.business_validation import BusinessValidation

app = FastAPI()

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


@app.post("/process", response_model=DocProcessResponse)
async def process_doc(
    file: UploadFile = File(...),
    docservice: DocProcess = Depends(),
):

    extension = file.content_type.split("/")[-1]

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, detail="Only PDF, JPEG, JPG and PNG files are supported."
        )

    try:
        file_bytes = await file.read()

        result = await docservice.process_doc(file_bytes, extension)

        validate = BusinessValidation(result)

        validation_response = validate.check()

        print("validation_response", validation_response)

        return {
            "filename": file.filename,
            "status": "success",
            "data": result,
            "validation": validation_response,
            "humanreview": not validation_response["is_valid"],
        }

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    finally:
        await file.close()
