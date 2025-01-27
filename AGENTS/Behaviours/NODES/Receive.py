#Receive
from spade.behaviour import State
from spade.message import Message
import time
import pickle
import codecs
import Config

from utils.MultipartHandler import MultipartHandler

class ReceiveState(State):

    def __init__(self):
        super().__init__()
        self.multipart_handler = MultipartHandler()


    async def process(self, msg):
        if self.agent.weights is not None and msg.body.split("|")[0] != "None" and not msg.body.startswith("I don't"):
            # Process message
            weights_and_Neighbours = msg.body.split("|")

            #print(f"[RECV-fsm] Consensus message: {weights_and_losses[0][:5]}...{weights_and_losses[0][-5:]} weights, {weights_and_losses[1][:5]}...{weights_and_losses[1][-5:]} losses, {neighbour_max_order} max order")
            unpickled_neighbour_weights = pickle.loads(codecs.decode(weights_and_Neighbours[0].encode(), "base64"))
            N_Neighbours = weights_and_Neighbours[1]
           
            # Update agent properties
            self.agent.weights = unpickled_neighbour_weights
            self.agent.trainer.actualizeModel(self.agent.weights)

            print("Processed Weights")


    async def run(self):
        msg = None

        while True:
            msg = await self.receive(timeout=Config.DEFAULT_TIMER)
            multipart = self.multipart_handler.rebuild_multipart(msg)
            if multipart is not None:
                msg = multipart

            if not self.multipart_handler.is_multipart(msg) or multipart is not None:
                self.agent.message_logger.write_to_file("RECEIVE,{},{}".format(msg.get_metadata("message_id"), msg.sender))
                await self.process(msg)
                break

        self.set_next_state("TRAIN")