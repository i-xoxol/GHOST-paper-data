import random
import time

import matplotlib.pyplot as plt
import numpy as np

# Simulation parameters
nRecipients = 100  # Number of potential recipients
maxNumOfHops = 4  # Max number of hops
minNumOfHops = 2  # Min number of hops
a = 1  # Min number of transmissions
b = 2  # Max number of transmissions
numOfRealPerBurst = 1  # Number of real packets
maxBranching = 10  # Maximum number of branching
realRecipient = 15  # Real recipient ID
numOfCycles = 1000
maxDeviation = 0.1

# Global variables
recipientsData = []  # For histogram
realNum = 0

# Get current time in ms
def current_milli_time():
    return round(time.time() * 1000)

random.seed(current_milli_time())  # Randomize

class RNode:
    def __init__(self, id):
        self.id = id
        self.nextHops = []

# Function to count the frequency of items in a list
def CountFrequency(my_list):
    freq = {}
    for item in my_list:
        freq[item] = freq.get(item, 0) + 1
    return freq

# Function to calculate the mean frequency of a frequency dictionary
def getMeanFreq(freq):
    return sum(freq.values()) / len(freq) if freq else 0

# Function to calculate a randomized mean frequency
def getMeanFreqRandom(maxDeviation, freq):
    meanFreq = getMeanFreq(freq)
    deviation = random.uniform(0, maxDeviation)
    return meanFreq * (1 + deviation)

# Function to get the frequency of a specific recipient
def getFreqOfRecipient(freq, recipientID):
    return freq.get(recipientID, 0)

# Function to check if a recipient's frequency is above the randomized average
def aboveAverage(recipientsData, recipientID):
    freq = CountFrequency(recipientsData)
    mean = getMeanFreqRandom(maxDeviation, freq)
    realFreq = getFreqOfRecipient(freq, recipientID)
    return realFreq > mean if realFreq else False

# Function to get a fake recipient ID, ensuring it's not the real recipient if its frequency is above average
def getFakeRecipient(recipients, realRecipient, recFreqs):
    fakeRecipient = random.choice(recipients)
    while fakeRecipient == realRecipient and aboveAverage(recFreqs, realRecipient):
        fakeRecipient = random.choice(recipients)
    return fakeRecipient

# Recursive function to generate hops for a package route
def getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq):
    if currentHop > hopsNum:
        return None

    hopsNbranchingum = random.randint(1, maxNumOfBranching)

    if shouldContainReal and realHopNum == currentHop and not addedReal:
        node = RNode(realRecipient)
        addedReal = True
    else:
        node = RNode(getFakeRecipient(recipients, realRecipient, recipientsFreq))

    recipientsFreq.append(node.id)
    currentHop += 1

    for _ in range(hopsNbranchingum):
        nextNode = getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq)
        if nextNode:
            node.nextHops.append(nextNode)

    return node

# Function to generate a package route with a randomized number of hops
def getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, recipientsFreq):
    hopsNum = random.randint(minNumOfHops, maxNumOfHops)
    realRecHop = random.randint(1, hopsNum) if shouldContainReal else None
    return getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, 1, hopsNum, realRecHop, recipientsFreq)

# Function to generate multiple package routes with a randomized number of transmissions
def getRoutesNew(recipients, minTransNum, maxTransNum, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, hasReal, recipientsFreq):
    n_trans = random.randint(minTransNum, maxTransNum)
    print("Number of transmissions:", n_trans)

    realWasSent = not hasReal  # Initialize to True if no real package is to be sent
    nSent = 0
    counter = 0

    while counter < n_trans or (hasReal and not realWasSent):
        toSendReal = hasReal and nSent < numOfRealPerBurst and random.getrandbits(1)
        node = getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, toSendReal, realWasSent, recipientsFreq)
        if toSendReal:
            realWasSent = True
            nSent += 1
        counter += 1

    return node

# Generate recipient list
recipients = list(range(1, nRecipients + 1))
print("Number of recipients:", len(recipients))

# Generate package routes
numOfRealPackages = 0
for _ in range(numOfCycles):
    hasReal = random.getrandbits(1)  # Determine if a real message should be sent
    if aboveAverage(recipientsData, realRecipient):
        hasReal = False
    if hasReal:
        numOfRealPackages += 1
    print("Has real package:", hasReal)
    getRoutesNew(recipients, a, b, minNumOfHops, maxNumOfHops, maxBranching, realRecipient, hasReal, recipientsData)

print("Number of real packages sent:", numOfRealPackages)

# Plot histogram of recipient frequencies
plt.hist(recipientsData, bins=nRecipients, color='skyblue', edgecolor='black')
freq = CountFrequency(recipientsData)
print("Mean freq:", getMeanFreq(freq))
print("15 freq:", getFreqOfRecipient(freq, 15))
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.title('Basic Histogram')
plt.show()