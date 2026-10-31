"""
Fixed question set for Experiment 5 (Chain-of-Thought Reasoning and
Self-Consistency by Sampling).

Ten short arithmetic / logic word problems, each with a unique id and a
gold answer. Most are simple enough that a single correct reasoning path
is the "obvious" one; a few (q05, q07, q09) are built so that a plausible
but wrong shortcut is at least as natural as the correct multi-step
solution, which is what lets a single greedy trace go wrong while
sampling several traces and voting recovers the right answer.

Gold answers are stored as plain numbers; exp5_cot_selfconsistency.py
normalises both gold and extracted answers to the same canonical string
before comparing them.
"""

QUESTIONS = [
    {
        "id": "q01",
        "text": "A shop had 23 apples. It sold 8 in the morning and 6 in "
                "the afternoon. How many apples are left?",
        "gold": 9,
    },
    {
        "id": "q02",
        "text": "A train travels at 60 km/h for 2.5 hours. How many "
                "kilometres does it cover?",
        "gold": 150,
    },
    {
        "id": "q03",
        "text": "Ravi has 3 boxes with 12 pens each and 2 boxes with 8 "
                "pens each. How many pens does he have in total?",
        "gold": 52,
    },
    {
        "id": "q04",
        "text": "A tank is filled by a pipe at 15 litres per minute. How "
                "many litres are in the tank after 8 minutes?",
        "gold": 120,
    },
    {
        "id": "q05",
        "text": "A store marks up a product that costs 80 rupees by 25% "
                "to set the selling price, then later applies a 25% "
                "discount to the selling price during a sale. What is the "
                "final sale price?",
        "gold": 75,
    },
    {
        "id": "q06",
        "text": "There are 5 rows of chairs with 9 chairs in each row. If "
                "4 chairs are removed, how many chairs remain?",
        "gold": 41,
    },
    {
        "id": "q07",
        "text": "A worker is paid for 6 full days and one half day at a "
                "daily rate of 400 rupees. What is the total pay?",
        "gold": 2600,
    },
    {
        "id": "q08",
        "text": "A rectangular garden is 12 metres long and 7 metres wide. "
                "What is its area in square metres?",
        "gold": 84,
    },
    {
        "id": "q09",
        "text": "A bus stops at every station from station 1 to station 9 "
                "inclusive. How many gaps (stretches of road between "
                "consecutive stations) does the bus travel through?",
        "gold": 8,
    },
    {
        "id": "q10",
        "text": "A recipe needs 250 grams of flour per batch. How many "
                "grams of flour are needed for 4 batches, minus 100 grams "
                "of flour already available?",
        "gold": 900,
    },
]

QUESTIONS_BY_ID = {q["id"]: q for q in QUESTIONS}
