import os
from celery import Celery
from celery.utils.log import get_task_logger
from model.CropModel import CropModel, CropModelException

# Set up logger
log = get_task_logger(__name__)

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)



@celery_app.task(bind=True, track_started=True, name='celery_model_get_bau')
def celery_model_get_bau(self, landscape_id):

    self.update_state(state='PROGRESS', meta={'status': 'Initialising'})

    # Initialise crop model
    model = CropModel()
    model.set_landscape_id(int(landscape_id))
    model.initialise_model()

    self.update_state(state='PROGRESS', meta={'status': 'Running'})
    model.run_model()

    result = model.to_dict()

    #self.update_state(state='SUCCESS')
    log.info(result)

    return {'result': result}


@celery_app.task(bind=True, track_started=True, name='celery_model_run')
def celery_model_run(self, landscape_id, data):

    self.update_state(state='PROGRESS', meta={'status': 'Initialising'})

    # Initialise crop model
    model = CropModel()
    model.set_landscape_id(int(landscape_id))
    model.initialise_model()

    # Extract parameters from strings and build a list to pass to CropModel
    max_crops = len(model.cropAreasBAU)
    crop_areas = []
    for i in range(0, max_crops):
        crop = model.get_crop_string(i).lower().split(' ')[0]
        area = float(data[crop])
        # log.info("{}={}".format(crop, area))
        crop_areas.append(area)

    max_livestock = len(model.livestockNumbersBAU)
    livestock_areas = []
    for i in range(0, max_livestock):
        livestock = model.get_livestock_string(i).lower()  # .split(' ')[0]
        area = int(data[livestock])  # TODO: This will likely need to change to type float
        # log.info("{}={}".format(livestock, area))
        livestock_areas.append(area)

    # set_crop_areas takes an ordered list of float point numbers
    model.set_crop_areas(crop_areas)
    model.set_livestock_areas(livestock_areas)

    self.update_state(state='PROGRESS', meta={'status': 'Running'})
    model.run_model()

    result = model.to_dict()

    #self.update_state(state='SUCCESS')
    log.info(result)

    return {'result': result}


if __name__ == "__main__":
    log.info(celery_app.tasks)
    celery_app.start(argv=['celery', 'worker', '-l', 'info'])