from words import import_5lwords
from typing import Counter, List
from enum import Enum, auto
from collections import Counter

ALL_WORDS = import_5lwords()

class GuessResult(Enum):
    CORRECT = auto()
    WRONG_SPOT = auto()
    UNUSED = auto()

def generate_result_list(guess: str, answer: str) -> List[GuessResult]:
    counter = Counter()
    for c in answer:
        counter[c] += 1
    result = []
    for g,a in zip(guess,answer):
        if g == a and counter[g]:
            result.append(GuessResult.CORRECT)
            counter[g] -= 1
        elif counter[g]:
            result.append(GuessResult.WRONG_SPOT)
            counter[g] -=1
        else:
            result.append(GuessResult.UNUSED)

def parse_results(result_str: str) -> List[GuessResult]:
    r = []
    for c in result_str:
        if c == "c":
            r.append(GuessResult.CORRECT)
        elif c == "w":
            r.append(GuessResult.WRONG_SPOT)
        elif c == "u":
            r.append(GuessResult.UNUSED)
    return r

class SearchSpace:
    def __init__(self) -> None:
        # Letters we know aren't in the word more than a certain amount of times ex. 'c': 0 means c isn't in the word at all, 'd':1 means d is in the word
        # at most 1 times
        self.unused_letters = {}
        # Letters we know are in the word
        self.used_letters = set()
        # Individual letter spaces that hold more specific info
        self.letters = [LetterSpace() for i in range(5)]
        # History
        self.candidates = ALL_WORDS
        self.ordered_candidates

    def check_word(self, word: str) -> bool:
        word_letters = set(word)
        # Checking if any letters we know appear in the word aren't present in the guess word
        if self.used_letters-word_letters:
            return False
        for c in self.unused_letters:
            if word.count(c) > self.unused_letters[c]:
                return False
        for i in range(5):
            if not self.letters[i].check_letter(word[i]):
                return False
        return True

    def add_guess_results(self, guess: str, results: List[GuessResult]):
        letter_freq = Counter()
        unused_letters = set()
        for i, r in enumerate(results):
            if r == GuessResult.CORRECT:
                self.letters[i].value = guess[i]
                self.used_letters.add(guess[i])
                letter_freq[guess[i]] += 1
            elif r == GuessResult.UNUSED:
                unused_letters.add(guess[i])
            elif r == GuessResult.WRONG_SPOT:
                self.letters[i].wrong_spot.add(guess[i])
                self.used_letters.add(guess[i])
                letter_freq[guess[i]] += 1
        for c in unused_letters:
            self.unused_letters[c] = letter_freq[c]

    def update_candidate_words(self) -> int:
        candidate_words = []
        for word in self.candidates:
            if self.check_word(word):
                candidate_words.append(word)
        self.candidates = candidate_words
        del self._ordered_candidates
        return len(self.candidates)

    @property
    def ordered_candidates(self):
        try:
            return self._ordered_candidates
        except AttributeError:
            # List of dicts, where each dict counts the amount of times each letter shows up in a space across all candidate words
            # Ex. if self.candidates = [apple, aphid, panda], freq_counters = [{'a':2, 'p':1}, {'p':2, 'a':1}, {'p':1, 'h':1, 'n':1}, {'l':1, 'i':1, 'd':1}, {'e': 1, 'd':1, 'a': 1}] 
            freq_counters: List[dict] = [Counter() for i in range(5)]
            for word in self.candidates:
                for i, c in enumerate(word):
                    freq_counters[i][c] += 1
            scores = {w: self.score_candidate(w, freq_counters, len(self.candidates)) for w in self.candidates}
            self._ordered_candidates = sorted(self.candidates, key=lambda w: self.score_candidate(w, freq_counters, len(self.candidates)))
            return self.ordered_candidates

    def score_candidate(self, candidate, freq_counters, total_candidates):
        """
        Scores a candidate guess based on its ability to narrow down search field
        """
        total_score = 0
        for i, c in enumerate(candidate):
            frequency = freq_counters[i][c]
            proportion = frequency/total_candidates
            letter_score = 1-(2*abs(0.5-proportion))
            total_score += letter_score
        return total_score

class LetterSpace:
    def __init__(self) -> None:
        self.value = None
        self.wrong_spot = set()

    def check_letter(self, letter):
        if self.value:
            if letter != self.value:
                return False
            else:
                return True
        elif letter in self.wrong_spot:
            return False
        return True

def play():
    player_input = None
    space = SearchSpace()
    guess_word = None
    while True:
        print(f"Suggested words:")
        for word in space.ordered_candidates:
            print(f"\t{word}")
        print(f"Total candidates: {len(space.candidates)}")
        guess = input("Enter guess: ")
        guess_results = input("Enter guess results: ")
        if guess == "exit" or guess_results == "exit":
            break
        space.add_guess_results(guess, parse_results(guess_results))
        count = space.update_candidate_words()
    
if __name__ == "__main__":
    play()