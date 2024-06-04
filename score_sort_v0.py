from __future__ import print_function
import numpy as np



def sort(quantize_per_beat,score):
        #order the events
        eventnumber=0
        outputscore=[]

        for t in np.arange(0,101,1/quantize_per_beat):
            thisbeat_events=[] #temporary array to contain all the events that happened on that beat
            for i in range(len(score)):
                if abs(score[i][3]-t)<0.01:
                    thisbeat_events+=[score[i]]
            #print(str(t)+' thisbeat_events '+str(thisbeat_events))
            sort1=sorted(thisbeat_events, key=lambda x: x[2])
            sort2=sorted(sort1, key=lambda x: x[1])
            #print(str(t)+' sorted '+str(sort2))
            for index,event in enumerate(sort2):
                alreadyhad=0 #remove duplicates
                if index!=0:
                    if event[1:]==sort2[index-1][1:]:
                        alreadyhad=1
                if alreadyhad==0:
                    outputscore+=[[eventnumber]+event[1:]]
                    eventnumber+=1

        return outputscore

if __name__ == "__main__":
    quantize_per_beat=int(input("quantize per beat\n"))
    #score=[[1,144,60,0],[2,144,70,5],[3,128,60,2],[4,144,61,2],[5,128,65,2]]
    score=eval(input("score\n"))
    #print(score)
    print('sorted:\n')
    print(sort(quantize_per_beat,score))
