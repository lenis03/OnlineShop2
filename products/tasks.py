from bucket import bucket
from celery import shared_task


# TODO: can be async?
def get_product_bucket_objects_task():
    result = bucket.get_objects()
    return result


@shared_task
def delete_obj_bucket_task(key):
    bucket.delete_object(key=key)


@shared_task
def download_obj_from_bucket(obj_name):
    bucket.download_object(obj_name=obj_name)
