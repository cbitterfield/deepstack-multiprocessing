from multiprocessing import Process, Queue
import time
import logging
from utilities import func_name

from utilities import get_files, generate_id
from PIL import Image, UnidentifiedImageError
import requests
from os import walk, makedirs
from os.path import join, isfile, isdir, dirname, split, sep
from database import  insert_into_db
from io import BytesIO
from uuid import uuid4, uuid5, NAMESPACE_URL
from database import connect_database
import random

# Multiprocessing Functions Go Here

def fill_q(queue,queue_data):
    for datum in queue_data:
        queue.put(datum)

def empty_q(queue):
    cnt = 0
    while not queue.empty():
        print('item no: ', cnt, ' ', queue.get())
        cnt += 1


def test_worker(queue, worker_no , logger, ai_url, config):
    logger = logging.getLogger(func_name())
    while not queue.empty():
        filename = queue.get()
        logger.info("Worker {} got filename {}".format(worker_no, filename))
        time.sleep(1)


def monitor(queue,logger):
    logger = logging.getLogger(func_name())
    while not queue.empty():
        time.sleep(60)
        size = queue.qsize()
        logger.info("There are {} items left in the queue".format(size))


def recognizer(queue, worker_no, logger, ai_url, config):
    logger = logging.getLogger(func_name() + str(worker_no))
    logger.info("worker number %s starting", worker_no)
    count = 0
    skipped = 0
    # Each worker has its own connection to the database
    connection = connect_database(config, logger)
    output_directory = config.output
    logger.info("Write output to %s",output_directory)
    while not queue.empty():
        time.sleep(random.random())
        objects = list()
        scene = ""
        image_bytes = BytesIO()
        size = queue.qsize()
        file = queue.get()
        count += 1
        logger.info("Processing file: {}, Files remaining {}, recognizer {} processed {} files and skipped {}"
                    .format(file, size, worker_no, count, skipped))
        try:
            image = Image.open(file).convert("RGB")
        except Exception as error:
            logger.warning("Image File is unidentified %s error %s", file, error)
            skipped += 1
            continue

        image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        file_uuid = str(uuid5(NAMESPACE_URL, file))
        file_directory = dirname(file)

        # Recognize Objects
        logger.info("Recognizing objects")
        objects = list()
        object_response = requests.post(
            ai_url + "/v1/vision/detection",
            data={"min_confidence": .8},
            files={"image": image_data}
        ).json()

        if object_response.get('success', False):
            for predicted_object in object_response["predictions"]:
                logger.debug('Object Detected %s', predicted_object["label"])
                objects.append(predicted_object["label"])
        logger.info('%s objects recognized in the file',len(objects))
        # Recognize Scene
        scene = ""
        scene_response = requests.post(
            ai_url + "/v1/vision/scene",
            data={"min_confidence": .8},
            files={"image": image_data}
        ).json()
        if scene_response.get('success', False):
            scene = scene_response['label']
            logger.debug('The scene was recognized as %s', scene_response['label'])
        else:
            scene = "not detected"
        logger.info('The scene is %s', scene)
        # Recognize Faces
        response = requests.post(ai_url + "/v1/vision/face/recognize",
                                 data={"min_confidence": config.confidence},
                                 files={"image": image_data}
                                 ).json()
        logger.debug('Response: %s', response)
        if not response.get('predictions', False):
            logger.info("No face detected in this image %s", file)
            continue
        for face in response["predictions"]:
            cropped_image_data = BytesIO()
            # Location of found face
            y_max = int(int(face["y_max"]) * 1.1)
            y_min = int(int(face["y_min"]) * .55)
            x_max = int(int(face["x_max"]) * 1.1)
            x_min = int(int(face["x_min"]) * .73)
            confidence = face['confidence']

            # Create cropped image of found face
            logger.debug('face {} found at {} {} {} {}'.format(face['userid'], x_min, y_min, x_max, y_max))
            logger.info(
                'face {} found with confidence of {} %'.format(face['userid'], int(face['confidence'] * 100)))
            cropped = image.crop((x_min, y_min, x_max, y_max))
            cropped.save(cropped_image_data, format='PNG')
            cropped_image_data = cropped_image_data.getvalue()

            user_id = uuid4()
            if face['userid'] == "unknown":
                face_id = str(user_id)
                # If unknown register it with Deepstack for future reference
                response = requests.post(ai_url + "/v1/vision/face/register",
                                         files={"image1": cropped_image_data},
                                         data={"userid": face_id}).json()
                logger.info("Adding user_id {} from image file {}".format(face_id, file))

            else:
                face_id = face['userid']

            if not isdir("/".join([output_directory, face_id])):
                logger.warning('Creating directory %s', "/".join([output_directory, face_id]))
                makedirs("/".join([output_directory, face_id]))
            cropped.save(
                "{output}/{face}/{file}_face_{face}.jpg".format(output=output_directory, file=file_uuid,
                                                                face=face_id))

            # Write information to SQLite3 database for future reference
            if config.path_start:
                file = file.replace(config.path_start, "")
                file_directory = file_directory.replace(config.path_start, "")

            movie_path = file_directory.split(sep)

            record = {
                'filename_full': file,
                'file_id': file_uuid,
                'face_id': face_id,
                'movie_path': ",".join(movie_path),
                'y_min': y_min,
                'x_min': x_min,
                'x_max': x_max,
                'y_max': y_max,
                'confidence': confidence,
                'scene': scene,
                'objects': ", ".join(objects),
                'headshot_image': cropped_image_data
            }
            insert_into_db(logger, connection, "performer", record)


