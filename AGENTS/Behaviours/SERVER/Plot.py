#Comportamiento final

import matplotlib.pylab as plt


from spade.behaviour import State
import time
from utils.weightsAndData import average_weights

class PLOT(State):

    def plotLoss(self):
        for key in self.agent.errors.keys():
            plt.plot(self.agent.errors[key], label = key)
        plt.legend() 
        plt.show()

    async def run(self):
        print("PLOT")
        self.plotLoss()
