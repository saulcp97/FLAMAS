#Receive
from spade.behaviour import State
from spade.message import Message
import datetime
import pickle
import codecs
import Config
from utils.weightsAndData import apply_consensus
import time
import uuid

from utils.MultipartHandler import MultipartHandler


class ReceiveState(State):
    def __init__(self):
        super().__init__()
        self.multipart_handler = MultipartHandler()


    async def msg_management(self, msg):
        if self.agent.weights is not None and msg.body.split("|")[0] != "None" and not msg.body.startswith("I don't"):
            # Process message
            codes = msg.body.split("|")
            meaning = codes[0]
            nName = str(msg.sender)
            if meaning == "GET_WEIGHTS":
                #Check if the name of the node is in the list, if not add it
                if nName not in self.agent.connectedNodes:
                    self.agent.connectedNodes.append(str(nName))
                    print("Unknow node:", nName)
                #Send a message giving it the actual weights
                id = str(uuid.uuid4())
                n_msg = Message(to=nName)
                n_msg.set_metadata("conversation", "pre_consensus_data")
                n_msg.set_metadata("message_id", id)

                local_weights = codecs.encode(pickle.dumps(self.agent.weights), "base64").decode()
                if local_weights is not None:
                    msg_local_weights = str(local_weights).strip()
                    checkSum = str(0)
                    content = msg_local_weights + "|" + checkSum
                    
                    multipart_messages = self.multipart_handler.generate_multipart_messages(content, Config.max_message_body_length, n_msg)  
                    if multipart_messages is not None:
                        for i, message in enumerate(multipart_messages):
                            print(f"[SEND-fsm]  multipart message ({i + 1}/{len(multipart_messages)}) sent to {nName}")
                            message.set_metadata("timestamp", str(datetime.datetime.now()))
                            await self.send(message)
                        self.agent.message_logger.write_to_file("SEND,{},{}".format(id, nName))
                    else:
                        n_msg.body = content
                        n_msg.set_metadata("timestamp", str(datetime.datetime.now()))
                        self.agent.message_logger.write_to_file("SEND,{},{}".format(id, nName))
                        await self.send(n_msg)
            else:
                if not msg.body.startswith("I don't"):
                    weights_and_losses = msg.body.split("|")
                    unpickled_neighbour_weights = pickle.loads(codecs.decode(weights_and_losses[0].encode(), "base64"))
                    unpickled_neighbour_loss = pickle.loads(codecs.decode(weights_and_losses[1].encode(), "base64"))

                    lList = self.agent.errors.get(nName, [])
                    lList.append(unpickled_neighbour_loss)
                    self.agent.errors[nName] = lList
                    self.agent.partialWeights.append(unpickled_neighbour_weights)


    async def run(self):
        stable = False
        while not stable:
            msg = await self.receive(timeout=Config.DEFAULT_TIMER)
            if msg is not None:
                multipart = self.multipart_handler.rebuild_multipart(msg)
                if multipart is not None:
                    msg = multipart
                if not self.multipart_handler.is_multipart(msg) or multipart is not None:
                    self.agent.message_logger.write_to_file("RECEIVE,{},{}".format(msg.get_metadata("message_id"), msg.sender))
                    await self.msg_management(msg)
                stable = len(self.agent.connectedNodes) == len(self.agent.partialWeights)


        if self.agent.localEpoch < Config.EPOCH_NUM:
            self.agent.localEpoch += 1
            self.set_next_state("MIX")
        else:
            self.set_next_state("PLOT")