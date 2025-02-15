from enum import Enum

class CardType(Enum):
    EMPEROR = 0  # 皇帝
    CITIZEN = 1  # 市民
    SLAVE = 2    # 奴隷

class Card:
    def __init__(self, card_type: CardType):
        self.card_type = card_type
        
    def is_stronger_than(self, other_card):
        if self.card_type == CardType.EMPEROR:
            return other_card.card_type == CardType.CITIZEN
        elif self.card_type == CardType.CITIZEN:
            return other_card.card_type == CardType.SLAVE
        else:  # SLAVE
            return other_card.card_type == CardType.EMPEROR