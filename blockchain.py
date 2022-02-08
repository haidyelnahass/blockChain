from asyncore import write
from hashlib import sha256
from itertools import chain
import json
from random import randint, random
import time
from numpy import block
import requests
# from flask import Flask, request
import numpy  as np
from scipy import rand


class Block:
    def __init__(self, index, tx,timestamp, prevHash, nonce = 0):
        self.index = index
        self.ver = 1
        self.transactions = tx
        self.timestamp = timestamp
        self.prevHash = prevHash
        self.nonce = nonce

def computeHash(block):
    block_string = json.dumps(block.__dict__, sort_keys=True)
    hash = sha256(block_string.encode()).hexdigest()
    return hash[::-1]


class BlockChain: 
    def __init__(self):
        self.pendingTx = []
        self.chainOfTx = []
        self.branches = []
        self.forkBlockIndex = 0
        self.numTrials = 0
        self.difficulty = 4

        self.createGenesisBlock()
 
    def createGenesisBlock(self):
        genesisBlock = Block(0, [], time.time(), "0")
        computeHash(genesisBlock)
        self.chainOfTx.append(genesisBlock)


    def getLastBlock(self):
        return self.chainOfTx[-1]
    # proof of work
    def getBlock(self, index):
        return self.chainOfTx[index]

    def getDifficulty(self):

        return self.difficulty

   

    def setDifficulty(self,d):

        self.difficulty = d

        pass

    def proofOfWork(self, block):
            block.nonce = 0
            computed_hash = computeHash(block)
            # print(block.nonce)
            while not computed_hash.startswith('0' * self.difficulty):
                block.nonce += 1
                computed_hash = computeHash(block)
                # print(block.nonce)
            return computed_hash
 
    def isProofValid(self, block, blockHash):
            return (blockHash.startswith('0' * self.difficulty) and
                    blockHash == computeHash(block))


    def addBlock(self, block, proof):
        
        lastBlock = self.getLastBlock()
        hash = computeHash(lastBlock)
        index = lastBlock.index

        if hash != block.prevHash:
            return False
        if not self.isProofValid(block, proof):
            return False
        # block.nonce = proof
        self.chainOfTx.append(block)
        # self.numTrials = self.numTrials + 1
        return True

    def appendTx(self, transaction):
                self.pendingTx.append(transaction)
    
    def mine(self):
            # print('here?')
            if not self.pendingTx:
                return False
    
            lastBlock = self.getLastBlock()

            transactions = lastBlock.transactions + self.pendingTx
    
            newBlock = Block(index=lastBlock.index + 1,
                            tx=transactions,
                            timestamp=time.time(),
                            prevHash=computeHash(lastBlock))
                        
    
            proof = self.proofOfWork(newBlock)
            self.addBlock(newBlock, proof)
            self.pendingTx = []
            return newBlock

class User:
    def __init__(self, number):
        self.blockChain = BlockChain()
        self.number = number
    

def broadcastTransaction(users, transactionUser, newBlock):
    for user in users:
        if(user.number == transactionUser.number):
            continue
        proof = user.blockChain.proofOfWork(newBlock)
        user.blockChain.addBlock(newBlock, proof)

def write_to_text_file(data):
    with open('result.txt','w') as f:
        for item in data:
            f.write(str(item.__dict__))
            f.write('\n')

def controlGUI(user):
    history = []

    for it in range(0,10):
        print("Working...!")
        avg = []

        for i in range(0,8):

            t1 = time.time()
            user.blockChain.appendTx('Transaction')
            time1 = time.time()
            user.blockChain.mine()
            time2 = time.time()
            # print('Block mined in ' + str(time2 - time1))

            avg.append(time.time()-t1)

        mean = sum(avg)/len(avg)

        print("Iteration: ", it ,", avg is ",mean)

        del avg



        old = user.blockChain.getDifficulty()

        history.append({old:mean})

        if mean == 0.0:
            continue
        if not(int(mean/1) > 0.9 and int(mean/1) < 1.2):

            if int(mean/1) >1.2:

                user.blockChain.setDifficulty(old -1)

                print("new N ",old-1)

            else:

                user.blockChain.setDifficulty(old +1)

                print("new N ",old+1)



        else:
            print('Found suitable N')
            break

    if len(history) > 1:

        last = list(history[-1].values())[0]

        l2= list(history[-2].values())[0]

        if last > 0.9 and last < 1.5 :

            user.blockChain.setDifficulty(list(history[-1].keys())[0])
            N = list(history[-1].keys())[0]
            print("new N",N)

        else :

            user.blockChain.setDifficulty(list(history[-2].keys())[0])
            N = list(history[-2].keys())[0]
            print("new N",N)
        return N



print('---- BLOCK CHAIN ----')
user = User(0)
print('Finding suitable N')
difficulty = controlGUI(user)


users = []
numUsers = randint(2,10)
totalMiningTime = 0
for i in range(numUsers):
    user = User(i)
    users.append(user)
print('Number of users is ' , numUsers)

numTurns = randint(5,50)
print('Normal transaction simulation: ')
# Transaction simulation
for i in range(numTurns):
    winner = np.random.choice( np.arange (len(users)))
    users[winner].blockChain.appendTx('Transaction' + str(winner))
    time1 = time.time()
    newBlock = users[winner].blockChain.mine()
    time2 = time.time()
    totalMiningTime = totalMiningTime + time2 - time1
    # print('Block mined in ' + str(time2 - time1))
    broadcastTransaction(users, users[winner], newBlock)

write_to_text_file(users[0].blockChain.chainOfTx)

print('Resulted blockchain: ')
for block in users[0].blockChain.chainOfTx:
    print(block.__dict__)



# Attack Simulation!
print('attack simulation: ')
users = []
for i in range(numUsers):
    user = User(i)
    users.append(user)
# print(users)

# assume computational power is 100

attackerComputationalPower = randint(20, 100)
attackerUserNumber = randint(0,numUsers - 1)
attackerMiningTime = 0
normalMiningTime = 0
nodeUserNumber = 0
attackerTurns = 0
nodeTurns = 0

for i in range(numTurns):
    if(randint(0,100) <= attackerComputationalPower):
        #attacker's turn
        time1 = time.time()
        users[attackerUserNumber].blockChain.appendTx('Transaction' + str(attackerUserNumber))
        users[attackerUserNumber].blockChain.mine()
        time2 = time.time()
        # print('Block mined in ' + str(time2 - time1))
        attackerMiningTime = attackerMiningTime + time2 - time1
        attackerTurns = attackerTurns + 1
    else:
        #normal node's turn
        time1 = time.time()
        users[nodeUserNumber].blockChain.appendTx('Transaction' + str(nodeUserNumber))
        users[nodeUserNumber].blockChain.mine()
        time2 = time.time()
        normalMiningTime = normalMiningTime + time2 - time1
        #mine in normal chain
        nodeTurns = nodeTurns + 1
        nodeUserNumber = nodeUserNumber + 1
        if nodeUserNumber == attackerUserNumber:
            nodeUserNumber = nodeUserNumber + 1
        if nodeUserNumber == numUsers:
            nodeUserNumber = 0
#see who wins.
if(attackerTurns > nodeTurns):
    print('Attacker wins')
    #relative speed is number of turns?
else:
    print('Attacker loses')

print('total mining time in normal simulation is: ' + str(totalMiningTime * int(numUsers / 2)))
# print('Total nodes mining time in attack simulation is: ' + str(normalMiningTime * int(numUsers / 2)))
print('Attacker time is: ' + str(attackerMiningTime))



