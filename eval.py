from card import Card
from deck import Deck
from evaluator import Evaluator




board=[

]

hand= [
    Card.new('Qs'),
    Card.new('Th')
]

Card.print_pretty_cards(board+hand)

evaluator=Evaluator()

print evaluator.evaluate(hand, board)
