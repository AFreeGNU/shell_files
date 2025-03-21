import secrets
import sys

characters = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '.', ',', '!', '?', ':', ';', '"', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '+', '-', '*', '/', '(', ')', '[', ']', '{', '}', '@', '§', '$', '%', '&', '~', '#', '_', '<', '>', '|', '^', 'ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß']

def addition(a, b):
    if a+b<100:
        return a+b
    else:
        return a+b-100

def subtraction(a, b):
    if a-b>=0:
        return a-b
    else:
        return a-b+100

def encrypt(key, text):
    global shared_key
    shared_key = key[len(text)*2:]

    list_text = list(map(characters.index, list(text)))
    list_key = list(map(lambda x, y: int(x+y), list(key)[::2], list(key)[1::2]))

    if len(list_text)>len(list_key): raise ValueError('The key is not long enough!')

    enc_message = ''
    for i in range(len(list_text)):
        if addition(list_key[i], list_text[i])<10:
            enc_message += '0'+str(addition(list_key[i], list_text[i]))
        else:
            enc_message += str(addition(list_key[i], list_text[i]))
    return enc_message

def decrypt(key, enc_text):
    global shared_key
    shared_key = key[len(enc_text):]

    list_text = list(map(lambda x, y: int(x+y), list(enc_text)[::2], list(enc_text)[1::2]))
    list_key = list(map(lambda x, y: int(x+y), list(key)[::2], list(key)[1::2]))

    if len(list_text)>len(list_key): raise ValueError('The key is not long enough!')

    dec_message = ''.join([characters[subtraction(list_text[i], list_key[i])] for i in range(len(list_text))])
    return dec_message

def test_if_enc(text):
    ls = list(filter(lambda x: x not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], list(text)))
    if ls == [] and len(text)%2 == 0: return True
    return False

def messenger(key, text):
    if test_if_enc(text): return decrypt(key, text)
    return encrypt(key, text)

def type_message():
    print('Type a message:')
    global shared_key
    i=1
    while i>0:
        x = input()
        i = len(x)
        if i==0:
            key_file = open('/home/hiesl/linux/shell_files/input_files/key.txt', 'w')
            key_file.write(shared_key)
            key_file.close()
            break
        print(messenger(shared_key, x), '\n')
        print('Percentage of left key:', round(100*len(shared_key)/key_length,2), '%' '\n')

def create_key(key_length):
    key = ''
    for _ in range(key_length):
        key += str(secrets.randbelow(10))
    key_file = open('/home/hiesl/linux/shell_files/input_files/key.txt', 'w')
    key_file.write(key)
    key_file.close()

def import_key():
    global shared_key
    global key_length
    key_file = open('/home/hiesl/linux/shell_files/input_files/key.txt', 'r')
    shared_key = key_file.read()
    key_length = len(shared_key)
    key_file.close()

def help():
    print("""Arguments must be passed in the order as shown:    [keylen]
             - [keylen] in int, only if new key should be generated. (OPTIONAL)""")

if(len(sys.argv) == 2 and sys.argv[1].isdigit()):
    create_key(int(sys.argv[1]))
    import_key()
    type_message()
elif str(sys.argv[1]) == "pass":
    import_key()
    type_message()
else:
    help()
