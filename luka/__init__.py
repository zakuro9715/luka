import os
import json
import shutil
from datetime import datetime


__all__ = ['Snapshot', 'Luka']

class Snapshot(object):
    def __init__(self, id, message):
        self.id = id
        self.message = message


class Luka(object):
    def __init__(self, source_path, load=False):
        self.source_path = source_path
        self.snapshots = []
        if not os.path.isdir(self.luka_directory()):
            os.mkdir(self.luka_directory())

        if load:
            self.load()

    def load(self):
        self.snapshots = []
        with open(self.luka_json()) as f:
            data = json.load(f)['snapshots']
            for id in data.keys():
                self.snapshots.append(Snapshot(id, data[id]['message']))

    def save(self):
        with open(self.luka_json(), 'w+') as f:
            data = { 'snapshots': {} }

            for s in self.snapshots:
                data['snapshots'][s.id] = { 'message': s.message }

            json.dump(data, f)

    def take_snapshot(self, message, id=None, save=True):
        if id is None:
            id = datetime.utcnow().isoformat()
        shutil.copy2(self.source_path, self.build_snapshot_path(id))
        self.snapshots.append(Snapshot(id, message))

        if save:
            self.save()

    def restore_snapshot(self, id):
        shutil.copy2(self.build_snapshot_path(id), self.source_path)

    def build_snapshot_path(self, id):
        ext = os.path.splitext(self.source_path)[1]
        return os.path.join(self.luka_directory(), id + ext)

    def luka_directory(self):
        return self.source_path + '.luka'

    def luka_json(self):
        return os.path.join(self.luka_directory(), 'luka.json')

    def list_snapshots(self):
        pass
