import cloudinary.uploader


def delete_file_from_cloudinary(public_id):
    """
    Deletes a file from Cloudinary using its public_id.

    Args:
        public_id (str): The public ID of the file to delete on Cloudinary.

    Returns:
        dict: Response from Cloudinary indicating the result of the deletion.
        Raises an exception if the deletion fails.
    """
    try:
        # Call Cloudinary's destroy API
        result = cloudinary.uploader.destroy(public_id)
        if result.get("result") == "ok":
            return {"message": "File deleted successfully", "result": result}
        else:
            return {"error": "Failed to delete the file", "result": result}
    except Exception as e:
        raise Exception(f"Failed to delete file from Cloudinary: {str(e)}")


def upload_file_to_cloudinary(file, folder=None, resource_type="auto"):
    """
    Uploads a file to Cloudinary.

    Args:
        file (File): The file object to be uploaded.
        folder (str, optional): The folder in Cloudinary to upload the file to.
        resource_type (str, optional): The type of resource. Defaults to "auto".

    Returns:
        dict: Response from Cloudinary indicating the result of the upload.
        Raises an exception if the upload fails.
    """
    try:
        # Prepare upload parameters
        upload_params = {"resource_type": resource_type}
        if folder:
            upload_params["folder"] = folder

        # Upload the file
        result = cloudinary.uploader.upload(file, **upload_params)
        return result
    except Exception as e:
        raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")
