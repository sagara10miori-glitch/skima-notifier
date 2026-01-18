# SKIMA Notifier
SKIMA の新着出品を自動で監視し、Discord に通知するシステムです。
優先ユーザー通知、深夜帯の静音化、ピン固定、SQLite による高速・安全な既読管理など、
プロダクション品質の監視機能を備えています。

---

## 🚀 主な機能

### 🔥 優先通知（Priority Users）
- priority_users.json に登録されたユーザーの出品を 最優先で通知
- 通知は 金色の embed で強調
- 通知メッセージは 自動でピン固定
- 既存のピンは自動解除
- 優先通知には @everyone を付与

### 🌙 深夜帯の静音化（1:00〜5:59）
- 深夜帯は **優先ユーザーのみ通知**
- 通常ユーザーの通知は翌朝まで抑制
- 無駄な API 呼び出しを減らし高速化

### 📝 通常通知
- 通常ユーザーの出品は昼間のみ通知
- 出品の「優先度（🔥特選 / ✨おすすめ / 通常）」に応じてタイトルを自動変更
- 通常通知には @everyone を付けない

### 🗂 SQLite による既読管理
- 既読管理を JSON から SQLite（seen.db）に移行
- 書き込み中の破損が起きない
- 高速・安全・堅牢
- 1週間より古い ID は自動削除

### 🔁 通知の再送処理
- Discord Webhook / Bot が一時的に落ちていても自動リトライ
- 429（レート制限）や 500 系エラーに強い

### ⚙ GitHub Actions 自動化
- 5分ごとに自動実行
- concurrency により 同時実行を完全禁止
- seen.db / last_pin.json を自動コミット
- キャッシュにより高速実行
- 安定した通知運用が可能

---

## 📁 ディレクトリ構成

<details><summary>クリックして展開</summary>
skima-notifier/
├── main.py
├── fetch.py
├── embed.py
├── notify.py
├── score.py
├── utils.py
├── seen_manager.py
├── requirements.txt
│
├── config/
│   └── settings.py
│
├── users/
│   ├── priority_users.json
│   └── exclude_users.json
│
└── .github/
    └── workflows/
        └── check.yml
</details>
