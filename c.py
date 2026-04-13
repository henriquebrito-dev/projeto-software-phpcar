from flask import Flask, render_template, request, flash, redirect
import pyodbc

app = Flask(__name__)
app.secret_key = "php_soluctions_key_2024"

# Configurações de conexão (Centralizadas aqui)
config_db = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost,1401;'
    'DATABASE=php car;' 
    'UID=sa;'
    'PWD=hgservices23'
)

OPCOES_COMBUSTIVEL = ['Gasolina', 'Álcool', 'Flex', 'Diesel', 'GNV', 'Elétrico', 'Híbrido']
OPCOES_TRANSMISSAO = ['Manual', 'Automático', 'CVT', 'Automatizado']

# --- ROTA 1: MENU PRINCIPAL (DIRECIONADOR) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ROTA 2: FORMULÁRIO DE CADASTRO ---
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Toda a sua lógica de coleta de dados
        marca = request.form.get('marca').strip()
        modelo = request.form.get('modelo').strip()
        versao = request.form.get('versao').strip()
        
        try:
            ano_fab = int(request.form.get('ano_fab').replace('.', ''))
            ano_mod = int(request.form.get('ano_mod').replace('.', ''))
        except:
            flash("❌ Erro nos campos de Ano. Use apenas números.", "danger")
            return redirect('/cadastrar')

        cor = request.form.get('cor').strip()
        km = request.form.get('km').strip()
        combustivel = request.form.get('combustivel')
        transmissao = request.form.get('transmissao')
        placa = request.form.get('placa').strip()
        preco = request.form.get('preco').strip()
        descricao = request.form.get('descricao').strip()

        # Inserção no Banco de Dados
        try:
            conn = pyodbc.connect(config_db)
            cursor = conn.cursor()
            sql = """
                INSERT INTO veiculos (
                    marca, modelo, versao, ano_fabricacao, ano_modelo, 
                    cor, quilometragem, combustivel, transmissao, 
                    placa_final, preco, descricao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (marca, modelo, versao, ano_fab, ano_mod, cor, km, 
                                combustivel, transmissao, placa, preco, descricao))
            conn.commit()
            conn.close()
            flash(f"✅ {marca} {modelo} cadastrado com sucesso!", "success")
        except Exception as e:
            flash(f"❌ Erro ao gravar no banco: {e}", "danger")

        return redirect('/cadastrar')

    return render_template('cadastrar.html', combustiveis=OPCOES_COMBUSTIVEL, transmissoes=OPCOES_TRANSMISSAO)

@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
    try:
        conn = pyodbc.connect(config_db)
        cursor = conn.cursor()
        
        # 1. Pega os dados e LIMPA TUDO (ponto e vírgula) que o navegador enviar
        busca = request.args.get('busca', '').strip()
        preco_min = request.args.get('preco_min', '').replace('.', '').replace(',', '').strip()
        preco_max = request.args.get('preco_max', '').replace('.', '').replace(',', '').strip()
        ano = request.args.get('ano', '').strip()

        # SQL com apelidos para o HTML
        sql = """
            SELECT 
                marca AS marca, 
                modelo AS modelo, 
                versao AS versao, 
                cor AS cor, 
                ano_fabricacao AS ano_fab, 
                ano_modelo AS ano_mod, 
                quilometragem AS km, 
                preco AS preco 
            FROM veiculos WHERE 1=1
        """
        params = []

        if busca:
            sql += " AND (marca LIKE ? OR modelo LIKE ?)"
            params.extend([f'%{busca}%', f'%{busca}%'])

        # Lógica de Preço Blindada no SQL também
        if preco_min:
            sql += " AND CAST(REPLACE(REPLACE(preco, '.', ''), ',', '.') AS DECIMAL(18,2)) >= ?"
            params.append(preco_min)
        if preco_max:
            sql += " AND CAST(REPLACE(REPLACE(preco, '.', ''), ',', '.') AS DECIMAL(18,2)) <= ?"
            params.append(preco_max)

        if ano:
            sql += " AND (ano_fabricacao = ? OR ano_modelo = ?)"
            params.extend([ano, ano])

        cursor.execute(sql, params)
        
        columns = [column[0] for column in cursor.description]
        veiculos = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return render_template('consultar.html', veiculos=veiculos)
    except Exception as e:
        return f"Erro: {e}"

# --- ROTAS FUTURAS (AC 3) ---
@app.route('/excluir')
def excluir():
    return "<h1>Página de Exclusão</h1><p>Em desenvolvimento...</p>"

@app.route('/vendas')
def vendas():
    return "<h1>Página de Vendas</h1><p>Em desenvolvimento...</p>"



if __name__ == '__main__':
    app.run(debug=True, port=5001)
