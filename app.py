import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # libera requisições vindas de outra origem (o HTML)

DB = "banco.db"


def conectar():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabela():
    with conectar() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                categoria TEXT
            )"""
        )


@app.route("/produtos", methods=["GET"])
def listar_produtos():
    with conectar() as conn:
        linhas = conn.execute("SELECT * FROM produtos ORDER BY id DESC").fetchall()
    return jsonify([dict(l) for l in linhas]), 200


@app.route("/produtos", methods=["POST"])
def cadastrar_produto():
    dados = request.get_json(silent=True)
    if not dados or not dados.get("nome") or dados.get("preco") is None:
        return jsonify({"erro": "Informe nome e preco."}), 400

    try:
        preco = float(dados["preco"])
    except (TypeError, ValueError):
        return jsonify({"erro": "Preço inválido."}), 400

    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO produtos (nome, preco, categoria) VALUES (?, ?, ?)",
            (dados["nome"].strip(), preco, dados.get("categoria", "").strip()),
        )
        novo_id = cur.lastrowid

    return jsonify({"id": novo_id, "mensagem": "Produto cadastrado com sucesso!"}), 201


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True, port=5000)
