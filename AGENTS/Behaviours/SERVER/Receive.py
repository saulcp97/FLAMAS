#Receive
from spade.behaviour import State
from spade.message import Message
import datetime
import pickle
import codecs
import Config
from utils.weightsAndData import apply_consensus
import time

class ReceiveState(State):
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
                n_msg = Message(to=nName)
                n_msg.set_metadata("conversation", "pre_consensus_data")

                local_weights = self.agent.weights
                if local_weights is not None:
                    msg_local_weights = codecs.encode(pickle.dumps(local_weights), "base64").decode()
                    checkSum = str(0)

                    content = msg_local_weights + "|" + checkSum
                    
                    n_msg.body = content
                    n_msg.set_metadata("timestamp", str(datetime.datetime.now()))
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
                #print(self.agent.available_agents)
                self.agent.message_logger.write_to_file("RECEIVE,{},{}".format(msg.get_metadata("message_id"), msg.sender))
                await self.msg_management(msg)
                stable = len(self.agent.connectedNodes) == len(self.agent.partialWeights)
        self.agent.localEpoch += 1
        if self.agent.localEpoch < Config.EPOCH_NUM:
            self.set_next_state("MIX")
        else:
            self.set_next_state("PLOT")