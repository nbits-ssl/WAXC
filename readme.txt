
WickedWhims Animation XML Converter 
====================================================================

性別のBOTHを書き換えるためだけに使っていたWWAniXmlTweaksがPropを消し
てしまうのに気づいて作成しました。

同性愛でWWが発動してしまうのを防ぐためだけに使っていたため、他の機能
の使いやすさとかはあまり気にしていません。


## 概要

* WW AnimationのXMLファイルをタブ区切りのCSV(TSV)に変換して、表計算ソ
  フトなどでいじれるようにします。

* いじった後にXMLファイルに戻せます。

* XMLファイルの取り出しや埋め込みは外部ソフト(s4peなど)任せです。

* Pythonでの実装ですが、Windowsで使いやすいようにexeファイルとbatファ
  イルを同梱しています。


## 使い方

0. resフォルダにある_priority.txtと_alternative.txtの最初の「_」を消す
1. s4peなどでpackageからxmlを取り出す
2. xmlをwaxc-parse.batにドラッグアンドドロップ
3. csvファイルを編集
4. csvファイルをwaxc-dump.batにドラッグアンドドロップ
5. xmlをs4peなどで埋め込む

※ pythonの実行環境がある方は`python waxc.py -h`を見てください

### priority.txtとalternative.txtとalternative

res/priority.txtにあるヘッダ要素はcsvの一番左側に配置されます。

res/alternative.txtは「: 」で区切られたテーブルであり、parse時には
左のWWの語句→右の独自語句、dump時にはその逆に文字列を変換します。

alternative.txtの右の語句は、他の語句に出てこないユニークなものにして
ください。

正しい)

  animation_genders: 性別(主)
  animation_pref_gender: 性別(優先)

誤り) 「性別」という文字列は下の「性別(優先)」の中にも出てくる

  animation_genders: 性別
  animation_pref_gender: 性別(優先)

保存はutf-8でしてください。
また、dont_run_ifまわりには効かないと思います。


## 注意事項

* エラー処理はまじめにしていません。処理状況は適当に垂れ流しているの
  で、止まってしまった場合は処理途中のアニメの記述を確認してください。

* filename.pkgname.txtはcsvを生成するときに一緒に生成されます。xmlの
  先頭行を生成するために必要なものなので、削除したり編集したりしない
  で下さい。(csvを削除する際には一緒に削除して構いません)

* 値を保持していない要素(<T></T>ないし<T/>)は消えます。

* コメントは消えます。

* csvのヘッダにあたる要素は大きなカテゴリごとにファイルに出現した順番
  で追加されていきます。(root / actor / interactions / prop / event)
  xml生成の時はその順番に従って生成するため、元のファイルと要素の順番
  がずれることがあります。
  (actor_idの順番が途中から変更されるファイルなどは、diffを取るとひど
  いことに……)
  
* csvのヘッダの文字列はxml生成用の制御文字が入っているところがあるので、
  編集の際はお気を付けください。$***, _n, dont_run_if-など。
  
* actor_interactionsのところはxml生成時にソートしているので、順番がず
  れるかもしれません。
  
* デフォルトではWickedWhims公式にあわせて<L>や<U>で出力すべきところは
  その通りにします。
  <T>で出力したい場合はwaxc.iniのTagNameをclassicにしてください。

* 2021/2/7時点でWWのページで「Honorary Creators」にあげられているアニ
  メの何種類かはエラーなく通過するのを確認済みです。
  
* 要素の名称や内容にはタッチしないので、そこの増減や変更は元のxmlがあれ
  ば問題ありませんが、要素の入れ子になっている部分では各々の処理をして
  いるので、そこの増減には更新しないと対応できません。


## 制作者の環境

* Python 3.7.9 (bat & exeを使えばなくても動作します)
* LibreOffice Calc
* s4pe


## 謝辞

* EA
* TURBODRIVER @ WhikedWhims
* Ashal @ LoversLab
* halapeco @ ワールドに存在しません
* picolet21 @ WWAniXmlTweaks
* シムズ4 エロMod避難所 @ bbspink

* znerol / py-fnvhash @ github (MIT license)


## 更新履歴

* 2021/02/** - 0.2 初回リリース


----------------------------------------------------------------------


## おまけ機能

おまけというか開発に使っている機能ですがtidyとtestモードがあります。
pythonが動かない環境で必要があったらresフォルダからwaxc.pyがあるフォルダ
に移動して使ってください。

### tidy 

waxcが生成するxmlの整形に使用している処理を、読み込んだxmlに適用します。
元xmlに適用して、わかりやすいdiffを取るために使用しています。

### test

CLIで動くdiffコマンドが必要です。下記を処理を全部やります。

1. tmpフォルダを作ります
2. 元xmlファイルにtidyを通してtmpに置きます
3. xmlファイルをparseしてcsvなどを作ってtmpに置きます
4. tmpに置かれたcsvなどをそのまま使ってdumpします
5. 'diff {tidyしたxmlファイル} {生成したxmlファイル}'を実行してtmpに
   x.diffとして出力します
