import random
import time

import matplotlib.pyplot as plt
import numpy as np

# Number of potential recipients
nRecipients = 1000
# Maximum number of hops in a route
maxNumOfHops = 4
# Minimum number of hops in a route
minNumOfHops = 1
# Minimum number of transmissions in a burst
a = 1
# Maximum number of transmissions in a burst
b = 2
# Number of real packets per burst
numOfRealPerBurst = 1  
# Maximum number of branches at each hop
maxBranching = 2  

# Real recipient ID
realRecipient = 15  

# List to store recipient data for the histogram
recipientsData = []  

# Number of simulation cycles
numOfCycles = 100
# Maximum deviation from the mean frequency for recipient selection
maxDeviation = 0.1  

# Counter for real recipient occurrences
realNum = 0  

# Get current time in milliseconds
def current_milli_time():
    return round(time.time() * 1000)

# Initialize random number generator with current time
random.seed(current_milli_time())  

# Define a class to represent a node in the routing graph
class RNode:
    def __init__(self, id):
        self.id = id
    id = 0
    nextHops = []

# Function to count the frequency of items in a list
def CountFrequency(my_list):
    freq = {}
    for item in my_list:
        if item in freq:
            freq[item] += 1
        else:
            freq[item] = 1
    return freq

# Function to calculate the mean frequency of a frequency dictionary
def getMeanFreq(freq):
    if len(freq) == 0:
        return 0
    meanFreq = sum(freq.values()) / len(freq)
    return meanFreq

# Function to calculate a randomized mean frequency with deviation
def getMeanFreqRandom(maxDeviation, freq):
    meanFreq = getMeanFreq(freq)
    deviation = random.uniform(0, maxDeviation)
    meanFreq = meanFreq * deviation + meanFreq
    return meanFreq

# Function to get the frequency of a specific recipient from the frequency dictionary
def getFreqOfRecipient(freq, recipientID):
    return freq.get(recipientID, 0)

# Function to check if a recipient's frequency is above the randomized average
def aboveAverage(recipientsData, recipientID):
    result = False
    freq = CountFrequency(recipientsData)
    mean = getMeanFreqRandom(maxDeviation, freq)
    realFreq = getFreqOfRecipient(freq, recipientID)
    if realFreq == 0:
        return result
    if realFreq > mean:
        result = True
    return result

# Function to select a fake recipient, avoiding the real recipient if its frequency is above average
def getFakeRecipient(recipients, realRecipient, recFreqs):
    fakeindex = random.randint(0, len(recipients) - 1)
    fakeRecipient = recipients[fakeindex]
    if fakeRecipient == realRecipient and aboveAverage(recFreqs, realRecipient):
        mod = random.randint(1, len(recipients) - 1)
        plus = bool(random.getrandbits(1))
        if plus:
            fakeindex = fakeindex + mod
            if fakeindex > len(recipients) - 1:
                fakeindex = len(recipients) - 1
        else:
            fakeindex = fakeindex - mod
            if fakeindex < 0 and not aboveAverage(recFreqs, recipients[0]):
                fakeindex = 0
            else:
                fakeindex = random.randint(0, len(recipients) - 1)
    fakeRecipient = recipients[fakeindex]
    return fakeRecipient

# Function to recursively generate a routing graph with fake and real recipients
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
    currentHop = currentHop + 1
    for i in range(hopsNbranchingum):
        nextNode = getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq)
        if nextNode is not None:
            node.nextHops.append(nextNode)
    return node

# Function to generate a package route with a specified number of hops and branching
def getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, recipientsFreq):
    hopsNum = random.randint(minNumOfHops, maxNumOfHops)
    addedReal = False
    realRecHop = 0
    if shouldContainReal:
        realRecHop = random.randint(1, hopsNum)
    node = getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, 0, hopsNum, realRecHop, recipientsFreq)
    return node

# Function to generate a package route with a specified number of hops
def getPackageRoute(recipients, maxNumOfHops, realRecipient, hasReal, recipientsFreq):
    hopsNum = random.randint(minNumOfHops, maxNumOfHops)
    route = []
    addedReal = False
    global realNum
    if hasReal:
        realRecHop = random.randint(1, hopsNum)
    for i in range(hopsNum):
        if hasReal and realRecHop == i + 1:
            route.append(realRecipient)
            addedReal = True
            recipient = realRecipient
        else:
            recipient = getFakeRecipient(recipients, realRecipient, recipientsFreq)
        if recipient == realRecipient:
            realNum = realNum + 1
        route.append(recipient)
        recipientsData.append(recipient)
    print(hasReal)
    return route

# Function to generate multiple package routes with varying number of transmissions and branching
def getRoutesNew(recipients, minTransNum, maxTransNum, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, hasReal, recipientsFreq):
    n_trans = random.randint(minTransNum, maxTransNum)  # Number of transmissions
    print("Number of transmissions: " + str(n_trans))
    realWasSent = False
    if not hasReal:
        realWasSent = True  # Prevents infinite loop if all packages are fake
    nSent = 0
    counter = 0
    stop = False
    while not stop:
        if counter >= n_trans:
            if realWasSent:
                stop = True
                break
        counter = counter + 1
        toSendReal = False
        if hasReal and nSent < numOfRealPerBurst:
            toSendReal = bool(random.getrandbits(1))
        node = getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, toSendReal, realWasSent, recipientsFreq)
        if toSendReal:
            realWasSent = True
            nSent = nSent + 1
    return node

# Function to generate multiple package routes with varying number of transmissions
def getRoutes(recipients, maxNumOfHops, realRecipient, hasReal, minTransNum, maxTransNum, recipientsFreq):
    n_trans = random.randint(minTransNum, maxTransNum)  # Number of transmissions
    print("Number of transmissions: " + str(n_trans))
    realWasSent = False
    if not hasReal:
        realWasSent = True  # Prevents infinite loop if all packages are fake
    nSent = 0
    counter = 0
    stop = False
    while not stop:
        if counter >= n_trans:
            if realWasSent:
                stop = True
        counter = counter + 1
        toSendReal = False
        if hasReal and nSent < numOfRealPerBurst:
            toSendReal = bool(random.getrandbits(1))
        getPackageRoute(recipients, maxNumOfHops, realRecipient, toSendReal, recipientsFreq)
        if toSendReal:
            realWasSent = True
            nSent = nSent + 1

# Generate a list of recipients
recipients = [*range(1, nRecipients + 1, 1)]
print("Number of recipients: " + str(len(recipients)))

# Counter for the number of real packages sent
numOfRealPackages = 0  

# Generate a package route using the new method
node = getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxBranching, realRecipient, True, False, recipientsData)

# Simulate multiple cycles of message sending
for i in range(numOfCycles):
    # Randomly determine if the current transmission should include a real package
    hasReal = bool(random.getrandbits(1))
    # If the real recipient's frequency is above average, do not send a real package
    if aboveAverage(recipientsData, realRecipient):
        hasReal = False
    if hasReal:
        numOfRealPackages += 1
    print("Has real package: " + str(hasReal))
    # Generate routes for the current transmission
    getRoutes(recipients, 10, realRecipient, hasReal, a, b, recipientsData)

# Print statistics
print("Number of real packages sent: " + str(numOfRealPackages))
print("Real recipient count: " + str(realNum))

# Plot a histogram of recipient frequencies
plt.hist(recipientsData, bins=nRecipients, color='skyblue', edgecolor='black')

# Calculate and print frequency statistics
freq = CountFrequency(recipientsData)
print("Mean frequency: " + str(getMeanFreq(freq)))
print("15 frequency: " + str(getFreqOfRecipient(freq, 15)))

# Add labels and title to the histogram
plt.xlabel('Recipient ID')
plt.ylabel('Frequency')
plt.title('Recipient Frequency Histogram')

# Display the histogram
plt.show()