import Config
import asyncio

from spade.agent import Agent
from spade.template import Template

from spade.behaviour import CyclicBehaviour, State, FSMBehaviour, OneShotBehaviour

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision

from AGENTS.Behaviours.SERVER import Receive, Training, Send, Plot

class StateMachineBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()

class CentralAgent(Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False, weights: dict = None):
        super().__init__(jid, password, verify_security)
        self.connectedNodes = []
        self.weights = weights
        self.partialWeights = []
        self.localEpoch = 0
        self.errors = {}
        
    class Behav1(OneShotBehaviour):
        def on_available(self, jid, stanza):
            print("[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0]))

        def on_subscribed(self, jid):
            print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
            print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))

        def on_subscribe(self, jid):
            print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
            self.presence.approve(jid)
            self.presence.subscribe(jid)
            self.agent.connectedNodes.append(jid)

        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            self.presence.on_available = self.on_available

            self.presence.set_available()

    
    async def setup(self):
        self.state_machine_behaviour = StateMachineBehaviour()

        self.state_machine_behaviour.add_state(name= "RECEIVE", state= Receive.ReceiveState(), initial=True)
        self.state_machine_behaviour.add_state(name= "MIX", state= Training.MIX())
        self.state_machine_behaviour.add_state(name= "SEND", state= Send.SendState())
        self.state_machine_behaviour.add_state(name= "PLOT", state= Plot.PLOT())
        
        self.state_machine_behaviour.add_transition(source= "RECEIVE", dest= "MIX")
        self.state_machine_behaviour.add_transition(source= "RECEIVE", dest= "PLOT")
        self.state_machine_behaviour.add_transition(source= "MIX", dest= "SEND")

        self.state_machine_behaviour.add_transition(source= "SEND", dest= "RECEIVE")

        state_machine_template = Template()
        state_machine_template.metadata = {"conversation": "pre_consensus_data"}

        self.add_behaviour(self.state_machine_behaviour, state_machine_template)
        self.add_behaviour(self.Behav1())
        