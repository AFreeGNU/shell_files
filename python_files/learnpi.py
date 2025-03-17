import numpy as np
import datetime as dt
import sys

table =  np.genfromtxt("/home/hiesl/linux/shell_files/input_files/pao0099.csv", delimiter=',', dtype= str)[:,1:]

pi = str(np.genfromtxt("/home/hiesl/linux/shell_files/input_files/pi.txt", dtype=str))

def give_pao(n1, n2, place):
    return str(table[int(n1)+3*int(n1)+1+place, int(n2)])

def Learn_Pi(skip=0, pao=0, max_digit=10000):
    i = 1
    pos = skip
    total = 0
    print(f"Push ENTER to start at digit {skip}!")
    enter = input()
    if len(enter) == 0:
        start = dt.datetime.now()
    else: return print("Attempt aborted!")
    while i>0 and not pos>=max_digit:
        number = pi[pos]+pi[pos+1] + " " + pi[pos+2]+pi[pos+3] + " " + pi[pos+4]+pi[pos+5]
        pao_pair = give_pao(pi[pos], pi[pos+1], 0) + " " + give_pao(pi[pos+2], pi[pos+3], 1) + " " + give_pao(pi[pos+4], pi[pos+5], 2)
        print(number)
        if pao == 1:
            print(pao_pair)
        total += 1
        pos += 6
        x = input()
        i = len(x)
        if i!=0:
            break
        else: i=1
    stop = dt.datetime.now()
    print("You learned: ", 6*total, " digits of pi.")
    print("You took: ", stop-start)

def help():
    print("""Arguments must be passed in the order as shown:    [start_digit] [pao] [max_digit]
             - [start_digit] is the start digit of pi (default=0).
             - [pao] in int to show pao pairs (pao=1) (default=0).
             - [max_digit] is the upper bound of digits (default=10000).""")

if(len(sys.argv) == 4 and sys.argv[1].isdigit() and sys.argv[2].isdigit() and sys.argv[3].isdigit()):
    Learn_Pi(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
else:
    help()
