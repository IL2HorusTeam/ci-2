

def validate_upload(
    file_name,
    content_type,
    allowed_extensions,
    allowed_content_types,
):
    if (
        '.' not in file_name
        or file_name.rsplit('.', 1)[1] not in allowed_extensions
        or content_type not in allowed_content_types
    ):
        raise ValueError("file type is not supported")
