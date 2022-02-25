# wordle
Quick wordle bot in Python. Manual entry of feedback still required. Currently averaging 3.89 guesses across all possible answers.

# How to Use
You can try the bot yourself with:
```
python search.py
```
Initially you'll be prompted to enter your first guess word and the feedback you got as a result of entering it.
Guess feedback is expected as a 5 letter string of 'u', 'w', and 'c' characters.
'u' represents feedback that a letter is unused (grey), 'w' represents feedback that the letter is in the wrong spot (yellow), and 'c' means the letter is in the correct spot (green).

For example, if the answer word is 'bloke' and you guess the word 'glean', you'd enter that you got the feedback 'ucwuu'.

On future guesses, you'll first be prompted if you want to skip bot calculation. If you answer anything other than 'y', the bot will calculate the best guess word based on the constraints it knows about.

If you're using the bot please don't try to pass the results off as your own :smiley:.

# Future wishlist
I really enjoyed working on this project but unfortunately I didn't have enough time to do fully do it justice. I'm hoping to one day have enough time to add these things:
- Increase the search depth to look multiple guesses ahead. Currently the bot recommends whatever word reduces the list of candidate words the most on average (across all possible answer words) with no consideration for if the followup guess will be good.
- Improve speed by changing constraint representation to numpy arrays rather than a Python class storing multiple lists/dicts.
- Add in option to precompute recommended guesses

# Re-running Benchmark
In order to get a better sense of the bot's performance, I created a benchmark script to test the bot against all possible answers. If you're curious, you can run it with:
```
python benchmark.py
```
