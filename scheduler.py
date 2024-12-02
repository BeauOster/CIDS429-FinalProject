#! /usr/bin/env python3

from __future__ import print_function
import sys
from optparse import OptionParser
import random

# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system", action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times", action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job", action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: SJF, FIFO, RR, PSJF", action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")
parser.add_option("-a", "--maxarrival", default=10, help="Set the max arrival time for jobs", action="store", type="int", dest="maxarrival") # Added new option for max arrival time here

(options, args) = parser.parse_args()

random_seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
    print('ARG jobs', options.jobs)
    print('ARG maxlen', options.maxlen)
    print('ARG seed', options.seed)
else:
    print('ARG jlist', options.jlist)
print('')

print('Here is the job list, with the run time of each job: ')

import operator

joblist = []
if options.jlist == '':
    for jobnum in range(0,options.jobs):
        runtime = int(options.maxlen * random.random()) + 1
        arrival_time = int(options.maxarrival * random.random()) # This is used to generate a random arrival time based on the new option defined earlier
        remaining_time = runtime # since the remaining time will equal the runtime initially
        joblist.append([jobnum, runtime, arrival_time, remaining_time])
        #print('  Job', jobnum, '( length = ' + str(runtime) + ' )')
        print(f'  Job {jobnum} ( length = {runtime}, arrival = {arrival_time} )') #for easier readability (used F-strings)
else:
    jobnum = 0
    for runtime in options.jlist.split(','):
        runtime = float(runtime) #this line was initially in joblist.append below, I just swapped it out for easier readability
        remaining_time = runtime
        arrival_time = int(options.maxarrival * random.random()) # This is used to generate a random arrival time based on the new option defined earlier
        joblist.append([jobnum, runtime, arrival_time, remaining_time])
        jobnum += 1
    for job in joblist:
        #print('  Job', job[0], '( length = ' + str(job[1]) + ' )')
        print(f'  Job {job[0]} (length = {job[1]}, arrival = {job[2]})')
print('\n')

if options.solve == True:
    print('** Solutions **\n')
    if options.policy == 'SJF':
        joblist = sorted(joblist, key=operator.itemgetter(1))
        options.policy = 'FIFO'
    
    if options.policy == 'FIFO':
        thetime = 0
        print('Execution trace:')
        for job in joblist:
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
            thetime += job[1]

        print('\nFinal statistics:')
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for tmp in joblist:
            jobnum  = tmp[0]
            runtime = tmp[1]
            
            response   = t
            turnaround = t + runtime
            wait       = t
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            t += runtime
            count = count + 1
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        print('Execution trace:')
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        for i in range(0,jobcount):
            lastran[i] = 0.0
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        runlist = []
        for e in joblist:
            runlist.append(e)

        thetime  = 0.0
        while jobcount > 0:
            job = runlist.pop(0)
            jobnum  = job[0]
            runtime = float(job[1])
            if response[jobnum] == -1:
                response[jobnum] = thetime
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, runtime])
            else:
                ranfor = runtime;
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor
                jobcount -= 1
            thetime += ranfor
            lastran[jobnum] = thetime

        print('\nFinal statistics:')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0,len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    if options.policy == 'PSJF':

        print('Execution trace:')
        # Sort by arrivale time and then by remaining time (incase 2 jobs have the same arrival time)
        joblist = sorted(joblist, key=lambda x: (x[2], x[3]))
        currentTime = 0.0 # also noted as thetime as defined above in FIFO. I like this naming better. Also changed it to a float for better precision.
        completedJobs = 0
        readyQueue = [] # this is needed because of premption
        jobcount = len(joblist)

        while completedJobs < jobcount:

            # examines each job to see if it should be added to the ready que
            # The job's arrival time must be <= current time (only jobs that have arrived need to be considered)
            # the job must not already be in the ready queue, and needs remaining run time.
            for job in joblist:
                if job[2] <= currentTime and job not in readyQueue and job[3] > 0:
                    readyQueue.append(job)

            readyQueue = sorted(readyQueue, key=lambda x: x[3])  # Sort by remaining time

            if readyQueue:

                # selects the job with the shortest remaining time
                currentJob = readyQueue[0]

                currentTime += 1
                currentJob[3] -= 1

                if currentJob[3] == 0:
                    readyQueue.remove(currentJob)
                    completedJobs += 1
                    #Statistics code here maybe?

            # This is needed if no jobs are ready yet
            else:
                currentTime += 1
        
        # Final stats go here
        



    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR': 
        print('Error: Policy', options.policy, 'is not available.')
        sys.exit(0)
else:
    print('Compute the turnaround time, response time, and wait time for each job.')
    print('When you are done, run this program again, with the same arguments,')
    print('but with -c, which will thus provide you with the answers. You can use')
    print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
    print('to generate different problems for yourself.')
    print('')
