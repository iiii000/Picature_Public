# Picature

Python / Pygameで制作した、マウスで線を描いて攻略する2Dアクションゲームです。

> **公開範囲について**：現在のゲームで使用する自作画像と、ステージエディター用のフォント（ライセンス同梱）を収録しています。

## ゲームの特徴

- **描いた線を足場にする**：マウスで描いた線から衝突判定用のマスクを生成し、プレイヤーが線に乗れるようにしています。
- **描いた軌跡に沿ったダッシュ**：プレイヤーに重なる線を描くと、その軌跡に沿って移動します。
- **線の組み合わせによる魔法**：3本の線の長さの組み合わせを判定し、特定の組み合わせで弾を生成します。
- **敵ごとの行動**：共通の敵クラスを基に、敵の種類ごとに探索・移動・攻撃などの処理を実装しています。
- **ステージ制作ツール**：ステージデータをCSVとして保存するエディターを用意しています。

## 注目してほしいコード

| 実装 | ファイル | 内容 |
| --- | --- | --- |
| 手描き入力 | [object/lines.py](object/lines.py) | マウス入力の座標変換、軌跡の保存、マスク生成、線の長さによる魔法判定 |
| プレイヤー | [object/player.py](object/player.py) | 移動・ジャンプ、線に沿ったダッシュ、アニメーション |
| 衝突判定 | [core/collision.py](core/collision.py) | 地形・手描き線・敵・ギミックとの接触判定 |
| 敵の共通処理 | [data/program/enemy/enemy_base.py](data/program/enemy/enemy_base.py) | 敵の基底クラスと共通処理 |
| 敵の行動例 | [data/program/enemy/spider.py](data/program/enemy/spider.py) | 状態に応じた行動の切り替え |
| ゲーム進行 | [core/game.py](core/game.py) / [state/](state/) | タイトル・ゲーム・イベントなどの状態遷移 |
| ステージ管理 | [object/stage.py](object/stage.py) | CSVの読み込み、オブジェクト更新、衝突処理の呼び出し |
| ステージエディター | [stage_maker.py](stage_maker.py) | マップ編集とCSV出力 |

## 操作

| 操作 | 入力 |
| --- | --- |
| タイトルの選択 / 決定 | W・S / Space |
| 左右移動 | A・D |
| ジャンプ | Space |
| 線を描く | マウス左ボタンを押しながらドラッグし、離して確定 |
| 終了 | Esc |

## 開発環境・起動方法

Python 3.11系 / Pygame 2.6.1を使用したプロジェクトです。
依存パッケージをインストールして、以下の手順で起動します。公開版での起動・プレイ確認は未実施です。

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

プロジェクトのルートで実行してください。起動時はフルスクリーンになります。
同じPython環境で`stage_maker.py`を実行するとステージエディターを起動できます。

## 開発状況

現在開発中のLINER/TRACERの前身となったプロトタイプです。

## 素材について

- ゲームの手描きイラストは本プロジェクトで制作したものです。
- `assets/font/PressStart2P-Regular.ttf`：Press Start 2P Project Authors、SIL Open Font License 1.1。著作権表示と全文は[OFL.txt](assets/font/OFL.txt)を参照してください。ステージエディターで使用しています。
