from typing import List
from card import Card, CardType
import random
from enum import Enum

class PlayerType(Enum):
    HUMAN = 0
    AI = 1

class Player:
    def __init__(self, name: str, player_type: PlayerType):
        self.name = name
        self.player_type = player_type
        self.hand: List[Card] = []
        self.score = 0
        
    def init_hand(self):
        # 手札の初期化（市民4枚、皇帝1枚、奴隷1枚）
        self.hand = [
            Card(CardType.CITIZEN) for _ in range(4)
        ]
        self.hand.append(Card(CardType.EMPEROR))
        self.hand.append(Card(CardType.SLAVE))
        
    def select_card(self, index: int) -> Card:
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None
        
    def get_hand_size(self) -> int:
        return len(self.hand)

class AIPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name, PlayerType.AI)
        self.opponent_played_cards = []
        
    def select_card_ai(self) -> Card:
        if len(self.hand) == 0:
            return None
            
        # 基本戦略の実装
        emperor_count = sum(1 for card in self.hand if card.card_type == CardType.EMPEROR)
        slave_count = sum(1 for card in self.hand if card.card_type == CardType.SLAVE)
        citizen_count = sum(1 for card in self.hand if card.card_type == CardType.CITIZEN)
        
        # 最後の1枚は選択の余地なし
        if len(self.hand) == 1:
            return self.select_card(0)
        
        # ランダム要素を導入（30%の確率で完全ランダム選択）
        if random.random() < 0.3:
            index = random.randint(0, len(self.hand) - 1)
            return self.select_card(index)
        
        # 残りの70%は状況に応じた選択
        available_indices = []
        
        # 市民カードがある場合、50%の確率で市民を使用
        if citizen_count > 0 and random.random() < 0.5:
            for i, card in enumerate(self.hand):
                if card.card_type == CardType.CITIZEN:
                    available_indices.append(i)
        
        # 皇帝/奴隷カードがある場合、それぞれ30%の確率で使用
        elif (emperor_count > 0 or slave_count > 0) and random.random() < 0.3:
            for i, card in enumerate(self.hand):
                if card.card_type in [CardType.EMPEROR, CardType.SLAVE]:
                    available_indices.append(i)
        
        # 上記の条件に当てはまらない場合や、available_indicesが空の場合
        if not available_indices:
            available_indices = list(range(len(self.hand)))
        
        # 選択可能なカードからランダムに1枚を選択
        selected_index = random.choice(available_indices)
        return self.select_card(selected_index)