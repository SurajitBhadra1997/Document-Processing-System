from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from dependencies.doc_process import DocProcess

app = FastAPI()

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}

@app.post("/process")
async def process_doc(file: UploadFile = File(...), docservice: DocProcess = Depends()):

    extension = file.content_type.split("/")[-1]

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, detail="Only PDF, JPEG, JPG and PNG files are supported."
        )

    try:
        file_bytes = await file.read()

        result = docservice.process_doc(file_bytes,extension)

        return {"filename": file.filename, "status": "success", "data": result}

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    finally:
        await file.close()
