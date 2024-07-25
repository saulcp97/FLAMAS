import Config
import asyncio

from spade.agent import Agent
from spade.template import Template

from spade.behaviour import CyclicBehaviour, State, FSMBehaviour, OneShotBehaviour
from utils.Logger import Logger
from AGENTS.Behaviours.NODES import Ask, Receive, Training, Send
from Models.Training import *




class StateMachineBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()



class NodeAgent(Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False, sjid: str = None, model: torch.nn.Module = None,
            dataTrain:torchvision.datasets = None, dataTest:torchvision.datasets = None):
        super().__init__(jid, password, verify_security)

        self.serverJid = sjid
        self.trainer = FederatedLearning(self.name, model=model, dataTrain=dataTrain, dataTest=dataTest)
        self.weights = None

        self.train_acc = 0
        self.train_loss = 0
        self.test_acc = 0
        self.test_loss = 0

        self.weight_logger = Logger(
            "Logs/Weight Logs/" + self.name + ".csv", Config.WEIGHT_LOGGER
        )
        self.training_logger = Logger(
            "Logs/Training Logs/" + self.name + ".csv", Config.TRAINING_LOGGER
        )
        self.epsilon_logger = Logger(
            "Logs/Epsilon Logs/" + self.name + ".csv", Config.EPSILON_LOGGER
        )
        self.message_logger = Logger(
            "Logs/Message Logs/" + self.name + ".csv", Config.MESSAGE_LOGGER
        )
        self.training_time_logger = Logger(
            "Logs/Training Time Logs/" + self.name + ".csv", Config.TRAINING_TIME_LOGGER
        )

    def updateWeights(self, nWeights):
        self.weights = nWeights
        self.trainer.actualizeModel(self.weights)

    class Behav1(OneShotBehaviour):
        def on_available(self, jid, stanza):
            print("[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0]))

        def on_subscribed(self, jid):
            print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
            print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))

        def on_subscribe(self, jid):
            print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
            self.presence.approve(jid)

        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            self.presence.on_available = self.on_available

            self.presence.set_available()
            self.presence.subscribe(self.agent.serverJid)
            print("Suscribed, to:", self.agent.serverJid)


    async def setup(self):
        self.state_machine_behaviour = StateMachineBehaviour()
        self.state_machine_behaviour.add_state(name= "ASK", state= Ask.AskState(), initial=True)
        self.state_machine_behaviour.add_state(name= "TRAIN", state= Training.TrainState())
        self.state_machine_behaviour.add_state(name= "SEND", state= Send.SendState())
        self.state_machine_behaviour.add_state(name= "RECEIVE", state= Receive.ReceiveState())
        
        self.state_machine_behaviour.add_transition(source= "ASK", dest= "TRAIN")

        self.state_machine_behaviour.add_transition(source= "TRAIN", dest= "SEND")

        self.state_machine_behaviour.add_transition(source= "SEND", dest= "RECEIVE")

        self.state_machine_behaviour.add_transition(source= "RECEIVE", dest= "TRAIN")

        
        state_machine_template = Template()
        state_machine_template.metadata = {"conversation": "pre_consensus_data"}

        self.add_behaviour(self.state_machine_behaviour, state_machine_template)
    
        self.add_behaviour(self.Behav1())