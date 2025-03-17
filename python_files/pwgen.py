import secrets
import sys
import numpy as np
import math

ascii = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '.', ',', '!', '?', ':', ';', "'", '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '+', '-', '*', '/', '(', ')', '[', ']', '{', '}', '@', '§', '$', '%', '&', '~', '#', '_', '<', '>', '|', '^', 'ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß']
num_cs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
num_ci = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
cs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ci = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
bin = ['0', '1']
pao = ['a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x']
dice_en = np.genfromtxt("/home/hiesl/linux/shell_files/input_files/dice_en.txt", dtype=str)
dice_de = np.genfromtxt("/home/hiesl/linux/shell_files/input_files/dice_de.txt", dtype=str)

def create_password(pw_length, pw_signs):
    global bits
    password = ""
    bits = round(math.log(len(pw_signs),2)*pw_length,1)
    if len(pw_signs) != len(dice_de):
        for i in range(pw_length):
            password += str(secrets.choice(pw_signs))
    else:
        for i in range(pw_length):
            password += str(secrets.choice(pw_signs))
            if i < pw_length-1:
                password += "-"
    return password

def help():
    print("""Arguments must be passed in the order as shown:    [pwlen] [pwchars] [bits]
             - [pwlen] is the length of the password as int (default=20).
             - [pwchars] is either in {ascii, num_cs, num_ci, cs, ci, num, bin, pao, dice_en, dice_de} or any string (default=num_cs).
             - [bits] calculates the password strength if "bits" is passed (optional).""")

if(len(sys.argv) == 4 and sys.argv[1].isdigit()):
    password = create_password(int(sys.argv[1]), eval(sys.argv[2]) if sys.argv[2] in ['ascii', 'num_cs', 'num_ci', 'cs', 'ci', 'num', 'bin', 'pao', 'dice_en', 'dice_de'] else sys.argv[2])
    if str(sys.argv[3]) == "bits":
        print(password)
        print("Strength:", bits, "bits.")
    elif sys.argv[3] == "pass":
        print(password)
    else:
        help()
else:
    help()
