# filename: server.py

import logging
import os
import typing

from flask import Flask
from flask import request

# =========================================================================
# 【修正1】Flaskアプリケーションをグローバルスコープで作成
# waitressやgunicornなどのWSGIサーバーは、グローバル変数 'application' 
# または 'app' を探します。
# =========================================================================
app = Flask("Battlesnake")
# waitressが探す変数名として 'application' も設定（互換性のため）
application = app 

# Battlesnakeのゲームロジック（info, start, move, end 関数）が
# 定義されたファイル（通常は 'snake.py'）からハンドラをインポートします。
# ここでは、もしインポートできなかった場合のためにダミーを用意しています。
try:
    from snake import handlers 
except ImportError:
    # 実際のロジックファイルが見つからない場合のフォールバック（動作確認用）
    print("Warning: Could not import 'handlers' from snake.py. Using dummy handlers.")
    handlers = {
        "info": lambda: {"apiversion": "1", "author": "MySnake", "color": "#888888", "head": "default", "tail": "default"},
        "start": lambda game_state: None,
        "move": lambda game_state: {"move": "up"},
        "end": lambda game_state: None,
    }


# =========================================================================
# 【修正2】すべてのルーティング定義（@app.get, @app.post）をグローバルスコープに移動
# 元々あった run_server 関数は不要になるため削除し、その中身をトップレベルに展開します。
# =========================================================================
@app.get("/")
def on_info():
    # 'handlers' はグローバルでアクセス可能です
    return handlers["info"]()

@app.post("/start")
def on_start():
    game_state = request.get_json()
    handlers["start"](game_state)
    return "ok"

@app.post("/move")
def on_move():
    game_state = request.get_json()
    return handlers["move"](game_state)

@app.post("/end")
def on_end():
    game_state = request.get_json()
    handlers["end"](game_state)
    return "ok"

@app.after_request
def identify_server(response):
    response.headers.set(
        "server", "battlesnake/github/starter-snake-python"
    )
    return response


# =========================================================================
# 【修正3】ローカル開発用の起動ロジックを if __name__ == "__main__": ブロックに入れる
# waitressなどのWSGIサーバーを使う場合、app.run() は実行しないようにします。
# =========================================================================
if __name__ == "__main__":
    # ローカルで 'python server.py' を実行した時のみ、このブロックが実行されます。
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print(f"\nRunning Battlesnake (Local Dev Mode) at http://{host}:{port}")
    # WSGIサーバーを使わず、Flask内蔵の簡易サーバーで実行します
    application.run(host=host, port=port)
