from spade.behaviour import State
from spade.message import Message
import datetime
import random
import time
import uuid
import Config
import codecs
import pickle
import Config

from utils.MultipartHandler import MultipartHandler


class AskState(State):

    def __init__(self):
        super().__init__()
        self.multipart_handler = MultipartHandler()

    async def send_message(self, recipient):
        id = str(uuid.uuid4())
        msg = Message(to=recipient)
        msg.set_metadata("conversation", "pre_consensus_data")
        msg.set_metadata("message_id", id)
        content = "GET_WEIGHTS"
        
        msg.body = content

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

    async def manage_weights(self, msg):
        if not msg.body.startswith("I don't"):
            server_weights = msg.body.split("|")
            unpickled_server_weights = pickle.loads(codecs.decode(server_weights[0].encode(), "base64"))
            self.agent.updateWeights(unpickled_server_weights)
            self.agent.trainer.build_Model()

    async def run(self):
        msg = None
        await self.send_message(self.agent.serverJid)
        print(self.agent.name, ": PESOS Solicitados y esperando")
        while True:
            msg = await self.receive(timeout=Config.DEFAULT_TIMER)
            multipart = self.multipart_handler.rebuild_multipart(msg)
            if multipart is not None:
                msg = multipart

            if not self.multipart_handler.is_multipart(msg) or multipart is not None:
                self.agent.message_logger.write_to_file("RECEIVE,{},{}".format(msg.get_metadata("message_id"), msg.sender))
                await self.manage_weights(msg)
                break
        
        print(self.agent.name, ": PESOS RECIBIDOS Totalmente")
        self.set_next_state("TRAIN")