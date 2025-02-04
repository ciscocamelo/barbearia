from flask import Flask, request, jsonify, redirect, render_template, url_for
import stripe
import sqlite3

app = Flask(__name__)

# Configure sua API Key da Stripe (certifique-se de usar variáveis de ambiente em produção)
stripe.api_key = "sua_stripe_api_key"

def get_cliente_por_cartao(uid):
    """Consulta o banco de dados para obter o stripe_customer_id associado ao UID."""
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT stripe_customer_id FROM associacoes WHERE rfid_uid = ?", (str(uid),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

@app.route('/validar-cartao', methods=['POST'])
def validar_cartao():
    """
    Endpoint que recebe o UID do cartão via POST (em JSON) e realiza a validação:
    1. Procura a associação no banco de dados.
    2. Consulta a Stripe para obter os dados do cliente.
    3. Se o cliente estiver ativo (metadata.status == 'ativo'), retorna a URL da dashboard.
    """
    data = request.get_json()
    uid = data.get('uid')
    if not uid:
        return jsonify({"error": "UID não informado"}), 400

    stripe_customer_id = get_cliente_por_cartao(uid)
    if not stripe_customer_id:
        return jsonify({"error": "Cartão não associado a nenhum cliente"}), 404

    try:
        # Recupera os dados do cliente na Stripe
        customer = stripe.Customer.retrieve(stripe_customer_id)
        # Supondo que a metadata do cliente possua um campo 'status' com valor 'ativo'
        if customer.get("metadata", {}).get("status") == "ativo":
            # Retorna a URL completa da dashboard
            dashboard_url = url_for('dashboard', customer_id=stripe_customer_id, _external=True)
            return jsonify({"dashboard_url": dashboard_url})
        else:
            return jsonify({"error": "Cliente inativo"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """
    Renderiza a página da dashboard com as informações do cliente.
    O ID do cliente (stripe_customer_id) é passado via query string.
    """
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return "Customer ID não fornecido", 400
    try:
        customer = stripe.Customer.retrieve(customer_id)
    except Exception as e:
        return f"Erro ao recuperar dados do cliente: {str(e)}", 500

    # Renderiza o template dashboard.html passando os dados do cliente
    return render_template("dashboard.html", customer=customer)

if __name__ == '__main__':
    # Rode o servidor Flask na porta 5000 e em todas as interfaces (para acesso local e externo)
    app.run(host='0.0.0.0', port=5000)
