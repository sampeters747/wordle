from typing import Callable, List

def wordle_filter(word: str) -> bool:
    if len(word) != 5:
        return False
    for c in word:
        if (not c.isalpha()) or c.isupper():
            return False
    return True

def create_wordlist(file_location: str, word_filter: Callable[[str], bool]) -> List[str]:
    with open(file_location, "r") as f:
        words = f.readlines()
    words = [word.strip() for word in words]
    print(len(words))
    target_words = list(filter(word_filter, words))
    print(len(target_words))
    target_word_lines = [word + "\n" for word in target_words]
    with open("5lwords.txt", "w") as f:
        f.writelines(target_word_lines)
    return target_words

def import_5lwords(file_location: str="5lwords.txt") -> List[str]:
    with open(file_location, "r") as f:
        words = f.readlines()
    words = [word.strip() for word in words]
    return words

