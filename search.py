import logging
from words import all_words, answers
from typing import Dict, List
from enum import Enum, auto
from collections import Counter
from copy import deepcopy

log = logging.getLogger(__name__)


class Feedback:
    def __init__(self, size=5, values=None) -> None:
        if values:
            self.values = values
            self.size = len(values)
        else:
            self.values = " "*size
            self.size = size

    def __getitem__(self, key):
        if key < self.size:
            return self.values[key]
        else:
            raise IndexError('Feedback index out of range')

    def __setitem__(self, key, val):
        if key < len(self.values):
            if val not in "cwu":
                raise ValueError("Feedback can only be the letters: c, w, u")
            self.values = self.values[0:key] + val + self.values[key+1:]
        else:
            raise IndexError('Feedback index out of range')

    def __len__(self):
        return self.size

    def __eq__(self, __o: 'Feedback') -> bool:
        if type(__o) != Feedback:
            return False
        return self.values == __o.values

    def __hash__(self) -> int:
        return hash(self.values)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.values):
            result = self.values[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration


class FeedbackLetter(Enum):
    CORRECT = auto()
    WRONG_SPOT = auto()
    UNUSED = auto()


def get_feedback(guess: str, answer: str) -> Feedback:
    fb = Feedback()
    counter = Counter()
    for c in answer:
        counter[c] += 1
    # First pass handles correctly guessed letters
    for i in range(5):
        g, a = guess[i], answer[i]
        if g == a:
            fb[i] = "c"
            counter[g] -= 1
    # Second pass handles letters that are unused/in the wrong spot
    for i in range(5):
        g, a = guess[i], answer[i]
        if g != a and counter[g]:
            fb[i] = "w"
            counter[g] -= 1
        elif g != a:
            fb[i] = "u"
    return fb


class ConstraintSpace:
    def __init__(self, candidates) -> None:
        self.candidates = candidates
        # self.ordered_candidates
        """
        Letters we know aren't in the word more than a certain amount of times
        ex. 'c':0 means c isn't in the word at all, 'd':1 means d is in the
        word at most 1 times
        """
        self.unused_letters = {}
        # Letters we know are in the word
        self.used_letters = set()
        # Stores correct letters for individual spaces
        self.correct = [None for i in range(5)]
        # Stores incorrect letters for individual spaces
        self.incorrect = [set() for i in range(5)]

    def check_word(self, word: str) -> bool:
        counter = Counter(word)
        # Checking if any letters we know appear in the word aren't present in
        # the guess word
        for c in self.used_letters:
            if counter[c] < 1:
                return False
        # Checking if any letters exceed the max occurance limit for that
        # letter
        for c in self.unused_letters:
            if counter[c] > self.unused_letters[c]:
                return False
        for i in range(5):
            if self.correct[i] and self.correct[i] != word[i]:
                return False
            if word[i] in self.incorrect[i]:
                return False
        return True

    def add_guess_feedback(self, guess: str, feedback: Feedback):
        # Min number of times we know a letter shows up in the answer word
        # based solely on this guess
        min_letter_freq = Counter()
        # Letters marked as unused in the feedback
        marked_unused = set()
        for i, g in enumerate(guess):
            if feedback[i] == "c":
                self.correct[i] = g
                self.used_letters.add(g)
                min_letter_freq[g] += 1
            elif feedback[i] == "u":
                marked_unused.add(g)
                self.incorrect[i].add(g)
            elif feedback[i] == "w":
                self.incorrect[i].add(g)
                self.used_letters.add(g)
                min_letter_freq[g] += 1
        """
        A character can show up multiple times in the same guess word and
        receive different results for each occurance of the word. If
        a character is marked as unused while in the guess word, then
        the amount of times it shows up in the actual answer is equal to
        the amount of times it is marked as correct or wrong_spot while in
        the guess word
        """
        for c in marked_unused:
            self.unused_letters[c] = min_letter_freq[c]

    def update_candidate_words(self) -> int:
        candidate_words = []
        for word in self.candidates:
            if self.check_word(word):
                candidate_words.append(word)
        self.candidates = candidate_words
        return len(self.candidates)


def feedback_frequency(guess_word, answer_words: List[str]) -> Dict[str, int]:
    freq = Counter()
    for answer in answer_words:
        freq[get_feedback(guess_word, answer)] += 1
    return freq


def choose_guess_word(guess_words: List[str],
                      constraints: ConstraintSpace) -> str:
    if len(constraints.candidates) == 1:
        return constraints.candidates[0]

    min_score = float('inf')
    min_word = None
    i = 0
    for g in guess_words:
        score = score_guess_word(g, constraints)
        i += 1
        if score < min_score:
            min_score = score
            min_word = g
            log.debug(f"Word: {g}, score: {score}")
    return min_word


def score_guess_word(word: str, constraints: ConstraintSpace):
    candidates_size = len(constraints.candidates)
    score = 0
    feedback_frequencies = feedback_frequency(word, constraints.candidates)
    for feedback in feedback_frequencies:
        fb_propability = feedback_frequencies[feedback]/candidates_size
        c = deepcopy(constraints)
        c.add_guess_feedback(word, feedback)
        remaining_count = c.update_candidate_words()
        score += remaining_count*fb_propability
    return score


def play(guess_words=all_words):
    constraints = ConstraintSpace(answers)
    first_guess = True
    while True:
        if not first_guess:
            skip_calc = input("Skip calc?: ")
        else:
            skip_calc = "y"
            first_guess = False
        if skip_calc != "y":
            reccomendation = choose_guess_word(guess_words, constraints)
            print(f'Recommended word: {reccomendation}')
        print(f"Total candidates: {len(constraints.candidates)}")
        guess = input("Enter guess (or exit to exit the program): ")
        if guess == "exit":
            break
        guess_results = input("Enter guess results: ")
        constraints.add_guess_feedback(guess, Feedback(values=guess_results))
        constraints.update_candidate_words()


if __name__ == "__main__":
    play(guess_words=answers)
