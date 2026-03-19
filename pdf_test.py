from langchain_community.document_loaders import PyPDFLoader

file_path = "./example_data/layout-parser-paper.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()
docs[0]