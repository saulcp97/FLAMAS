from spade.behaviour import State
from spade.message import Message
import datetime
import random
import time
import Config
import codecs
import pickle
import uuid
from utils.MultipartHandler import MultipartHandler


class SendState(State):
    def __init__(self):
        super().__init__()
        self.multipart_handler = MultipartHandler()
    
    async def send_message(self, recipient):
        id = str(uuid.uuid4())
        msg = Message(to=recipient)
        msg.set_metadata("conversation", "pre_consensus_data")
        msg.set_metadata("message_id", id)

        local_weights = self.agent.weights
        local_losses = self.agent.train_loss

        if local_weights is not None or local_losses is not None:
            msg_local_weights = str(codecs.encode(pickle.dumps(local_weights), "base64").decode()).strip()
            msg_local_losses = str(codecs.encode(pickle.dumps(local_losses), "base64").decode()).strip()

            content = msg_local_weights + "|" + msg_local_losses + "|" + "SEND_STATE"
            

            multipart_messages = self.multipart_handler.generate_multipart_messages(content, Config.max_message_body_length, msg)  
            if multipart_messages is not None:
                for i, message in enumerate(multipart_messages):
                    print(f"[SEND-fsm]  multipart message ({i + 1}/{len(multipart_messages)}) sent to {recipient}")
                    message.set_metadata("timestamp", str(datetime.datetime.now()))
                    await self.send(message)
                self.agent.message_logger.write_to_file("SEND,{},{}".format(id, recipient))
            else:
                msg.body = content
                msg.set_metadata("timestamp", str(datetime.datetime.now()))
                self.agent.message_logger.write_to_file("SEND,{},{}".format(id, recipient))
                await self.send(msg)

    async def run(self):
        await self.send_message(self.agent.serverJid)
        self.set_next_state("RECEIVE")