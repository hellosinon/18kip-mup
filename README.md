# 18きっぷ 到着時刻マップ

## 機能

- 東京駅 / 大阪駅始発・平日ダイヤでの各駅到着時刻を等時線マップで表示
- 福岡編は博多駅始発の到達駅マップ（時刻は未記入、経路は表示可能）
- 駅タップで始発駅からの経路と時刻表を表示
- ピンチ / ホイールで拡大・縮小、ドラッグで移動
- 複数経路がある駅はタブで切り替え
- スマホ対応（下部パネル）
- トップページと各マップ左上から東京編・大阪編・福岡編を切り替え

- 追加したい機能
- 土日祝ダイヤへの対応
- 羅針盤のように回せる機能
- 記入した駅での検索機能
- 
## 使い方

### 方法1: ブラウザで直接開く

`index.html` を開いて東京編・大阪編・福岡編を選びます。直接 `tokyo.html` / `osaka.html` / `hukuoka.html` を開くこともできます。

### 方法2: ローカルサーバー（推奨）F

```powershell
cd "c:\Users\g17h2\OneDrive\デスクトップ\2026製作"
python -m http.server 8000
```

http://localhost:8000/index.html

## ファイル構成

```
2026製作/
├── index.html             # 東京 / 大阪 / 福岡の選択画面
├── tokyo.html             # 東京始発版
├── osaka.html             # 大阪始発版
├── hukuoka.html           # 福岡（博多）始発版
├── reference_tokyo.html   # 公式サイト取得元（東京）
├── reference_osaka.html   # 公式サイト取得元（大阪）
├── build.py               # 東京 / 大阪 / 福岡の生成
├── build_hukuoka.py       # 福岡編の地図生成（build.py から呼ばれる）
├── extract_data.py        # 公式サイトから reference_*.html を取得
├── data/
│   ├── 東京/
│   │   ├── timetable.json
│   │   └── map.svg
│   ├── 大阪/
│   │   ├── timetable.json
│   │   └── map.svg
│   └── 福岡/
│       ├── timetable.json      # 博多始発の駅・経路（時刻は未記入）
│       └── map.svg
└── README.md
```

## データの更新

```powershell
# 公式サイトから最新HTMLを取得して再生成
python build.py --fetch

# 手元の HTML / データから東京・大阪・福岡を再生成
python build.py

# 福岡編だけ再生成
python build.py hukuoka
```

- **時刻表データ**: `data/東京/timetable.json` または `data/大阪/timetable.json` を編集
- **路線図**: `data/東京/map.svg` または `data/大阪/map.svg` を編集



## 注意

変更した内容をgithub通さずにVSで完結させるコマンド

git add .
git commit -m "変更内容"
git push

で変更できる