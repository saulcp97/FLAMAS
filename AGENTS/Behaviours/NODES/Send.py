from spade.behaviour import State
from spade.message import Message
import datetime
import random
import time
import Config
import codecs
import pickle
import uuid

class SendState(State):
    
    async def send_message(self, recipient):
        id = str(uuid.uuid4())
        msg = Message(to=recipient)
        msg.set_metadata("conversation", "pre_consensus_data")
        msg.set_metadata("message_id", id)

        local_weights = self.agent.weights
        local_losses = self.agent.train_loss

        if local_weights is not None or local_losses is not None:
            msg_local_weights = codecs.encode(pickle.dumps(local_weights), "base64").decode()
            msg_local_losses = codecs.encode(pickle.dumps(local_losses), "base64").decode()

            content = msg_local_weights + "|" + msg_local_losses + "|" + "SEND_STATE"
            
            msg.body = content
            msg.set_metadata("timestamp", str(datetime.datetime.now()))
            self.agent.message_logger.write_to_file("SEND,{},{}".format(id, recipient))
            await self.send(msg)

    async def run(self):
        await self.send_message(self.agent.serverJid)
        self.set_next_state("RECEIVE")