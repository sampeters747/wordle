from typing import List


def import_wordlist(file_location: str) -> List[str]:
    with open(file_location, "r") as f:
        words = f.readlines()
    words = [word.strip() for word in words]
    return words


allowed_guesses = import_wordlist("wordle-allowed-guesses.txt")
answers = import_wordlist("wordle-answers-alphabetical.txt")
all_words = allowed_guesses + answers
