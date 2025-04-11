from celery import Celery

def make_celery(app_name=__name__):
    # Configure Celery with Redis as the broker and backend
    celery = Celery(app_name, 
                    broker='redis://localhost:6379/0', 
                    backend='redis://localhost:6379/0')
    celery.conf.update(app_name.config)
    return celery

