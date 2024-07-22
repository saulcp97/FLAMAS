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
class AskState(State):

    async def send_message(self, recipient):
        id = str(uuid.uuid4())
        msg = Message(to=recipient)
        msg.set_metadata("conversation", "pre_consensus_data")
        
        content = codecs.encode("GET_WEIGHTS").decode()
        
        msg.body = content
        msg.set_metadata("timestamp", str(datetime.datetime.now()))
        await self.send(msg)

    async def manage_weights(self, msg):
        print("MSG RECIEVED!")
        if not msg.body.startswith("I don't"):
            server_weights = msg.body.split("|")

            unpickled_server_weights = pickle.loads(codecs.decode(server_weights[0].encode(), "base64"))

            self.agent.updateWeights(unpickled_server_weights)
            self.agent.trainer.build_Model()

    async def run(self):
        msg = None

        while msg is None:
            await self.send_message(self.agent.serverJid)
            msg = await self.receive(timeout=Config.DEFAULT_TIMER)
        await self.manage_weights(msg)
        
        
        
        self.set_next_state("TRAIN")