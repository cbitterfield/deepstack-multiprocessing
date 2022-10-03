import logging
from utilities import func_name


headshots = {
    'performer': {
                'filename_full': 'text',
                'file_id': 'text',
                'face_id': 'text',
                'movie_path': 'text',
                'y_min': 'text',
                'x_min': 'text',
                'x_max': 'text',
                'y_max': 'text',
                'confidence': 'text',
                'scene': 'text',
                'objects': 'text',
                'description': 'text',
                'headshot_image': 'blob'
        },
}

faces = {
    'named_faces': {
        'face_id': 'text',
        'description': 'text'
        }
    }


schema = [headshots, faces]


