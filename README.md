# AIDeckPP / deck2pptx

AI に PowerPoint 資料を作らせるための、意味構造ベースの PPTX 生成CLIコマンドです。

YAML 、 Markdown 、ASCIIDOC の形式を変換します。 README_AI を AI に理解させて、 AIに処理させるとよいと思います。 AI フレンドリーな CLI を目指しています。

## まず読むもの

- 人間向け: この `README.md`
- AI 向け: `README_AI.md`
- 詳細なリリース確認: `docs/release-verification.md`
- ソース管理方針: `docs/source-baseline.md`

AI に処理を依頼するときは、まず `README_AI.md` を見せてください。

## 環境作成

PowerShell でリポジトリ直下に移動して、repo-local の仮想環境を作成します。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e . pytest python-pptx pyyaml pillow
```

通常の作業では、この `.venv` を使ってください。

```powershell
.\.venv\Scripts\Activate.ps1
```

### Mermaid の描画セットアップ

`` `mermaid `` ブロックを画像としてスライドに埋め込むには、システムに **Mermaid CLI (`mmdc`)** および Puppeteer 用のブラウザが必要です。
*(※ `` `flow `` ブロックは内部エンジンによって PowerPoint の標準図形として描画されるため、外部の CLI やブラウザは不要です。)*

1. **Mermaid CLI のグローバルインストール**:
   ```powershell
   npm install -g @mermaid-js/mermaid-cli
   ```
2. **ヘッドレスブラウザ (Puppeteer) のセットアップ**:
   もし `mmdc` 実行時に `Could not find Chrome` などのエラーが発生した場合は、`mermaid-cli` が要求するバージョンのブラウザをインストールしてください。
   ```powershell
   npx.cmd puppeteer browsers install chrome-headless-shell@148.0.7778.97
   ```
   *(※ Windows PowerShell 上では実行ポリシーの関係上、`npx` の代わりに `npx.cmd` を明示して呼び出す必要があります。)*

*※ Mermaid CLI がインストールされていない環境では、エラーや強制終了せず、ソースコードが自動的に `CodeBlock` （黒背景枠付きのデバッグ用テキスト）としてスライド上にフォールバック描画されます。*

## CLIコマンドの概要

CLIのメインエントリポイントは `deck2pptx` です（`python -m deck2pptx` で呼び出し）。以下、概要。

基本は、AI が利用します。

### 1. `explain-spec`
AI向けのモデルスキーマ（JSONなど）を出力します。

### 2. `inspect`
入力ファイルをパースし、標準化された Deck モデルの表現（内部構造）を出力します。

### 3. `inspect-template`
PowerPoint テンプレート（`.pptx`）のレイアウト構造、プレースホルダー名、およびタイプIDを解析・出力します。

### 4. `validate`
入力ファイルが Deck モデルスキーマに準拠しているかバリデーション（妥当性検証）を行います。

### 5. `build`
入力ファイルから PowerPoint プレゼンテーション（`.pptx`）をビルドして生成します。

---

## 基本的な記法

`ReferenceSheet.md` に説明があります。

## ライセンス

このプロジェクトは MIT License です。詳細は `LICENSE` を参照してください。
