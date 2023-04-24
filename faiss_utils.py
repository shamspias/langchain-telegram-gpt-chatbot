import pickle
from langchain.vectorstores import FAISS as BaseFAISS


class FAISS(BaseFAISS):
    @staticmethod
    def load(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)


def load_faiss_index(file_path):
    return FAISS.load(file_path)
