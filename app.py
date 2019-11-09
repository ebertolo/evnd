from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Rotinas Principais
@app.route("/")
def index():
    return render_template("pages/index.html", pagina="EVND - Home")

@app.route("/item/<name>")
def item(name):
    return render_template("pages/home.html", name=name, items=["arroz", "feijao", "farinha" , "teste"])


# Paginas de Erros customizados
@app.errorhandler(404)
def page_not_found(e):
    return render_template("exceptions/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("exceptions/500.html"), 500


# Permite execucao via script
if __name__ == "__main__":
    app.run(host="0.0.0.0")
