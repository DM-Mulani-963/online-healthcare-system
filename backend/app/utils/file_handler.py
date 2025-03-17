import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import boto3
from botocore.exceptions import ClientError

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, file_type='document'):
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    if not allowed_file(filename, current_app.config['ALLOWED_EXTENSIONS'][file_type]):
        return None
        
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Check if using S3 or local storage
    if current_app.config.get('AWS_ACCESS_KEY_ID'):
        return save_to_s3(file, unique_filename, file_type)
    else:
        return save_to_local(file, unique_filename, file_type)

def save_to_local(file, filename, file_type):
    try:
        # Create type-specific subdirectory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        return filename
    except Exception as e:
        current_app.logger.error(f"Error saving file locally: {str(e)}")
        return None

def save_to_s3(file, filename, file_type):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )
        
        # Create S3 path with file type folder
        s3_path = f"{file_type}/{filename}"
        
        s3_client.upload_fileobj(
            file,
            current_app.config['AWS_BUCKET_NAME'],
            s3_path,
            ExtraArgs={
                'ACL': 'private',
                'ContentType': file.content_type
            }
        )
        
        return s3_path
    except Exception as e:
        current_app.logger.error(f"Error uploading to S3: {str(e)}")
        return None

def get_file_url(filename, file_type):
    if not filename:
        return None
        
    # If using S3
    if current_app.config.get('AWS_ACCESS_KEY_ID'):
        try:
            s3_client = boto3.client('s3')
            return s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': current_app.config['AWS_BUCKET_NAME'],
                    'Key': f"{file_type}/{filename}"
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
        except ClientError as e:
            current_app.logger.error(f"Error generating S3 URL: {str(e)}")
            return None
    
    # If using local storage
    return os.path.join('/uploads', file_type, filename)

def delete_file(filename, file_type):
    if not filename:
        return False
        
    # If using S3
    if current_app.config.get('AWS_ACCESS_KEY_ID'):
        try:
            s3_client = boto3.client('s3')
            s3_client.delete_object(
                Bucket=current_app.config['AWS_BUCKET_NAME'],
                Key=f"{file_type}/{filename}"
            )
            return True
        except ClientError as e:
            current_app.logger.error(f"Error deleting from S3: {str(e)}")
            return False
    
    # If using local storage
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error deleting local file: {str(e)}")
        return False 