# E Card Game

E Card Game（皇帝ゲーム）は、Pyxel を使用して作られたシンプルなカードゲームです。

![main](./doc/images/main.png "main")

## 概要

プレイヤーは CPU と対戦し、手札から 1 枚ずつカードを出し合って勝負を行います。
全 6 バトルを行い、より多くのバトルに勝利したプレイヤーが勝者となります。

### カードの種類と強さ

- 皇帝(Emperor): 市民に勝つ、奴隷に負ける
- 市民(Citizen): 奴隷に勝つ、皇帝に負ける
- 奴隷(Slave): 皇帝に勝つ、市民に負ける

## 必要要件

- Python 3.7 以上
- Pyxel 1.9.0 以上

## インストール

1. リポジトリをクローン:

   ```bash
   git clone [repository-url]
   ```

2. 必要なパッケージをインストール:

   ```bash
   pip install -r requirements.txt
   ```

   ## 実行方法

```bash
python src/main.py
```

## 操作方法

- タイトル画面: SPACE キーでゲーム開始
- ゲーム中:
  - ←→ キー: カードの選択
  - SPACE キー: カードを出す
- 結果画面: SPACE キーでタイトルに戻る

## ゲームの流れ

1. プレイヤーは最初に皇帝陣営からスタート
2. 各バトルで 5 枚のカードを使用
3. 1 バトル終了ごとに陣営が入れ替わる
4. 全 6 バトルを行い、より多くのバトルに勝利した方が勝者

## ライセンス

[MIT License](LICENSE)
