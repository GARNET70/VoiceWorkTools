# VoiceWork 音声作品整理スクリプト

このフォルダには、音声作品フォルダの情報取得、RAR作成、不要ファイルの整理、音声ファイルへのメタデータ設定、および音声ファイルの移動を行うPythonスクリプトが含まれています。

## スクリプト一覧

| ファイル | 概要 |
| --- | --- |
| `01_CreateInfoJson.py` | `json/paths.json` の `rename.path` 直下にある各作品フォルダを調べ、フォルダ名からRJ番号を取得します。DLsiteの商品ページから作品情報・画像を取得し、作品フォルダに `dlsite_info.json` と画像を保存します。フォルダ名にRJ番号が見つからない場合や取得中にエラーが起きた場合は、その作品をスキップして次へ進みます。 |
| `02_CreateRAR.py` | `rename.path` 直下の作品フォルダごとにWinRARでRARファイルを作成します。作成したRARを `rar.path` へ移し、元の作品フォルダを `work.path` へ移します。Windowsで使用できないRARファイル名はスキップします。 |
| `03_TempFilesRemover.py` | `work.path` 直下の各作品フォルダを整理します。対象のテキスト・画像・`dlsite_info.json` と「繁體中文」「简体中文」フォルダを `00_tempfiles` へ移動します。「日本語」フォルダは中身を作品フォルダ直下へ移してから、空になったフォルダを退避します。同名の移動先がある項目は上書きせず、エラーを表示します。 |
| `04_SetMetaData.py` | `work.path` 直下の作品フォルダから `metainfo.json` を読み込み、音声ファイルのタイトル・アルバム名・アルバムアーティスト・アーティストを設定します。WAV/FLACはMP3へ変換し、変換元を `Original` に保存します。作品画像をMP3のカバーアートとして設定した後、作品フォルダを `comp.path` へ移します。`metainfo.json` がない作品フォルダは `esc.path` へ移します。 |
| `05_MoveMusic.py` | `comp.path` の作品フォルダから音声ファイルを選び、`addfiles.path` へ移動します。MP3があればMP3を対象にし、MP3がなければFLACを対象にします。対象外として指定されたサークル名のフォルダ、および移動先に同名の音声ファイルがあるフォルダは `esc.path` へ移します。処理後に移動件数などを表示します。 |
| `99_Decode_json.py` | カレントディレクトリの `metainfo.json` を読み込み、アルバムタイトル・アルバムアーティスト・アーティストを `output.txt` に書き出す確認用スクリプトです。 |
| `lib/DLsite_scraping.py` | `01_CreateInfoJson.py` から利用されるDLsite取得モジュールです。RJ番号を使って作品ページを取得し、作品情報と画像を作品フォルダへ保存します。 |

## 処理の流れ

作業場所は `json/paths.json` で指定します。現状の設定では、各場所は `D:\work\voice\...` です。実行環境に合わせてパスを変更してください。

大まかな処理は次のとおりです。

1. `01_CreateInfoJson.py` — `rename.path` の作品フォルダからDLsite情報・画像を取得
2. `02_CreateRAR.py` — RARを作成し、RARと作品フォルダを所定の場所へ移動
3. `03_TempFilesRemover.py` — `work.path` の作品フォルダ内を整理
4. `04_SetMetaData.py` — メタデータ設定・音声変換後、作品フォルダを `comp.path` または `esc.path` へ移動
5. `05_MoveMusic.py` — `comp.path` の音声ファイルを `addfiles.path` へ移動

すべての工程を必ずこの順で実行する必要があるとは限りません。各スクリプトが参照する場所と前提ファイルを確認してから実行してください。

## 実行方法

WindowsのコマンドプロンプトまたはPowerShellで、このプロジェクトのルートフォルダをカレントディレクトリにして実行します。

```powershell
py 01_CreateInfoJson.py
```

他のスクリプトも同様に、対象ファイル名を指定します。設定ファイルを相対位置から読み込むスクリプトがあるため、プロジェクトルートから実行してください。

## 設定・前提条件

- `json/paths.json` の各パスは、実際の作業環境に合わせて設定してください。Pythonスクリプトによってはパス文字列を連結しているため、設定値の末尾に `\` を含めてください。
- `02_CreateRAR.py` は `C:\Program Files\WinRAR\WinRAR.exe` を使用します。WinRARを別の場所にインストールしている場合は、スクリプト内の実行ファイルパスを変更してください。
- `04_SetMetaData.py` は、Pythonパッケージ `mutagen` と `ffmpeg-python` に加えて、コマンドラインで実行できる `ffmpeg` が必要です。WAV/FLACを変換する場合は `Original` フォルダを作成し、変換前ファイルをその中へ移動します。
- `01_CreateInfoJson.py` は `requests` と `beautifulsoup4` を使ってDLsiteへアクセスします。ネットワーク接続が必要です。
- `01_CreateInfoJson.py` が保存する情報ファイル名は `dlsite_info.json` ですが、`04_SetMetaData.py` が読み込むファイル名は `metainfo.json` です。これらは別ファイルです。メタデータ設定を実行する前に、`metainfo.json` を各作品フォルダに用意してください。
- `04_SetMetaData.py` は `metainfo.json` があるフォルダ内のJPEG/JPG画像（なければPNG画像）をカバーアートに使います。
- `05_MoveMusic.py` の対象外サークル名はスクリプト内の `NotTarget` に定義されています。

## 補助ファイル

`bat/` には次のバッチファイルがあります。

- `Compression.bat` — WinRARで指定フォルダを圧縮します。
- `AddFiles.bat` — 既存RARへPNG/JPG画像を追加更新します。
- `AddImage.bat` — ffmpegで音声ファイルへ画像を添付する処理を行います。
- `alllist.bat` — カレントフォルダの項目名を `file.txt` に出力します。

## 注意事項

- これらのスクリプトはファイルやフォルダを移動・変換します。初回実行時や設定変更後は、重要なデータをバックアップしたうえで、対象フォルダと移動先を確認してください。
- ファイル名の衝突や変換失敗が起きると、処理を完了できない場合があります。各スクリプトのコンソール出力を確認してください。
- `99_Decode_json.py` は実行したカレントディレクトリにある `metainfo.json` を読み込み、同じ場所の `output.txt` を上書きします。
