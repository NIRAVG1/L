import json
import logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({'level':record.levelname.lower(),'logger':record.name,'message':record.getMessage()})
def configure_logging():
    handler=logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root=logging.getLogger()
    if not root.handlers: root.addHandler(handler)
    root.setLevel(logging.INFO)
