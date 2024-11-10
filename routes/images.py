import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter()

UPLOAD_FOLDER = "uploads"

# Upload multiple DICOM images to the server
@router.post("/images")
async def upload_images(files: list[UploadFile] = File(...)):
    # Check if the uploads folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    for file in files:
        # Check if the file is a DICOM image
        if not file.filename.endswith('.dcm'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a DICOM image")

        # Save the file to the uploads folder
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as image_file:
            # Read the dicom images using PyDICOM
            image_file.write(await file.read())

    return JSONResponse(content={"message": "Files uploaded successfully"})


# Check if there are any DICOM images in the uploads folder
@router.get("/images")
async def list_images():

    # Check if the uploads folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        raise HTTPException(status_code=404, detail="No images found")

    # Check if uploads folder is empty
    if not os.listdir(UPLOAD_FOLDER):
        raise HTTPException(status_code=404, detail="No images found")

    return JSONResponse(status_code=200, content={"message": "Images found"})

