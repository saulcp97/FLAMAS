#Comportamiento de entrenamiento

from spade.behaviour import State
import time
from utils.weightsAndData import inference

class TrainState(State):

    async def train_local(self):
        self.start_time = time.monotonic()

        self.agent.training_time_logger.write_to_file("START")
        #Dento del tiempo de entrenamiento se incluye los tests de precisión.
        await self.agent.trainer.train()

        self.agent.weights = self.agent.trainer.weight
        self.agent.train_acc, self.agent.train_loss, self.agent.test_acc, self.agent.test_loss = self.get_accuracy()
        #f.write("time,training_accuracy,training_loss,test_accuracy,test_loss\n")
        #Time esta incluido
        self.agent.training_logger.write_to_file(
            "{},{},{},{}".format(self.agent.train_acc, self.agent.train_loss, self.agent.test_acc, self.agent.test_loss))

        
        self.agent.training_time_logger.write_to_file("STOP")

        #self.get_accuracy()

    def get_accuracy(self):
        self.agent.trainer.model.eval()
        acc, loss = inference(model=self.agent.trainer.model, loader=self.agent.trainer.train_loader)
        #print("[{}] Train Accuracy : {}%".format(self.agent_name, round(acc * 100, 2)))
        #print("[{}] Train Loss : {}".format(self.agent_name, round(loss, 4)))
        #self.train_accuracy.append(acc)
        #self.train_loss.append(loss)
        # Test inference after completion of training
        test_acc, test_loss = inference(model=self.agent.trainer.model, loader=self.agent.trainer.test_loader)

        #print("[{}] Test Accuracy: {}%".format(self.agent_name, round(test_acc * 100, 2)))
        #print("[{}] Test Loss: {}".format(self.agent_name, round(test_loss, 4)))


        return [
            round(acc * 100, 2),
            round(loss, 2),
            round(test_acc * 100, 2),
            round(test_loss, 4),
        ]


    async def run(self):
        await self.train_local()

        self.set_next_state("SEND")
