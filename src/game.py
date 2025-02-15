import pyxel
from enum import Enum
from player import Player, AIPlayer, PlayerType
from card import Card, CardType
import random
from typing import List

class GameMode(Enum):
    PVP = 0  # Player vs Player
    PVE = 1  # Player vs AI

class GameState(Enum):
    TITLE = 0
    MODE_SELECT = 1
    PLAYING = 2
    RESULT = 3

class Game:
    def __init__(self, width: int, height: int):
        pyxel.init(width, height, title="E CARD GAME")
        self.width = width
        self.height = height
        # カードサイズを定数として定義
        self.CARD_WIDTH = 28
        self.CARD_HEIGHT = 38
        self.CARD_SPACING = 4
        
        self.game_state = GameState.TITLE
        self.game_mode = None
        self.player = None
        self.ai_player = None
        self.selected_card_index = 0
        self.player_card = None
        self.ai_card = None
        self.round = 1  # ラウンド数を追加
        self.played_cards_history = []  # 場に出たカードの履歴
        self.rounds_to_win = 3  # 3ラウンド先取で勝利
        self.current_round_winner = None
        self.total_battles = 6  # 全6戦
        self.current_battle = 1  # 現在の戦数
        self.player_is_emperor = True  # プレイヤーが皇帝側かどうか
        self.show_result_popup = False
        self.battle_result = None  # "win" or "lose"
        self.selected_mode = 0  # 選択中のモード（0: PVP, 1: PVE）を追加
        self.init_sound()
        
    def init_game(self):
        # 音楽とサウンドの初期化
        self.init_sound()
        # その他の初期化処理
        
    def init_sound(self):
        # タイトル画面のBGM (sound 0)
        pyxel.sounds[0].set(
            "e2e3e2e3 g2g3g2g3",  # notes
            "s",                   # tone
            "4444 4444",          # volume
            "n",                   # effect
            20                     # speed
        )
        
        # ゲーム中のざわざわBGM (sound 1)
        pyxel.sounds[1].set(
            "c2c#2d2d#2 e2f2f#2g2",  # 半音階で不安感を演出
            "n",                      # ノイズ音
            "4",                      # volume
            "s",                      # サステイン効果
            30                        # speed
        )
        
        # カード選択音 (sound 2)
        pyxel.sounds[2].set(
            "c3",                     # notes
            "p",                      # パルス波
            "7",                      # volume
            "n",                      # effect
            15                        # speed
        )
        
        # 勝利ファンファーレ (sound 3)
        pyxel.sounds[3].set(
            "c3e3g3c4",              # メジャーコード
            "s",                      # サイン波
            "6",                      # volume
            "n",                      # effect
            10                        # speed
        )
        
        # 敗北音 (sound 4)
        pyxel.sounds[4].set(
            "f3d3b2g2",              # 下降音
            "n",                      # ノイズ
            "6",                      # volume
            "f",                      # フェード効果
            15                        # speed
        )
        
    def run(self):
        pyxel.run(self.update, self.draw)
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        if self.game_state == GameState.TITLE:
            self.update_title()
        elif self.game_state == GameState.MODE_SELECT:
            self.update_mode_select()
        elif self.game_state == GameState.PLAYING:
            self.update_game()
        elif self.game_state == GameState.RESULT:
            self.update_result()
            
    def draw(self):
        pyxel.cls(0)
        
        if self.game_state == GameState.TITLE:
            self.draw_title()
        elif self.game_state == GameState.MODE_SELECT:
            self.draw_mode_select()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
        elif self.game_state == GameState.RESULT:
            self.draw_result()
            
    def update_title(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.game_state = GameState.MODE_SELECT
            pyxel.playm(0, loop=True)  # タイトルBGM開始
            
    def draw_title(self):
        # タイトルテキストと開始案内
        title_text = "E CARD GAME"
        start_text = "PRESS SPACE TO START"
        
        # 1文字4ピクセルとして幅を計算
        title_width = len(title_text) * 4
        start_width = len(start_text) * 4
        
        # 両方のテキストを中央揃えで配置
        title_x = (self.width - title_width) // 2
        start_x = (self.width - start_width) // 2
        
        # タイトルを描画（開始案内の上に配置）
        pyxel.text(title_x, self.height // 2 - 10, title_text, 7)
        # 開始案内を描画
        pyxel.text(start_x, self.height // 2 + 10, start_text, 7)

    def init_cards(self, is_emperor: bool) -> List[Card]:
        """陣営に応じたカードを初期化"""
        cards = []
        if is_emperor:
            cards.append(Card(CardType.EMPEROR))  # 皇帝1枚
            cards.extend([Card(CardType.CITIZEN) for _ in range(4)])  # 市民4枚
        else:
            cards.append(Card(CardType.SLAVE))  # 奴隷1枚
            cards.extend([Card(CardType.CITIZEN) for _ in range(4)])  # 市民4枚
        random.shuffle(cards)
        return cards

    def start_game(self, mode: GameMode):
        self.game_mode = mode
        self.game_state = GameState.PLAYING
        self.selected_card_index = 0
        self.player_card = None
        self.ai_card = None
        self.round = 1
        
        # プレイヤーの初期化（最初は皇帝側）
        self.player = Player("Player 1", PlayerType.HUMAN)
        self.player.hand = self.init_cards(self.player_is_emperor)
        
        # AIプレイヤーの初期化（最初は奴隷側）
        self.ai_player = AIPlayer("CPU")
        self.ai_player.hand = self.init_cards(not self.player_is_emperor)
        
        # スコアの初期化
        self.player.score = 0
        self.ai_player.score = 0
        
        pyxel.playm(1, loop=True)  # ゲーム中BGM開始
        
    def play_card(self, card_index: int):
        if not self.player or not self.ai_player:
            return
            
        if card_index >= len(self.player.hand):
            return
            
        # プレイヤーのカードプレイ
        self.player_card = self.player.select_card(card_index)
        self.ai_card = self.ai_player.select_card_ai()
        
        if self.player_card and self.ai_card:
            # 履歴に追加
            self.played_cards_history.append((self.player_card, self.ai_card))
            
            # 勝敗判定
            result = self.judge_cards(self.player_card, self.ai_card)
            if result in ["win", "lose"]:
                self.battle_result = result
                self.show_result_popup = True
                if result == "win":
                    self.player.score += 1
                    self.current_round_winner = "Player"
                    pyxel.play(3, 3)
                else:
                    self.ai_player.score += 1
                    self.current_round_winner = "CPU"
                    pyxel.play(3, 4)
            else:  # 引き分けの場合
                self.round += 1

    def judge_cards(self, card1: Card, card2: Card) -> str:
        """カードの勝敗判定"""
        if card1.card_type == card2.card_type:
            return "draw"
        
        if card1.card_type == CardType.EMPEROR:
            return "win" if card2.card_type == CardType.CITIZEN else "lose"
        elif card1.card_type == CardType.CITIZEN:
            return "win" if card2.card_type == CardType.SLAVE else "lose"
        else:  # SLAVE
            return "win" if card2.card_type == CardType.EMPEROR else "lose"

    def is_emperor_vs_slave(self) -> bool:
        """皇帝vs奴隷の判定"""
        return ((self.player_card.card_type == CardType.EMPEROR and 
                self.ai_card.card_type == CardType.SLAVE) or
               (self.player_card.card_type == CardType.SLAVE and 
                self.ai_card.card_type == CardType.EMPEROR))

    def next_battle(self):
        """次の戦へ移行"""
        # 場のカードをリセット
        self.player_card = None
        self.ai_card = None
        
        self.current_battle += 1
        if self.current_battle > self.total_battles:
            self.game_state = GameState.RESULT
        else:
            # 陣営を交代
            self.player_is_emperor = not self.player_is_emperor
            # 新しい手札を配布
            self.player.hand = self.init_cards(self.player_is_emperor)
            self.ai_player.hand = self.init_cards(not self.player_is_emperor)
            self.round = 1

    def update_game(self):
        if self.show_result_popup:
            if pyxel.btnp(pyxel.KEY_SPACE):  # Spaceキーで次のバトルへ
                self.show_result_popup = False
                self.next_battle()
        else:
            if not self.player or not self.ai_player:
                return
                
            if self.player.player_type == PlayerType.HUMAN:
                # カード選択の処理
                if pyxel.btnp(pyxel.KEY_LEFT):
                    self.selected_card_index = (self.selected_card_index - 1) % max(1, len(self.player.hand))
                elif pyxel.btnp(pyxel.KEY_RIGHT):
                    self.selected_card_index = (self.selected_card_index + 1) % max(1, len(self.player.hand))
                elif pyxel.btnp(pyxel.KEY_SPACE):
                    if len(self.player.hand) > 0:
                        self.play_card(self.selected_card_index)
                    
    def draw_game(self):
        # 背景
        pyxel.rect(0, 0, self.width, self.height, 1)
        
        # CPUの情報を左上に表示
        self.draw_player_info(self.ai_player, 10, 5)  # 左上
        
        # プレイヤーの情報を右側、手札の上に表示
        player_info_y = self.height - self.CARD_HEIGHT - 60
        self.draw_player_info(self.player, self.width - 50, player_info_y)
        
        # バトル数とラウンド数の表示
        battle_text = f"Battle {self.current_battle}/6"
        round_text = f"Turn {self.round}"  # "Round" を "Turn" に変更
        
        pyxel.text(self.width // 2 - 30, 5, battle_text, 7)
        pyxel.text(self.width // 2 - 20, 15, round_text, 7)
        
        # CPU側の手札（裏面）表示
        self.draw_cpu_hand()
        
        # プレイされたカードの表示
        self.draw_played_cards()
        
        # 現在のプレイヤーの手札表示
        self.draw_hand(self.player, self.selected_card_index)
        
        # 操作ガイド表示
        self.draw_controls()

        # 決着時のポップアップを表示
        if self.show_result_popup:
            self.draw_result_popup()

    def draw_cpu_hand(self):
        if not self.ai_player or not self.ai_player.hand:
            return
            
        card_width = 28
        card_height = 38
        spacing = 4
        
        total_width = (card_width + spacing) * len(self.ai_player.hand)
        start_x = (self.width - total_width) // 2
        
        for i in range(len(self.ai_player.hand)):
            x = start_x + i * (card_width + spacing)
            y = 30  # 上部に配置
            
            # 裏面のカードを描画
            self.draw_card_back(x, y, card_width, card_height)

    def draw_card_back(self, x: int, y: int, width: int, height: int):
        # カードの裏面デザイン
        pyxel.rect(x, y, width, height, 13)  # 背景色
        pyxel.rectb(x, y, width, height, 7)  # 枠線
        
        # 裏面のパターン（シンプルな格子模様）
        for i in range(2, width - 2, 4):
            for j in range(2, height - 2, 4):
                pyxel.rect(x + i, y + j, 2, 2, 6)

    def draw_player_info(self, player: Player, x: int, y: int):
        name_color = 10 if player == self.player else 7
        pyxel.text(x, y, f"{player.name}", name_color)
        pyxel.text(x, y + 8, f"Score: {player.score}", 7)
        pyxel.text(x, y + 16, f"Cards: {player.get_hand_size()}", 7)
        
    def draw_played_cards(self):
        if not self.player_card and not self.ai_card:
            return
            
        # カードサイズを定数として定義
        card_width = 25
        card_height = 35
        
        # プレイヤーのカード表示位置
        if self.player_card:
            x = self.width // 2 - card_width // 2
            y = self.height // 2 + 20
            self.draw_card(self.player_card, x, y, card_width, card_height)
            
        # AIのカード表示位置
        if self.ai_card:
            x = self.width // 2 - card_width // 2
            y = self.height // 2 - 50
            self.draw_card(self.ai_card, x, y, card_width, card_height)

    def draw_card(self, card: Card, x: int, y: int, width: int, height: int):
        # カードの色を種類によって変更
        bg_color = 5  # デフォルト（市民）は灰色
        if card.card_type == CardType.EMPEROR:
            bg_color = 9  # 皇帝は青
        elif card.card_type == CardType.SLAVE:
            bg_color = 8  # 奴隷は赤

        # カードの背景
        pyxel.rect(x, y, width, height, bg_color)
        # カードの枠
        pyxel.rectb(x, y, width, height, 7)
        
        # カードの種類のテキスト（短縮版の英語表記）
        card_type = "EMP" if card.card_type == CardType.EMPEROR else "CIT" if card.card_type == CardType.CITIZEN else "SLV"
        
        # テキストの中央配置の計算
        text_width = len(card_type) * 4  # 英語フォントは1文字4ピクセル
        text_x = x + (width - text_width) // 2
        text_y = y + (height - 5) // 2  # フォントの高さを考慮して調整
        
        # テキストを描画
        pyxel.text(text_x, text_y, card_type, 0)
        
        # カードの種類を示すアイコンや記号を追加（オプション）
        icon_y = y + 5  # 上部に配置
        if card.card_type == CardType.EMPEROR:
            pyxel.text(x + 5, icon_y, "E", 0)  # 左上
            pyxel.text(x + width - 9, y + height - 10, "E", 0)  # 右下
        elif card.card_type == CardType.CITIZEN:
            pyxel.text(x + 5, icon_y, "C", 0)  # 左上
            pyxel.text(x + width - 9, y + height - 10, "C", 0)  # 右下
        else:  # SLAVE
            pyxel.text(x + 5, icon_y, "S", 0)  # 左上
            pyxel.text(x + width - 9, y + height - 10, "S", 0)  # 右下

    def draw_controls(self):
        # コントロール説明のテキスト（英語表記）
        arrow_text = "ARROWS: SELECT"
        space_text = "SPACE: DECIDE"
        
        # 各テキストの幅を計算（英語は1文字4ピクセル）
        arrow_width = len(arrow_text) * 4
        space_width = len(space_text) * 4
        total_width = arrow_width + 20 + space_width  # 20は間隔
        
        # 開始位置を計算（画面中央から左右に配置）
        start_x = (self.width - total_width) // 2
        text_y = self.height - 10
        
        # 左側のコントロール説明
        pyxel.text(start_x, text_y, arrow_text, 7)
        # 右側のコントロール説明
        pyxel.text(start_x + arrow_width + 20, text_y, space_text, 7)

    def update_result(self):
        if pyxel.btnp(pyxel.KEY_SPACE):  # Enterキーの代わりにSpaceキーに変更
            self.game_state = GameState.TITLE
            pyxel.stop()  # すべての音を停止
            
    def draw_result(self):
        # 半透明の黒い背景（ディザリングパターン）
        for y in range(self.height):
            for x in range(self.width):
                if (x + y) % 2 == 0:
                    pyxel.pset(x, y, 0)

        # ポップアップウィンドウ
        window_width = 160
        window_height = 100
        x = (self.width - window_width) // 2
        y = (self.height - window_height) // 2
        
        # ウィンドウの背景と枠
        pyxel.rect(x, y, window_width, window_height, 5)  # 背景
        pyxel.rectb(x, y, window_width, window_height, 7)  # 枠線
        
        # 最終結果の判定
        final_result = "WIN" if self.player.score > self.ai_player.score else "LOSE" if self.player.score < self.ai_player.score else "DRAW"
        title_bg_color = 11 if final_result == "WIN" else 8 if final_result == "LOSE" else 6  # DRAW は緑色
        
        # タイトル部分の背景
        pyxel.rect(x + 2, y + 2, window_width - 4, 16, title_bg_color)
        
        # GAME OVER テキスト
        game_over_text = "GAME OVER"
        text_x = x + (window_width - len(game_over_text) * 4) // 2
        pyxel.text(text_x, y + 6, game_over_text, 7)
        
        # 勝敗テキスト
        result_text = f"YOU {final_result}!"
        text_x = x + (window_width - len(result_text) * 4) // 2
        pyxel.text(text_x, y + 25, result_text, title_bg_color)
        
        # スコア表示
        pyxel.text(x + 20, y + 45, "【 Final Score 】", 7)
        
        # プレイヤーのスコア
        player_score_color = 11 if self.player.score > self.ai_player.score else 7
        pyxel.text(x + 20, y + 60, "YOU:", 7)
        pyxel.text(x + 50, y + 60, f"{self.player.score}", player_score_color)
        
        # CPUのスコア
        cpu_score_color = 11 if self.ai_player.score > self.player.score else 7
        pyxel.text(x + 20, y + 70, "CPU:", 7)
        pyxel.text(x + 50, y + 70, f"{self.ai_player.score}", cpu_score_color)
        
        # 続行方法の案内
        pyxel.text(x + 20, y + 85, "Press SPACE to title screen", 7)

    def update_mode_select(self):
        # 上下キーでモード選択
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_mode = (self.selected_mode - 1) % 2
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_mode = (self.selected_mode + 1) % 2
            
        # Spaceキーで決定
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.selected_mode == 0:
                # PVPモードは現在無効
                pass
            else:
                self.start_game(GameMode.PVE)
            
    def draw_mode_select(self):
        pyxel.text(self.width // 2 - 40, self.height // 2 - 20, "Select Game Mode:", 7)
        
        # PvPモードのテキストと取り消し線
        text_y = self.height // 2
        text_x = self.width // 2 - 40
        text = "Player vs Player"
        text_width = len(text) * 4  # 英語フォントは1文字4ピクセル
        
        # 選択中のモードは明るい色で表示
        text_color = 7 if self.selected_mode == 0 else 5
        pyxel.text(text_x, text_y, text, text_color)
        pyxel.line(text_x, text_y + 3, text_x + text_width, text_y + 3, 5)  # 取り消し線
        
        # PvEモードのテキスト
        text_y = self.height // 2 + 20
        text = "Player vs CPU"
        text_color = 7 if self.selected_mode == 1 else 5
        pyxel.text(text_x, text_y, text, text_color)
        
        # 選択中のモードを示すカーソル
        cursor_x = text_x - 10
        cursor_y = self.height // 2 + (20 * self.selected_mode)
        pyxel.text(cursor_x, cursor_y, ">", 7)

    def draw_hand(self, player: Player, selected_index: int):
        if not player or not player.hand:
            return
            
        # 手札の合計幅を計算
        total_width = (self.CARD_WIDTH + self.CARD_SPACING) * len(player.hand)
        start_x = (self.width - total_width) // 2

        for i, card in enumerate(player.hand):
            x = start_x + i * (self.CARD_WIDTH + self.CARD_SPACING)
            y = self.height - self.CARD_HEIGHT - 20
            
            # 選択中のカードは少し上に表示
            if i == selected_index:
                y -= 5
                
            self.draw_card(card, x, y, self.CARD_WIDTH, self.CARD_HEIGHT)

    def draw_text(self, x: int, y: int, text: str, col: int):
        pyxel.text(x, y, text, col)

    def draw_cards_history(self):
        if not self.played_cards_history:
            return
            
        card_width = 20  # 履歴用の小さいカードサイズ
        card_height = 28
        spacing = 5
        
        # 右端に履歴を表示
        for i, (p_card, a_card) in enumerate(self.played_cards_history):
            # CPU側のカード
            self.draw_card(a_card, self.width - card_width - 5, 
                         50 + i * (card_height + spacing), 
                         card_width, card_height)
            # プレイヤー側のカード
            self.draw_card(p_card, self.width - card_width - 5, 
                         self.height - 50 - (i * (card_height + spacing)), 
                         card_width, card_height)

    def draw_result_popup(self):
        # 半透明の黒い背景（ディザリングパターン）
        for y in range(self.height):
            for x in range(self.width):
                if (x + y) % 2 == 0:
                    pyxel.pset(x, y, 0)

        # ポップアップウィンドウ
        window_width = 160
        window_height = 100
        x = (self.width - window_width) // 2
        y = (self.height - window_height) // 2
        
        # ウィンドウの背景と枠
        pyxel.rect(x, y, window_width, window_height, 5)  # 背景
        pyxel.rectb(x, y, window_width, window_height, 7) # 枠線
        
        # タイトル部分の背景
        title_bg_color = 11 if self.battle_result == "win" else 8
        pyxel.rect(x + 2, y + 2, window_width - 4, 16, title_bg_color)
        
        # 決着テキスト
        result_text = "BATTLE FINISHED!"
        text_x = x + (window_width - len(result_text) * 4) // 2
        pyxel.text(text_x, y + 6, result_text, 7)
        
        # 勝敗テキスト
        result_text = "YOU WIN!" if self.battle_result == "win" else "YOU LOSE..."
        text_x = x + (window_width - len(result_text) * 4) // 2
        pyxel.text(text_x, y + 25, result_text, title_bg_color)
        
        # カード対決の結果表示
        pyxel.text(x + 20, y + 45, "【 Card Battle Result 】", 7)
        
        # プレイヤーのカード情報
        player_card_color = self.get_card_color(self.player_card.card_type)
        pyxel.text(x + 20, y + 60, "YOU:", 7)
        pyxel.text(x + 50, y + 60, f"{self.player_card.card_type.name}", player_card_color)
        
        # CPUのカード情報
        cpu_card_color = self.get_card_color(self.ai_card.card_type)
        pyxel.text(x + 20, y + 70, "CPU:", 7)
        pyxel.text(x + 50, y + 70, f"{self.ai_card.card_type.name}", cpu_card_color)
        
        # 続行方法の案内
        pyxel.text(x + 30, y + 85, "Press SPACE to Next Battle", 7)

    def get_card_color(self, card_type: CardType) -> int:
        """カードの種類に応じた色を返す"""
        if card_type == CardType.EMPEROR:
            return 9  # 青
        elif card_type == CardType.CITIZEN:
            return 6  # 緑
        else:  # SLAVE
            return 8  # 赤