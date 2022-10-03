#!/usr/bin/env python3

from utilities import get_files, generate_id
from PIL import Image, UnidentifiedImageError
import requests
from os import walk, makedirs
from os.path import join, isfile, isdir, dirname, split, sep
from database import create_database, connect_database, insert_into_db
from variables import schema
from cli import cli
from io import BytesIO
from uuid import uuid4, uuid5, NAMESPACE_URL
from multiprocessing import Queue, Process
from workers import monitor, fill_q, recognizer

# Enable Logging
import logging
logging.basicConfig(encoding='utf-8', format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

directory = "/home/colin/Rain Photos"
output_directory = "/home/colin/Rain_Headshots"
database = "/home/colin/Rain_Headshots/rain_studios_headshots.db"
ai_url = "http://localhost:32168"

__version__ = "0.1.0"
__short_name__ = "deepstack"
queue = Queue(100000)

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    config = cli(version=__version__, program=__short_name__)

    directory = config.search_directory
    database = config.database
    output_directory = config.output

    if not isdir(output_directory):
        makedirs(output_directory)

    logger.warning("Stopping after %s files",config.stop_after)

    logger.setLevel(getattr(logging, config.debug.upper()))
    # define file handler and set formatter
    file_handler = logging.FileHandler(config.logfile)
    file_handler.setFormatter(formatter)
    if not isfile(database):
        logger.info("Create database {} with schema {}".format(database, schema))
        create_database(config, logger, schema)
        connection = connect_database(config,logger)
    else:
        connection = connect_database(config,logger)



    files = list()
    worker = list()
    files = get_files(directory)
    logger.info("Files found for processing {}".format(len(files)))

    # Add files to Queue
    # Fill the Queue
    logger.debug("Filling the Queue with %s values", len(files))
    fill_q(queue, files)
    logger.info("Queue Size %s", queue.qsize())

    # Create and start workers
    workers = list()
    proc = Process(target=monitor, args=(queue, logger))
    workers.append(proc)
    proc.start()
    for worker_no in range(config.workers):
        logger.info("Adding worker # %s", worker_no)
        proc = Process(target=recognizer, args=(queue, worker_no , logger, ai_url, config))
        workers.append(proc)
        proc.start()

        # complete the processes
    for worker_proc in workers:
        print(worker_proc)
        worker_proc.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


