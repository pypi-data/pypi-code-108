import dirtyopts
import numpy as np
from lmz import *
from sklearn.metrics import f1_score
import matplotlib
matplotlib.use('module://matplotlib-sixel')
import matplotlib.pyplot as plt
##################
# the purpose oof this is to draw a precision recall curve
# should also use the average rank of an instance  as a threshold if multiple seeds were used
#################

doc = '''
--infiles str+ ''      all the csv files
--rawproba bool True   alternatively use the rank of the instance, this might help normalization
--showproblems int 0   output the instances where the method performs worst
--drawAll bool False   if multiple scores were collected per instance, we can display each run seperately
'''

args = dirtyopts.parse(doc)



'''
READ THE DATA
seed -> [[score, tru, instance_name, prediction]]
'''
from collections import defaultdict
print(f" reading csv files: {args.infiles=}")
seeds = defaultdict(list)
for e in args.infiles:
    for line in open(e,'r').read().split('\n')[1:]:
        if len(line) < 4:
            continue
        instance, truth, pred, score, seed  = line.split(',')
        seeds[int(seed)].append( [float(score), int(truth), instance, int(pred) ])



'''
vor each seed list:
    sort it by instance
    -> y and instance name are the same at each iteration
    -> predictions and scores change with each seed so we make a matrix
'''
scores = []
insta = instance
predictions = []
for sti_list  in seeds.values():
    sti_list.sort(key=lambda x: x[2] )
    score, truth, instance, prediction = Transpose(sti_list)
    # truth variable will live on :)
    insta = instance
    predictions.append(prediction)
    scores.append(score)



'''
transform predicted probabilities (in case we dont want to trust them)
then calculate the average score per instance
'''
if not args.rawproba:
    scores = [ np.argsort(np.argsort(s)) for s in scores ]
#avg_score= [np.mean(x) for x in zip(scores)] if len(scores)> 1 else scores[0]
avg_score = [np.mean(x) for x in zip(*scores)]





from sklearn.metrics import precision_recall_curve
precision, recall, thresholds = precision_recall_curve( truth, avg_score)
import structout as so
so.lprint(thresholds)
plt.plot(recall, precision, label=f"mean {'score' if args.rawproba else 'rank'} ({len(scores)} repeats)")
plt.xlabel("recall")
plt.ylabel("precision")
plt.title(f'score: {np.mean([f1_score(truth,x) for x in predictions])} instances: {len(truth)}')

if args.drawAll:
    for s in scores:
        precision, recall, thresholds = precision_recall_curve( truth, s)
        plt.plot(recall, precision)

plt.legend()
plt.show()



'''
we had a case where data was hand-classified, we wanted to identify the instances
where a) the ML method has issues or b) the human made a mistake
therefore we identify the most problematic missclassified instances
'''

if args.showproblems > 0:
    truth = np.array(truth)
    scores2 = np.array(avg_score)

    scoresT = np.array(scores).T
    print('SCORESHAPE',scoresT.shape)
    instances = np.array(insta)
    pmask = truth ==1
    nmask = truth ==0

    sorted_pos = np.argsort( scores2[pmask] )
    print(f"problematic pos instances:")
    for r in [(instances[pmask][x], scores2[pmask][x])  for x in sorted_pos[:args.showproblems]]:
        print(r)
    sorted_neg = np.argsort( -scores2[nmask] )
    print(f"problematic neg instances:")
    for r in [(instances[nmask][x], scores2[nmask][x])  for x in sorted_neg[:args.showproblems]]:
        print(r)

    plt.close()
    plt.hist(scores2[pmask], bins = 100)
    plt.title('positive')
    plt.show()
    plt.close()
    plt.title('negative')
    plt.hist(scores2[nmask], bins = 100)
    plt.show()

