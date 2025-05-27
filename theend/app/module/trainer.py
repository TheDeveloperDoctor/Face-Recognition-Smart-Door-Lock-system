import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle
try:
    from Face_db import Database
except:
    from app.Face_db import Database

def train_knn():
    db = Database()
    X, y = db.get_all_embeddings()
    if not X:
        print("No embeddings found.")
        return
    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(X, y)
    with open("knn_model.pkl", "wb") as f:
        pickle.dump(knn, f)
    print("KNN model trained and saved.")