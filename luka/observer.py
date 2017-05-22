class Subject:
    def __init__(self):
        self.subscriptions = []
 
    def subscribe(self, f):
        self.subscriptions.append(f)
 
    def unsbuscribe(self, f):
        self.subscriptions.remove(f)
 
    def notify(self, sender, *args, **kwargs):
         for f in self.subscriptions:
             f(sender, *args, **kwargs)
