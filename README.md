# 18きっぷ 到着時刻マップ

(https://maps.chizutodesign.com/18kippu/)
## 機能

- 東京駅 / 大阪駅始発・平日ダイヤでの各駅到着時刻を等時線マップで表示
- 駅タップで始発駅からの経路と時刻表を表示
- ピンチ / ホイールで拡大・縮小、ドラッグで移動
- 複数経路がある駅はタブで切り替え
- スマホ対応（下部パネル）
- 東京編・大阪編を相互リンク

- 追加したい機能
- 土日祝ダイヤへの対応
- 羅針盤のように回せる機能
- 記入した駅での検索機能
- 
## 使い方

### 方法1: ブラウザで直接開く

`東京.html` または `大阪.html` をダブルクリックしてブラウザで開きます。

### 方法2: ローカルサーバー（推奨）F

```powershell
cd "c:\Users\g17h2\OneDrive\デスクトップ\2026製作"
python -m http.server 8000
```

http://localhost:8000/index.html

## ファイル構成

```
2026製作/
├── 東京.html              # 東京始発版（メインアプリ）
├── 大阪.html              # 大阪始発版（メインアプリ）
├── reference_tokyo.html   # 公式サイト取得元（東京）
├── reference_osaka.html   # 公式サイト取得元（大阪）
├── build.py               # 東京.html / 大阪.html 生成スクリプト
├── extract_data.py        # 公式サイトから reference_*.html を取得
├── data/
│   ├── 東京/
│   │   ├── timetable.json
│   │   └── map.svg
│   └── 大阪/
│       ├── timetable.json
│       └── map.svg
└── README.md
```

## データの更新

```powershell
# 公式サイトから最新HTMLを取得
python extract_data.py

# 東京.html / 大阪.html を再生成
python build.py
```

- **時刻表データ**: `data/東京/timetable.json` または `data/大阪/timetable.json` を編集
- **路線図**: `data/東京/map.svg` または `data/大阪/map.svg` を編集


- オリジナル（東京）: [18きっぷ 到着時刻マップ 2026](https://maps.chizutodesign.com/18kippu/)
- オリジナル（大阪）: [18きっぷ 到着時刻マップ 大阪編](https://maps.chizutodesign.com/18kippu/osaka/)

## 注意

