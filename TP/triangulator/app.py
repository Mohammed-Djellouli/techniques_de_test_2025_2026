import os
from uuid import UUID
from urllib.error import HTTPError, URLError
from flask import Flask, Response, jsonify, request
from . import manager_client
from . import binary_utils
from . import core

app = Flask(__name__)

#récupération de l'url du PointSetManager 
POINT_SET_MANAGER_URL = os.environ.get(
    "POINT_SET_MANAGER_URL", "http://localhost:8080"
)

@app.route("/triangulation/<uuid:pointSetId>", methods=["GET"])
def get_triangulation(pointSetId: UUID):
    #prend un UUID
    #contacte le pointSetManager
    #calcule la triangulation et renvoie le résultat binaire


    
    print(f"Endpoint get_triangulation appelé avec l'ID: {pointSetId}")

    
    raise NotImplementedError("n'est pas implémenté")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)