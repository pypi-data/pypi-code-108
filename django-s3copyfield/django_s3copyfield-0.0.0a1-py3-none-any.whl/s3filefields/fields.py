import re
import boto3
from django.db.models.fields.files import FileField


class S3FileField(FileField):

    def pre_save(self, model_instance, add):
        """ override the pre_save method in django.db.models.fields.files.FileField to allow copying
            a file from a provided S3 uri """
        file = super().pre_save(model_instance, add)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file.file, save=False)
        elif file and file.name.startswith('s3://'):
            s3_pattern = '^s3://([^/]+)/(.*?([^/]+)/?)$'
            mo = re.match(s3_pattern, file.name)
            if mo:
                src_bucket, src_key, src_filename = mo.groups()
                file.name = src_filename
                dst_bucket = getattr(model_instance._meta.model, self.name).field.storage.bucket_name

                # if there is an upload_to function, use that to determine the dst filename
                model_field = getattr(model_instance._meta.model, self.name).field
                if hasattr(model_field, 'upload_to'):
                    dst_key = getattr(model_instance._meta.model, self.name).field.upload_to(model_instance)
                    file.name = dst_key

                # If src and dst are the same, just add the file to the database, don't change what's already in S3.
                # If src and dst are different, copy the file from src to dst.
                if src_bucket != dst_bucket or src_key != file.name:
                    s3 = boto3.resource('s3')
                    dst = s3.Bucket(dst_bucket)
                    source = {'Bucket': src_bucket, 'Key': src_key}
                    dst.copy(source, file.name)
        return file
