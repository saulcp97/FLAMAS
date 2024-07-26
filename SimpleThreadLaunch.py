import spade
import os
from spade.agent import Agent
from pathlib import Path
import networkx as nx

import time
import threading
import asyncio

import copy

import Config
from dataset.cifar import CIFAR8
from Models.Architectures import CIFAR8TinyCNN
#t = threading.Thread()

from AGENTS.ServerAgent import CentralAgent
from AGENTS.NodeAgent import NodeAgent

import torchvision.transforms as transforms


async def launch_agent(agent):
    await agent.start()

def launch_agent_sync(agent):
    try:
        asyncio.run(launch_agent(agent))
    except Exception as e:
        # Manejar el error de forma síncrona
        print(f"Error al iniciar el agente: {e}")

async def main():
    data = Path('data/cifar100_subset.pth').resolve()

    transform = transforms.Compose([
        transforms.ToTensor()
    ])

    datasetTr = CIFAR8(root=data.parent.resolve(), train=True, transform=transform, download=True)
    datasetTe = CIFAR8(root=data.parent.resolve(), train=False, transform=transform, download=True)


    names = Config.AGENT_NAMES
    pswrdd = "01234"
    agents = []
    threads = []
    model = CIFAR8TinyCNN()
    weights = model.state_dict()
    
    s0N = Config.SERVER_NAME + Config.jid_domain
    print(s0N)
    s0 = CentralAgent(jid=s0N, password=pswrdd,weights=weights)
    await s0.start()
    s0.web.start(hostname="127.0.0.1", port="10000")
    
    for name in names:
        jid_name = name + Config.jid_domain
        print(jid_name)
        agents.append(NodeAgent(jid=jid_name, password=pswrdd, sjid=s0N, model=copy.deepcopy(model), dataTrain=datasetTr, dataTest=datasetTe))
    
    for agent in agents:
    
        t = threading.Thread(
            target= launch_agent_sync,
            args=[agent],
        )
        t.daemon = True
        t.name = agent.name
        threads.append(t)
        t.start()

if __name__ == "__main__":
    spade.run(main())