import requests

from . import config


class Pecha:
    def __init__(self, images_dir=config.IMAGES_DIR, output_dir=config.OUTPUT_DIR):
        self.images_dir = images_dir
        self.output_dir = output_dir

    @property
    def volumes(self):
        return self._get_volumes()

    def _get_volumes(self):
        raise NotImplemented()

    def ocr(self):
        for volume in self.volumes:
            volume.get_images()
            volume.run_ocr()
            volume.archive()

class BdrcPecha(Pecha):
    def __init__(self, work_id):
        self.work_id = work_id
        volumes_url = (
            f"purl.bdrc.io/query/table/volumesForInstance?R_RES=bdr:M{self.work_id}&pageSize=500&format=json"
        )

    def _get_volumes(self):

