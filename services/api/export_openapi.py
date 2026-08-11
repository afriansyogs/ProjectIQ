import json
from app.main import app

if __name__ == "__main__":
    openapi_schema = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("Successfully exported openapi.json")
