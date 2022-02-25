from words import answers
from search import ConstraintSpace, get_feedback, choose_guess_word


def main(start_word="salet"):
    # Tests how the bot performs against all possible answers, outputs results into 'results.csv'
    results = {}
    for i, answer in enumerate(answers):
        c = ConstraintSpace(answers)
        guess_word = start_word
        guesses = [guess_word]
        while len(c.candidates) > 1:
            feedback = get_feedback(guess_word, answer)
            c.add_guess_feedback(guess_word, feedback)
            c.update_candidate_words()
            guess_word = choose_guess_word(c.candidates, c)
            guesses.append(guess_word)
        results[answer] = (len(guesses), guesses)
        print(f"{i}, {answer}, {results[answer]}")

    with open("results.csv", 'w') as out:
        for word in results:
            guesses = results[word][1]
            guess_number = len(guesses)
            out.write(f"{word},{guess_number},{','.join(guesses)}\n")

    guess_numbers = [val[0] for val in results.values()]
    print("Mean:", sum(guess_numbers)/len(guess_numbers))


if __name__ == "__main__":
    main()
