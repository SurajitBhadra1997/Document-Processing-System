from pipeline.doc_processing_pipeline import DocProcessPipeline


class DocProcessService:
    def __init__(self, file_bytes,extension):
        self.file_bytes = file_bytes
        self.extension=extension

    async def start(self):
        pipeline = DocProcessPipeline()

        return pipeline.process(self.file_bytes,self.extension)
