#Comportamiento de entrenamiento

from spade.behaviour import State
import time
from utils.weightsAndData import average_weights

class MIX(State):

    async def updateWeights(self):
        self.agent.weights = average_weights(self.agent.partialWeights)
        self.agent.partialWeights = []


    async def run(self):
        await self.updateWeights()

        self.set_next_state("SEND")
