from spade.behaviour import State
from spade.message import Message
import datetime
import random
import time
import uuid
import Config
import codecs
import pickle

class SendState(State):
    async def sendWeightMessages(self):
        for agent in self.agent.connectedNodes:
            id = str(uuid.uuid4())
            msg = Message(to=agent)
            msg.set_metadata("conversation", "pre_consensus_data")
            msg.set_metadata("message_id", id)
            local_weights = self.agent.weights

            if local_weights is not None:
                msg_local_weights = codecs.encode(pickle.dumps(local_weights), "base64").decode()
                msg_neighbors = str(len(self.agent.connectedNodes))

                content = msg_local_weights + "|" + msg_neighbors
                
                msg.body = content
                msg.set_metadata("timestamp", str(datetime.datetime.now()))
                self.agent.message_logger.write_to_file("SEND,{},{}".format(id, agent))
                await self.send(msg)

    async def run(self):
        await self.sendWeightMessages()
        self.set_next_state("RECEIVE")