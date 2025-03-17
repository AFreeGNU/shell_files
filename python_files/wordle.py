import numpy as np
import sys

wordsstring = ''.join(np.genfromtxt("/home/hiesl/linux/shell_files/input_files/2309-wordle-words.txt", delimiter = " ", dtype=str))
full_words = np.genfromtxt("/home/hiesl/linux/shell_files/input_files/valid-wordle-words.txt", dtype=str)
old_words = np.genfromtxt("/home/hiesl/linux/shell_files/input_files/old-wordle-words.txt", dtype=str)
abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
green = []
yellow = []

def convert_string_to_list(string):
    substring_list = []
    for i in range(0, len(string), 5):
        substring = string[i:i+5]
        substring_list.append(substring)
    return substring_list

words = convert_string_to_list(wordsstring)
# rd.shuffle(words)

def remove_letters(word_list, letter, pos):
    return [string for string in word_list if string[int(pos)] != str(letter)]

def green_letters(word_list, letter, pos):
    return [string for string in word_list if string[int(pos)] == str(letter)]

def yellow_letters(word_list, letter_to_include, pos):
    return [string for string in word_list if all(letter in string for letter in letter_to_include) and string[int(pos)] != str(letter_to_include)]

def find_doubles(word_list, letter, count):
    return [string for string in word_list if string.count(str(letter)) > count]

def remove_doubles(word_list, letter, count):
    return [string for string in word_list if string.count(str(letter)) <= count]

def gby(word_list, letter, count_green, pos):
    return [string for string in word_list if string.count(str(letter)) == count_green + 1 and string[int(pos)] != str(letter)]

def a_word(word, color_encoding):
    global words
    global green
    global yellow
    temp_list = list(word)
    veto_letter = ""
    for j,i in enumerate(color_encoding):
        if i == 1:
            yellow.append(temp_list[j])
            indices = [i for i in range(5) if temp_list[i] == word[j]]
            count_green = 0
            for index in indices:
                if color_encoding[index] == 2:
                    count_green += 1
            count_black = 0
            for index in indices:
                if color_encoding[index] == 0:
                    count_black += 1
            if count_green > 0 and not count_black > 0:
                words = find_doubles(words, word[j], count_green)
            elif count_black > 0 and not count_green > 0:
                words = remove_doubles(words, word[j], count_black)
            elif count_green > 0 and count_black > 0:
                veto_letter = word[j]
                for index in indices:
                    if color_encoding[index] != 2 and word[j] != temp_list[i]:
                        words = remove_letters(words, word[j], index)
                words = gby(words, word[j], count_green, j)
            words = yellow_letters(words, word[j], j)
        elif i == 2:
            words = green_letters(words, word[j], j)
            green.append(temp_list[j])
        elif i == 0:
            if temp_list.count(word[j]) == 1:
                for n in range(5):
                    words = remove_letters(words, word[j], n)
            else:
                if word[j] == veto_letter:
                    continue
                else:
                    indices = [i for i in range(5) if temp_list[i] == word[j]]
                    two_list = []
                    for index in indices:
                        if color_encoding[index] == 2:
                            two_list.append(index)
                    if two_list:
                        remove_indices = list(set(range(5)) - set(two_list))
                        for index in remove_indices:
                            words = remove_letters(words, word[j], index)
                    else:
                        for m in indices:
                            words = remove_letters(words, word[m], m)
        else:
            help()

def wordle(word_list, enc_list):
    global words
    for i in range(len(word_list)):
        a_word(word_list[i], enc_list[i])
    return words

def make_word_list(input_string):
    word_list = []
    for i in range(len(input_string)//5):
        word_list.append(input_string[5*i:5*i+5])
    return word_list

def make_int_list(input_string):
    int_list = []
    for i in range(len(input_string)//5):
        sub_list = []
        for j in range(5):
            sub_list.append(int(input_string[5*i:5*i+5][j]))
        int_list.append(sub_list)
    return int_list

def check_word_list(input_string):
    try:
        make_word_list(input_string)
    except:
        return False
    else:
        return True

def check_int_list(input_string):
    try:
        make_int_list(input_string)
    except:
        return False
    else:
        return True

def order_words(word_list):
    word_unique_counts = {}
    for word in word_list:
        word_unique_counts[word] = len(set(word))
    ordered_words = sorted(word_list, key=lambda x: word_unique_counts[x])
    print("There are", len(word_list), "possible words:")
    return ordered_words[::-1]

def count_letters(word_list):
    words_string = ''.join(word_list)
    letter_counts = []
    for i in abc:
        letter_counts.append(words_string.count(i))
    letter_dict = {k: v for k, v in zip(abc, letter_counts)}
    return letter_dict

def find_word_impossible(word_list):
    global green
    global yellow
    letter_dict = count_letters(word_list)
    weigth_dict = {}
    for word in full_words:
        count = 0
        if len(set(word)) == 5:
            for letter in word:
                if letter in green or letter in yellow:
                    count -= 10
                else:
                    count += letter_dict.get(letter)
        weigth_dict[word] = count
    key_with_largest_value = sorted(weigth_dict, key=lambda x: weigth_dict[x])[-3:][::-1]
    print("The best three words without already used letters are:")
    return key_with_largest_value

def find_word(word_list):
    letter_dict = count_letters(word_list)
    weigth_dict = {}
    for word in word_list:
        count = 0
        if len(set(word)) == 5:
            for letter in word:
                count += letter_dict.get(letter)
        else:
            for letter in word:
                count += letter_dict.get(letter)//2
        weigth_dict[word] = count
    key_with_largest_value = sorted(weigth_dict, key=lambda x: weigth_dict[x])[-3:][::-1]
    print("The best three possible words are:")
    return key_with_largest_value

def find_word_without_old(word_list):
    length = len(word_list)
    letter_dict = count_letters(word_list)
    weigth_dict = {}
    for word in word_list:
        count = 0
        if len(set(word)) == 5:
            for letter in word:
                count += letter_dict.get(letter)
        else:
            for letter in word:
                count += letter_dict.get(letter)//2
        weigth_dict[word] = count
    key_with_largest_value = sorted(weigth_dict, key=lambda x: weigth_dict[x])[-3:][::-1]
    print(f"The best three possible words excluding already used words are (total {length}):")
    return key_with_largest_value

def help():
    print("""Arguments must be passed in the order as shown:    [words] [pos]
             - [words] in string, no spaces (no default).
             - [pos] in string, no spaces, 0 for grey, 1 for yellow, 2 for green (no default).""")

if(len(sys.argv) == 3 and check_word_list(str(sys.argv[1])) and check_int_list(str(sys.argv[2]))):
    print(order_words(wordle(make_word_list(str(sys.argv[1])), make_int_list(str(sys.argv[2])))), "\n")
    print(find_word_impossible(words), "\n")
    print(find_word(words), "\n")
    words_without_olds = [item for item in words if item not in old_words]
    print(find_word_without_old(words_without_olds))
else:
    help()
