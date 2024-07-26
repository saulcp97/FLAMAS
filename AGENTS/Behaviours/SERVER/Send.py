from spade.behaviour import State
from spade.message import Message
import datetime
import random
import time
import uuid
import Config
import codecs
import pickle

from utils.MultipartHandler import MultipartHandler

class SendState(State):
    def __init__(self):
        super().__init__()
        self.multipart_handler = MultipartHandler()

    async def sendWeightMessages(self):
        for agent in self.agent.connectedNodes:
            id = str(uuid.uuid4())
            msg = Message(to=agent)
            msg.set_metadata("conversation", "pre_consensus_data")
            msg.set_metadata("message_id", id)
            local_weights = self.agent.weights

            if local_weights is not None:
                msg_local_weights = str(codecs.encode(pickle.dumps(local_weights), "base64").decode()).strip()
                msg_neighbors = str(len(self.agent.connectedNodes))

                content = msg_local_weights + "|" + msg_neighbors
                
                multipart_messages = self.multipart_handler.generate_multipart_messages(content, Config.max_message_body_length, msg)  
                if multipart_messages is not None:
                    for i, message in enumerate(multipart_messages):
                        print(f"[SEND-fsm]  multipart message ({i + 1}/{len(multipart_messages)}) sent to {agent}")
                        message.set_metadata("timestamp", str(datetime.datetime.now()))
                        await self.send(message)
                    self.agent.message_logger.write_to_file("SEND,{},{}".format(id, agent))
                else:
                    msg.body = content
                    msg.set_metadata("timestamp", str(datetime.datetime.now()))
                    self.agent.message_logger.write_to_file("SEND,{},{}".format(id, agent))
                    await self.send(msg)

                msg.body = content
                msg.set_metadata("timestamp", str(datetime.datetime.now()))
                self.agent.message_logger.write_to_file("SEND,{},{}".format(id, agent))
                await self.send(msg)

    async def run(self):
        await self.sendWeightMessages()
        self.set_next_state("RECEIVE")