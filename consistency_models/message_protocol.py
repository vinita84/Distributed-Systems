import time
import uuid

class Message_protocol(object):
    def __init__(self, sender_id, msg_type, local_t): #, sender_id, msg_type, local_time, global_time, msg_body):
        self.msg_id = uuid.uuid1()
        self.sender_id = sender_id
        self.msg_type = msg_type
        self.local_timestamp = local_t
        self.global_timestamp = time.time()
        self.msg_body = ''

    def prettyprint(self):
        msg = {'sender_id': self.sender_id,
               'msg_type': self.msg_type,
               # 'local_timestamp': self.local_timestamp,
               # 'global_timestamp': self.global_timestamp,
               'msg_body': self.msg_body}
        return msg








