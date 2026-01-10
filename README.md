# SKIMA Notifier  
SKIMA の新着商品を自動で取得し、Discord に美しい Embed で通知するシステムです。  
通知の確実性・視認性・保守性を最大限に高めた構成になっています。

---

## 🚀 機能一覧

### 🔔 通知機能
- SKIMAの新着DL商品を自動取得し、Discord Webhookに通知
- タイトルは《 額縁スタイル 》で統一
- 価格は「9,000円」のようにカンマ区切りで表示
- URLは「🔗 skima.jp/xxxx」の短縮表示（展開防止）
- サムネイル画像付き（存在しない場合は省略）
- 価格に応じたラベル（🔥特選 / ✨おすすめ / ⭐注目）を自動付与
- ラベルごとに色分け（赤→青→緑）で視認性向上
- 通知タイトルに絵文字（📢🔔📝）＋優先度（💌）を自動付与
- 通知は最大10件ずつまとめて送信

### 👤 ユーザー管理
- `users/priority_users.txt`：優先通知ユーザー（スコアに関係なく通知）
- `users/exclude_users.txt`：通知除外ユーザー
- 通知対象 = 優先 − 除外
- 空行・重複・全角スペースは自動除去

### 🛡 安定性・堅牢性
- fetch処理は最大3回まで自動リトライ
- Discord通知は最大2回まで再送＋レート制限対応
- `seen.json` が破損しても自動修復して継続動作
- HTML構造が変化してもフェイルセーフで通知継続
- `logs/notifier.log` に詳細な実行ログを記録（※オプション）

### ⚙ GitHub Actions
- 5分ごとに自動実行（cronスケジュール）
- 通知処理は最大2回まで自動リトライ
- ランダム遅延で同時実行の衝突を回避
- pipキャッシュを活用して高速化
- Webhook URLはGitHub Secretsで安全に管理

---

## 📁 ディレクトリ構成

<details>
skima-notifier/
  ├── .github/
  │   └── workflows/
  │       └── check.yml              # GitHub Actions ワークフロー定義
  │
  ├── config/
  │   └── settings.py                # パス・Webhook・環境変数設定
  │
  ├── users/
  │   ├── priority_users.txt         # 優先通知ユーザーID一覧
  │   └── exclude_users.txt          # 通知除外ユーザーID一覧
  │
  ├── embed.py                       # Discord embed メッセージの構築
  ├── fetch.py                       # SKIMA から作品情報を取得
  ├── main.py                        # 通知処理のメインスクリプト
  ├── notify.py                      # 通知送信処理（分離されたロジック）
  ├── score.py                       # 価格ベースのスコア・ラベル判定
  ├── seen_manager.py                # seen.json の読み書き・修復処理
  ├── utils.py                       # Webhook送信・整形・ユーザー読み込みなど
  ├── seen.json                      # 通知済み作品IDの記録
  ├── requirements.txt               # 必要なPythonパッケージ一覧
  └── README.md                      # プロジェクト説明
</details>
