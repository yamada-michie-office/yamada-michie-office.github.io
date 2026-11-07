# 山田みちえ ホームページ

公開先: https://yamada-michie-office.github.io/

## ブログの更新

1. https://app.pagescms.org/ を開き、GitHubでログインします。
2. `yamada-michie-office/yamada-michie-office.github.io` を選択します。
3. 「活動ブログ」で記事を作成、または既存記事を選択します。
4. タイトル・日付・本文を入力し、写真を追加します。
5. サイトに載せる記事は「公開する」をオンにして保存します。
6. GitHub Actionsの「ホームページを公開」が完了すると反映されます（通常数分）。

**このリポジトリは公開です。** 「公開する」をオフにした下書きも、GitHub上のファイルとして閲覧できます。個人情報・相談内容・未公表の機密情報は保存しないでください。

本文中の画像は本文の編集画面から挿入できます。「一覧に表示する写真」はブログ一覧用です。JPEG・PNG・WebP等を使用してください。

## ファイル構成

- `site/`: ホームページと画像、既存の固定ページ
- `content/posts/`: ブログの記事データ（1記事1 JSONファイル）
- `.pages.yml`: ブログ管理画面の設定
- `scripts/build.py`: 記事ページ・記事一覧・トップの最新記事を生成
- `.github/workflows/pages.yml`: 保存後の自動公開
- `build/`: 生成された公開用ファイル（Git管理しません）

古いホームページのブログ862件と画像・PDFを移行しています。旧URLへの依存を避け、画像はこのリポジトリに保存しています。

## ローカル確認

Python 3.12以上で実行します。外部パッケージは不要です。

```sh
python3 scripts/test_build.py
python3 scripts/build.py
python3 -m http.server 8765 --directory build
```

## 権限と引き継ぎ

Pages CMSはこのリポジトリだけにインストールします。本人または事務所担当者をOrganizationの所有者に追加すると引き継げます。

独自ドメインを使う場合はGitHub Pagesの設定とDNSを変更し、`scripts/build.py` の `SITE_URL` を更新してください。

掲載内容の本人確認が済むまでは、サイト上の「リニューアル案」の表示を残しています。
