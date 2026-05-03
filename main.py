from typing import Any

import yaml
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator

app = FastAPI(title="Kubernetes YAML CRUD API")

db: dict[str, dict[str, Any]] = {}


class YamlPayload(BaseModel):
    yaml_data: str

    @field_validator("yaml_data")
    def validate_yaml(cls, value):
        try:
            parsed = yaml.safe_load(value)
        except yaml.YAMLError:
            raise ValueError("Invalid YAML format")

        if not isinstance(parsed, dict):
            raise ValueError("YAML must be an object/map")

        required_fields = ["apiVersion", "kind", "metadata", "spec"]

        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(parsed["metadata"], dict):
            raise ValueError("metadata must be an object")

        if "name" not in parsed["metadata"]:
            raise ValueError("Missing required field: metadata.name")

        return value


class ImageUpdatePayload(BaseModel):
    container_name: str
    image: str


@app.post("/create", status_code=status.HTTP_201_CREATED)
def create_item(payload: YamlPayload):
    data = yaml.safe_load(payload.yaml_data)
    name = data["metadata"]["name"]

    if name in db:
        raise HTTPException(status_code=409, detail="Resource already exists")

    db[name] = data

    return {"message": "created", "name": name, "data": data}


@app.get("/items")
def get_all_items():
    return {"count": len(db), "items": db}


@app.get("/items/{name}")
def get_item(name: str):
    if name not in db:
        raise HTTPException(status_code=404, detail="Resource not found")

    return {"name": name, "data": db[name]}


@app.put("/items/{name}")
def update_item(name: str, payload: YamlPayload):
    if name not in db:
        raise HTTPException(status_code=404, detail="Resource not found")

    data = yaml.safe_load(payload.yaml_data)
    new_name = data["metadata"]["name"]

    if new_name != name:
        raise HTTPException(
            status_code=400,
            detail="metadata.name cannot be changed in PUT request"
        )

    db[name] = data

    return {"message": "updated", "name": name, "data": data}


@app.patch("/items/{name}/image")
def update_container_image(name: str, payload: ImageUpdatePayload):
    if name not in db:
        raise HTTPException(status_code=404, detail="Resource not found")

    data = db[name]
    containers = data.get("spec", {}).get("containers", [])

    for container in containers:
        if container.get("name") == payload.container_name:
            container["image"] = payload.image
            return {
                "message": "container image updated",
                "resource": name,
                "container": payload.container_name,
                "image": payload.image,
                "data": data,
            }

    raise HTTPException(status_code=404, detail="Container not found")


@app.delete("/items/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(name: str):
    if name not in db:
        raise HTTPException(status_code=404, detail="Resource not found")

    del db[name]
    return None