from game import Game

def main():
    # ウィンドウサイズを調整（横幅を広げる）
    game = Game(240, 300)  # 元: 200, 180
    game.run()

if __name__ == "__main__":
    main()