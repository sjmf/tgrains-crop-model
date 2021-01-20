import os
from celery import Celery
from celery.utils.log import get_task_logger
from model.CropModel import CropModel, CropModelException
from tasks.exceptions import TaskFailure
import cppyy

# Set up logger
log = get_task_logger(__name__)

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# We don't have an array length for nutritionaldelivery until run() is called.
# Therefore, we need to define its length to return food group strings:
TOTAL_FOOD_GROUPS = 9


# Helper function which initialises a model
def initialise_model(self, landscape_id=101):
    self.update_state(state='PROGRESS', meta={'status': 'Initialising'})

    # Initialise crop model
    model = CropModel()
    model.set_landscape_id(int(landscape_id))
    model.initialise_model()

    self.update_state(state='PROGRESS', meta={'status': 'Running'})
    return model


@celery_app.task(bind=True, track_started=True, name='celery_get_strings')
def celery_get_strings(self, landscape_id):
    try:
        model = initialise_model(self, landscape_id)

        strings = {
            'crops': [model.get_crop_string(i).lower()
                      for i in range(model.cropAreas.size())],
            'livestock': [model.get_livestock_string(i).lower()
                          for i in range(model.livestockAreas.size())],
            'food_groups': [model.get_food_group_string(i).lower()
                            for i in range(TOTAL_FOOD_GROUPS)]
        }

        log.info(model.data.nutritionaldelivery.size())

        return {'result': strings}

    except (CropModelException,
            cppyy.gbl.std.exception,
            cppyy.gbl.std.invalid_argument,
            cppyy.gbl.std.filesystem.filesystem_error) as e:
        log.error(e)
        raise TaskFailure('Task Failed: ' + str(e))


@celery_app.task(bind=True, track_started=True, name='celery_model_get_bau')
def celery_model_get_bau(self, landscape_id):
    try:
        model = initialise_model(self, landscape_id)
        model.run_model()
        result = model.to_dict()

        # Append grazing props to model BAU
        result['grazingProps'] = {
            'lamb': model.get_upland_grazing_lamb_prop(),
            'beef': model.get_upland_grazing_beef_prop()
        }

        log.info(result)
        return {'result': result}

    except (CropModelException,
            cppyy.gbl.std.exception,
            cppyy.gbl.std.invalid_argument,
            cppyy.gbl.std.filesystem.filesystem_error) as e:
        log.error(e)
        raise TaskFailure('Task Failed: ' + str(e))


@celery_app.task(bind=True, track_started=True, name='celery_model_run')
def celery_model_run(self, landscape_id, data):
    try:
        model = initialise_model(self, landscape_id)

        # Extract parameters from strings and mutate CropModel directly
        max_crops = model.cropAreas.size()
        for i in range(0, max_crops):
            crop = model.get_crop_string(i).lower()
            area = float(data[crop])
            # log.info("{}={}".format(crop, area))
            model.cropAreas[i] = area

        max_livestock = model.livestockAreas.size()
        for i in range(0, max_livestock):
            livestock = model.get_livestock_string(i).lower()
            area = float(data[livestock])
            # log.info("{}={}".format(livestock, area))
            model.livestockAreas[i] = area

        try:
            model.run_model()
        except cppyy.gbl.std.length_error as err:
            raise err

        result = model.to_dict()
        log.info(result)

        return {'result': result}

    except (CropModelException,
            cppyy.gbl.std.exception,
            cppyy.gbl.std.invalid_argument,
            cppyy.gbl.std.filesystem.filesystem_error) as e:
        log.error(e)
        raise TaskFailure('Task Failed: ' + str(e))


if __name__ == "__main__":
    log.info(celery_app.tasks)
    celery_app.start(argv=['celery', 'worker', '-l', 'info'])
