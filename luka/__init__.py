import os
import json
import shutil
from datetime import datetime

from luka.observer import Subject


__all__ = ['Snapshot', 'Luka']

class Snapshot(object):
    def __init__(self, id, message):
        self.id = id
        self.message = message

class Luka(object):
    loaded = Subject()
    saved  = Subject()
    snapshot_taked = Subject()
    snapshot_restored = Subject()
    snapshot_removed = Subject()
    
    def __init__(self, source_path, load=False):
        self.source_path = source_path
        self.snapshots = {}

        if load:
            self.load()

    def load(self):
        if not os.path.isfile(self.luka_json()):
            return []

        self.snapshots.clear()
        with open(self.luka_json()) as f:
            data = json.load(f)['snapshots']
            for id in sorted(data.keys()):
                self.snapshots[id] = (Snapshot(id, data[id]['message']))
        
        self.loaded.notify(self, self.snapshots)

        return self.snapshots

    def save(self):
        with open(self.luka_json(), 'w+') as f:
            data = { 'snapshots': {} }
            for id in self.snapshots.keys():
                s = self.snapshots[id]
                data['snapshots'][id] = { 'message': s.message }
            json.dump(data, f)
        
        self.saved.notify(self, self.snapshots)
        

    def take_snapshot(self, message, id=None, save=True):
        if id is None:
            id = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

        if id in self.snapshots.keys():
            raise ValueError()

        if not os.path.isdir(self.luka_directory()):
            self.create_directory()

        shutil.copy2(self.source_path, self.build_snapshot_path(id))

        s = Snapshot(id, message)
        self.snapshots[id] = s

        self.snapshot_taked.notify(self, s)

        if save:
            self.save()
        return s

    def restore_snapshot(self, s):
        shutil.copy2(self.build_snapshot_path(s.id), self.source_path)
        self.snapshot_restored.notify(self, s)

    def remove_snapshot(self, s, save=True):
        os.remove(self.build_snapshot_path(s.id))
        self.snapshot_removed.notify(self, s)
        if save:
            self.save()

    def create_directory(self):
         os.mkdir(self.luka_directory())

    def build_snapshot_path(self, id):
        ext = os.path.splitext(self.source_path)[1]
        return os.path.join(self.luka_directory(), id + ext)

    def luka_directory(self):
        return self.source_path + '.luka'

    def luka_json(self):
        return os.path.join(self.luka_directory(), 'luka.json')
