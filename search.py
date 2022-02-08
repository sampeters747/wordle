from statistics import mean
from words import all_words, answers
from typing import Counter, List
from enum import Enum, auto
from collections import Counter
from copy import deepcopy


class Feedback(Enum):
    CORRECT = auto()
    WRONG_SPOT = auto()
    UNUSED = auto()


def gen_feedback_list(guess: str, answer: str) -> List[Feedback]:
    counter = Counter()
    for c in answer:
        counter[c] += 1
    result = [None for i in range(5)]
    # First pass handles correctly guessed letters
    for i in range(5):
        g, a = guess[i], answer[i]
        if g == a:
            result[i] = Feedback.CORRECT
            counter[g] -= 1
    # Second pass handles letters that are unused/in the wrong spot
    for i in range(5):
        g, a = guess[i], answer[i]
        if g != a and counter[g]:
            result[i] = Feedback.WRONG_SPOT
            counter[g] -= 1
        elif g != a:
            result[i] = Feedback.UNUSED
    return result

def parse_feedback(feedback_str: str) -> List[Feedback]:
    r = []
    for c in feedback_str:
        if c == "c":
            r.append(Feedback.CORRECT)
        elif c == "w":
            r.append(Feedback.WRONG_SPOT)
        elif c == "u":
            r.append(Feedback.UNUSED)
    return r


class ConstraintSpace:
    def __init__(self, candidates) -> None:
        self.candidates = candidates
        # self.ordered_candidates
        """
        Letters we know aren't in the word more than a certain amount of times ex. 
        0 means c isn't in the word at all, 'd':1 means d is in the word
        at most 1 times
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
        # Checking if any letters we know appear in the word aren't present in the guess word
        for c in self.used_letters:
            if counter[c] < 1:
                return False
        # Checking if any letters exceed the max occurance limit for that letter
        for c in self.unused_letters:
            if counter[c] > self.unused_letters[c]:
                return False
        for i in range(5):
            if self.correct[i] and self.correct[i] != word[i]:
                return False
            if word[i] in self.incorrect[i]:
                return False
        return True

    def add_guess_feedback(self, guess: str, feedback: List[Feedback]):
        # Min number of times we know a letter shows up in the answer word based solely on this guess
        min_letter_freq = Counter()
        # Letters marked as unused in the feedback
        marked_unused = set()
        for i, g in enumerate(guess):
            if feedback[i] == Feedback.CORRECT:
                self.correct[i] = g
                self.used_letters.add(g)
                min_letter_freq[g] += 1
            elif feedback[i] == Feedback.UNUSED:
                marked_unused.add(g)
                self.incorrect[i].add(g)
            elif feedback[i] == Feedback.WRONG_SPOT:
                self.incorrect[i].add(g)
                self.used_letters.add(g)
                min_letter_freq[g] += 1
        """
        A character can show up multiple times in the same guess word and
        receive different results for each occurance of the word. If a character
        is marked as unused while in the guess word, then the amount of times it
        shows up in the answer is equal to the amount of times it is marked as 
        correct or wrong_spot while in the guess word 
        """
        for c in marked_unused:
            self.unused_letters[c] = min_letter_freq[c]

    def update_candidate_words(self) -> int:
        candidate_words = []
        for word in self.candidates:
            if self.check_word(word):
                candidate_words.append(word)
        self.candidates = candidate_words
        # Invalidating cache of sorted candidate words
        # del self._ordered_candidates
        return len(self.candidates)

    # @property
    # def ordered_candidates(self):
    #     try:
    #         # self._ordered_candidates caches the results of sorting
    #         # each time self.update_candidate_words() is called it invalidates the cache
    #         return self._ordered_candidates
    #     except AttributeError:
    #         # List of dicts, where each dict counts the amount of times each letter shows up in a space across all candidate words
    #         # Ex. if self.candidates = [apple, aphid, panda], freq_counters = [{'a':2, 'p':1}, {'p':2, 'a':1}, {'p':1, 'h':1, 'n':1}, {'l':1, 'i':1, 'd':1}, {'e': 1, 'd':1, 'a': 1}]
    #         freq_counters: List[dict] = [Counter() for i in range(5)]
    #         for word in self.candidates:
    #             for i, c in enumerate(word):
    #                 freq_counters[i][c] += 1
    #         scores = {w: self.score_candidate(w, freq_counters, len(
    #             self.candidates)) for w in self.candidates}
    #         self._ordered_candidates = sorted(self.candidates, key=lambda w: self.score_candidate(
    #             w, freq_counters, len(self.candidates)))
    #         return self.ordered_candidates

    # def score_candidate(self, candidate, freq_counters, total_candidates):
    #     """
    #     Scores a candidate guess based on its ability to narrow down search field
    #     """
    #     total_score = 0
    #     for i, c in enumerate(candidate):
    #         frequency = freq_counters[i][c]
    #         proportion = frequency/total_candidates
    #         letter_score = 1-(2*abs(0.5-proportion))
    #         total_score += letter_score
    #     return total_score


def choose_guess_word(guess_words: List[str], constraints: ConstraintSpace) -> str:
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
            # print(f"Word: {g}, score: {score}")
    return min_word

def score_guess_word(word: str, constraints: ConstraintSpace):
    remaining_candidates = []
    for answer in constraints.candidates:
        if word == answer:
            remaining_candidates.append(0)
            continue
        # Hypothetical guess feedback if candidate word is the answer
        guess_feedback = gen_feedback_list(word, answer)
        c = deepcopy(constraints)
        c.add_guess_feedback(word, guess_feedback)
        remaining_count = c.update_candidate_words()
        remaining_candidates.append(remaining_count)
    return mean(remaining_candidates)

def play(guess_words=all_words):
    player_input = None
    constraints = ConstraintSpace(answers)
    guess_word = None
    while True:
        skip_calc = input("Skip calc?: ")
        if skip_calc != "y":
            reccomendation = choose_guess_word(guess_words, constraints)
            print(reccomendation)
        print(f"Total candidates: {len(constraints.candidates)}")
        guess = input("Enter guess: ")
        guess_results = input("Enter guess results: ")
        if guess == "exit" or guess_results == "exit":
            break
        constraints.add_guess_feedback(guess, parse_feedback(guess_results))
        count = constraints.update_candidate_words()


if __name__ == "__main__":
    play(guess_words=answers)
