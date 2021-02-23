from nltk.sem import Expression
from nltk.inference import ResolutionProver
import pandas as pd

read_expr = Expression.fromstring
data = pd.read_csv('kb.csv', header=None)
kb= []
[kb.append(read_expr(row)) for row in data[0]]

def check_contradicts(expr, kb):
    contradicts = False
    negative_expr = Expression.negate(expr)
    res = ResolutionProver().prove(negative_expr, kb, verbose=True)
    if res:
        contradicts = True
    return contradicts

def check_csv(kb):
    error = False
    for expr in kb:
        negative_expr = Expression.negate(expr)
        if ResolutionProver().prove(negative_expr, kb, verbose=True):
            error = True
    return error

print(check_csv(kb))