import random
import time

import matplotlib.pyplot as plt
import numpy as np

nRecipients = 100 #number of potencial recipients
maxNumOfHops = 2 #max number of hops
minNumOfHops = 2 #min number of hops
a=1 #min number of transmissions
b=1 #max number of transmissions
numOfRealPerBurst=1 #number of real packets
maxBranching = 2 #maximum nuber of branching

realRecipient = 15 #real recipient ID

recipientsData=[] #for histogram

numOfCycles = 1000
maxDeviation = 0.1

realNum=0

#get current time in ms
def current_milli_time():
    return round(time.time() * 1000)

random.seed(current_milli_time()) #randomize

class RNode:
  
  def __init__(self, id):
    self.id = id

  id = 0
  nextHops = []

def CountFrequency(my_list):
 
    # Creating an empty dictionary
    freq = {}
    for item in my_list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
   #  for key, value in freq.items():
   #      print("% d : % d" % (key, value))
            
    return freq


def getMeanFreq(freq):
   if len(freq)==0:
      return 0
   meanFreq = sum(freq.values()) / len(freq)
   return meanFreq

def getMeanFreqRandom(maxDeviation, freq):
   meanFreq = getMeanFreq(freq)
   deviation = random.uniform(0, maxDeviation)
   meanFreq=meanFreq*deviation + meanFreq
   return meanFreq
 
def getFreqOfRecipient(freq, recipientID):
   return freq.get(recipientID, 0)

def aboveAverage(recipientsData, recipientID):
   result = False
   freq = CountFrequency(recipientsData)
   #mean = getMeanFreq(freq)
   mean = getMeanFreqRandom(maxDeviation,freq)
   realFreq = getFreqOfRecipient(freq, recipientID)

   if realFreq==0:
      return result

   if realFreq>mean:
      result=True
   
   return result

def getFakeRecipient(recipients, realRecipient, recFreqs):
   fakeindex = random.randint(0, len(recipients)-1)
   fakeRecipient = recipients[fakeindex]
   if fakeRecipient==realRecipient and aboveAverage(recFreqs, realRecipient):
      mod=random.randint(1,len(recipients)-1)
      plus = bool(random.getrandbits(1))
      if plus:
         fakeindex = fakeindex + mod
         if fakeindex>len(recipients)-1:
            fakeindex=len(recipients)-1
      else:
         fakeindex = fakeindex - mod
         if fakeindex<0 and not aboveAverage(recFreqs, recipients[0]):
            fakeindex=0    
         else:
            fakeindex = random.randint(0, len(recipients)-1)

              
   fakeRecipient = recipients[fakeindex]
   return fakeRecipient

def getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq):

   if currentHop>hopsNum:
      return None
   
   hopsNbranchingum= random.randint(1, maxNumOfBranching)
   
   if shouldContainReal and realHopNum==currentHop and not addedReal:
      node = RNode(realRecipient)
      addedReal=True
   else:
      node=RNode(getFakeRecipient(recipients,realRecipient, recipientsFreq))
   
   recipientsFreq.append(node.id)

   currentHop=currentHop+1

   for i in range(hopsNbranchingum):
      nextNode = getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq)
      if not nextNode==None:
         node.nextHops.append(getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, currentHop, hopsNum, realHopNum, recipientsFreq))

   return node

def getPackageRouteNew(recipients, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, recipientsFreq):

   hopsNum= random.randint(minNumOfHops, maxNumOfHops)
  
   addedReal=False

   realRecHop = 0
   if shouldContainReal:
      realRecHop = random.randint(1, hopsNum)

   node = getHops(recipients, maxNumOfBranching, realRecipient, shouldContainReal, addedReal, 0, hopsNum, realRecHop, recipientsFreq) 
  
   return node

#builds a package route: recipients list, max number of hops, real recipient ID, flag if the route contains real recipient
def getPackageRoute(recipients, maxNumOfHops, realRecipient, hasReal, recipientsFreq):
   
   hopsNum= random.randint(minNumOfHops, maxNumOfHops)
   route=[]
   addedReal=False

   global realNum

   if hasReal:
      realRecHop = random.randint(1, hopsNum)
   for i in range(hopsNum):
      if hasReal and realRecHop==i+1:
         route.append(realRecipient)
         addedReal=True
         recipient = realRecipient
      else:
        recipient = getFakeRecipient(recipients, realRecipient, recipientsFreq)
              
      if recipient==realRecipient:
         realNum=realNum+1
      route.append(recipient)
      recipientsData.append(recipient)

   
   print(hasReal)
   #print (route)
   return route

#generate multiple routes
def getRoutesNew(recipients, minTransNum, maxTransNum, minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, hasReal, recipientsFreq):

   n_trans = random.randint(minTransNum, maxTransNum) #number of transmissions
   print("Number of transsmissions: " + str(n_trans))
 

   realWasSent = False
   if not hasReal:
      realWasSent = True   #Prevents infinite while loop in case of all packages are fake

   nSent=0
   counter = 0
   stop=False
   while(not stop):
      if(counter>=n_trans):
         if(realWasSent):
            stop=True
            break
   
      counter=counter+1
      toSendReal = False
      if (hasReal and nSent<numOfRealPerBurst):
         toSendReal = bool(random.getrandbits(1))
      node = getPackageRouteNew(recipients,minNumOfHops, maxNumOfHops, maxNumOfBranching, realRecipient, toSendReal, realWasSent, recipientsFreq)
      if(toSendReal):
         realWasSent=True
         nSent=nSent+1
   
   return node

#generate multiple routes
def getRoutes(recipients, maxNumOfHops, realRecipient, hasReal, minTransNum, maxTransNum, recipientsFreq):

   n_trans = random.randint(minTransNum, maxTransNum) #number of transmissions
   print("Number of transsmissions: " + str(n_trans))

   

   realWasSent = False
   if not hasReal:
      realWasSent = True   #Prevents infinite while loop in case of all packages are fake

   nSent=0
   counter = 0
   stop=False
   while(not stop):
      if(counter>=n_trans):
         if(realWasSent):
            stop=True
   
      counter=counter+1
      toSendReal = False
      if (hasReal and nSent<numOfRealPerBurst):
         toSendReal = bool(random.getrandbits(1))
      getPackageRoute(recipients, maxNumOfHops, realRecipient, toSendReal, recipientsFreq)
      if(toSendReal):
         realWasSent=True
         nSent=nSent+1
      


recipients = [*range(1, nRecipients+1, 1)] 
print ("number of recipients: " + str(len(recipients)))

numOfRealPackages = 0 #number of real packages

node = getPackageRouteNew(recipients,minNumOfHops,maxNumOfHops, maxBranching, realRecipient, True, False, recipientsData)

# for i in range(numOfCycles):
   # hasReal = bool(random.getrandbits(1)) #contains real message
   # if aboveAverage(recipientsData, realRecipient):
      # hasReal=False
   # if hasReal:
      # numOfRealPackages+=1
   # print("Has real package: " + str(hasReal))
   # getRoutesNew(recipients, a, b, minNumOfHops, maxNumOfHops, maxBranching, realRecipient, recipientsData)

for i in range(numOfCycles):
   hasReal = bool(random.getrandbits(1)) #contains real message
   if aboveAverage(recipientsData, realRecipient):
      hasReal=False
   if hasReal:
      numOfRealPackages+=1
   print("Has real package: " + str(hasReal))
   getRoutes(recipients, 10, realRecipient, hasReal, a, b, recipientsData)

print("Number of real packages sent:" + str(numOfRealPackages))
print("real rec num: " + str(realNum))


#print(recipientsData)

# Plotting a basic histogram
plt.hist(recipientsData, bins=nRecipients, color='skyblue', edgecolor='black')

freq = CountFrequency(recipientsData)

print("Mean freq: " + str(getMeanFreq(freq)))
print("15 freq: " + str(getFreqOfRecipient(freq, 15)))

 
# Adding labels and title
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.title('Basic Histogram')
 
# Display the plot
plt.show()