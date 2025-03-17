import numpy as np
import datetime as dt
import sys

pi = str(np.genfromtxt("/home/hiesl/linux/shell_files/input_files/pi.txt", dtype=str))

def pao(w_pos, start_digit):
    if w_pos % 6 == 0:
        w_pos -= 1
    return pi[start_digit+int((w_pos)//6)*6:start_digit+int((w_pos)//6)*6+6:1]

def in_inp(inp, i, offset):
    if (i+offset+1) % 6 == 0:
        i -= 1
    skip = ((i+offset)//6)*6-offset
    return str(inp)[skip:skip+6:1]

def Ask_Pi(start_digit=0, mistake_limit=20):
    print("Push ENTER to start the timer!")
    enter = input()
    if len(enter) == 0:
        print(f"Start from digit {start_digit}!")
        start = dt.datetime.now()
    else: return print("Attempt aborted!")
    inp = input()
    if str(inp) == pi[start_digit:(len(str(inp))+start_digit)]:
        print("Everything is correct!")
        print("You learned: ", len(str(inp)), " digits of pi.")
        stop = dt.datetime.now()
    else:
        stop = dt.datetime.now()
        print("Incorrect!")
        mistake_count = 0
        offset = 0
        veto = 0
        for i in range(len(inp)):
            if str(inp)[i]==pi[i+start_digit+offset]:
                continue
            else:
                not_count = 0
                if mistake_count+offset == 0 and veto == 0:
                    print("Only the first", i, "digits of pi were correct.")
                try: str(inp)[i]==pi[i+1+start_digit+offset] and str(inp)[i+1]==pi[i+2+start_digit+offset] and str(inp)[i+2]==pi[i+3+start_digit+offset]
                except: not_count += 1
                else:
                    if str(inp)[i]==pi[i+1+start_digit+offset] and str(inp)[i+1]==pi[i+2+start_digit+offset] and str(inp)[i+2]==pi[i+3+start_digit+offset]:
                        print("You missed digit", i+offset+1, "which is:", pi[i+start_digit+offset], " (PAO:" + str(pao(i+offset+1, start_digit)) + ")  in:", in_inp(inp, i, offset))
                        offset += 1
                        mistake_count += 1
                    else:
                        not_count += 1
                try: str(inp)[i]==pi[i+2+start_digit+offset] and str(inp)[i+1]==pi[i+3+start_digit+offset] and str(inp)[i+2]==pi[i+4+start_digit+offset]
                except: not_count += 1
                else:
                    if str(inp)[i]==pi[i+2+start_digit+offset] and str(inp)[i+1]==pi[i+3+start_digit+offset] and str(inp)[i+2]==pi[i+4+start_digit+offset]:
                        print("You missed two digits", i+offset+1, "and", i+offset+2, "which are:", str(pi[i+start_digit+offset]) + str(pi[i+1+start_digit+offset]), " (PAO:" + str(pao(i+offset+1, start_digit)) + ")")
                        offset += 2
                        mistake_count += 1
                    else:
                        not_count += 1
                try: str(inp)[i]==pi[i+6+start_digit+offset] and str(inp)[i+1]==pi[i+7+start_digit+offset] and str(inp)[i+2]==pi[i+8+start_digit+offset]
                except: not_count += 1
                else:
                    if str(inp)[i]==pi[i+6+start_digit+offset] and str(inp)[i+1]==pi[i+7+start_digit+offset] and str(inp)[i+2]==pi[i+8+start_digit+offset]:
                        print("You missed six digits between", i+offset+1, "and", i+offset+6, "which are:", pi[i+start_digit+offset:i+6+start_digit+offset:1])
                        offset += 6
                        mistake_count += 1
                    else:
                        not_count += 1
                try: str(inp)[i+1]==pi[i+start_digit+offset] and str(inp)[i+2]==pi[i+1+start_digit+offset] and str(inp)[i+3]==pi[i+2+start_digit+offset]
                except: not_count += 1
                else:
                    if str(inp)[i+1]==pi[i+start_digit+offset] and str(inp)[i+2]==pi[i+1+start_digit+offset] and str(inp)[i+3]==pi[i+2+start_digit+offset]:
                        print("You added a digit between", i+offset, "and", i+offset+1, " (PAO:" + str(pao(i+offset+1, start_digit)) + ") in:", in_inp(inp, i, offset))
                        offset -= 1
                        veto = 1
                        mistake_count += 1
                    else:
                        not_count += 1
                if not_count == 4:
                    print("You got position", i+offset+1, "wrong:", str(inp)[i], "should be", pi[i+start_digit+offset], " (PAO:" + str(pao(i+offset+1, start_digit)) + ") in:", in_inp(inp, i, offset))
                    mistake_count += 1
                if mistake_count >= mistake_limit:
                    print("Too many mistakes!")
                    return print("You took: ", stop-start)
        print("You got a total of", len(str(inp))-mistake_count, "digits of", len(str(inp))+offset, "correct!")
    print("You took: ", stop-start)

def help():
    print("""Arguments must be passed in the order as shown:    [start_digit] [mistake_limit]
             - [start_digit] is the start digit of pi (default=0).
             - [mistake_limit] is the upper bound of mistakes (default=20).""")

if(len(sys.argv) == 3 and sys.argv[1].isdigit() and sys.argv[2].isdigit()):
    Ask_Pi(int(sys.argv[1]), int(sys.argv[2]))
else:
    help()
