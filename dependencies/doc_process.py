from services.doc_processing_service import DocProcessService


class DocProcess:
    def __init__(self):
        pass

    def process_doc(self, file_bytes: bytes,extension:str):
        service = DocProcessService(file_bytes,extension)

        return service.start()
