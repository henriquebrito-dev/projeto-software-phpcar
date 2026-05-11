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
        # Padronizado para 'placa' em todo o sistema
        placa = request.form.get('placa').strip().upper()
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
                    placa, preco, descricao
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
        
        # Pega os dados da busca
        busca = request.args.get('busca', '').strip()
        preco_min = request.args.get('preco_min', '').replace('.', '').replace(',', '').strip()
        preco_max = request.args.get('preco_max', '').replace('.', '').replace(',', '').strip()
        ano = request.args.get('ano', '').strip()

        # SQL Corrigido para a coluna 'placa'
        sql = """
            SELECT 
                marca AS marca, 
                modelo AS modelo, 
                versao AS versao, 
                cor AS cor, 
                ano_fabricacao AS ano_fab, 
                ano_modelo AS ano_mod, 
                quilometragem AS km, 
                preco AS preco,
                placa AS placa
            FROM veiculos WHERE 1=1
        """
        params = []

        if busca:
            sql += " AND (marca LIKE ? OR modelo LIKE ? OR placa LIKE ?)"
            params.extend([f'%{busca}%', f'%{busca}%', f'%{busca}%'])

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

# --- ROTAS DE EXCLUSÃO ---
@app.route('/excluir')
def excluir():
    return "<h1>Página de Exclusão</h1><p>Em desenvolvimento...</p>"

# --- ROTAS DE VENDAS ---
@app.route('/vendas', methods=['GET'])
def exibir_vendas():
    try:
        conn = pyodbc.connect(config_db)
        cursor = conn.cursor()
        # Busca placas disponíveis para o autocomplete bonitão
        cursor.execute("SELECT placa FROM veiculos")
        lista_placas = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return render_template('vendas.html', placas_sugeridas=lista_placas)
    except Exception as e:
        return f"Erro ao carregar placas: {e}"

@app.route('/registrar_venda', methods=['POST'])
def registrar_venda():
    placa = request.form.get('placa').strip().upper()
    valor_bruto = request.form.get('valor') or "0"
    
    # Melhorei a limpeza do valor para aceitar pontos e vírgulas corretamente
    valor = valor_bruto.replace('.', '').replace(',', '.')

    vendedor = request.form.get('vendedor') or "Henrique Brito"

    try:
        conn = pyodbc.connect(config_db)
        cursor = conn.cursor()
        
        # 1. Insere na tabela de vendas
        cursor.execute("""
            INSERT INTO vendas (placa_veiculo, valor_venda, vendedor, data_venda)
            VALUES (?, ?, ?, GETDATE())
        """, (placa, valor, vendedor))
        
        # 2. Deleta de veículos usando o nome correto da coluna: placa
        cursor.execute("DELETE FROM veiculos WHERE placa = ?", (placa,))
        
        conn.commit()
        conn.close()
        flash("💰 Venda registrada com sucesso!", "success")
    except Exception as e:
        flash(f"❌ Erro ao processar venda: {e}", "danger")
        
    return redirect('/vendas')

@app.route('/historico_vendas')
def historico_vendas():
    try:
        conn = pyodbc.connect(config_db)
        cursor = conn.cursor()
        
        # Busca todas as vendas realizadas
        sql = "SELECT placa_veiculo, valor_venda, vendedor, data_venda FROM vendas ORDER BY data_venda DESC"
        cursor.execute(sql)
        
        columns = [column[0] for column in cursor.description]
        vendas_brutas = cursor.fetchall()
        
        # Formata o preço direto no Python para garantir os centavos na lista
        vendas_realizadas = []
        for row in vendas_brutas:
            dicionario = dict(zip(columns, row))
            # Formata o valor para string com 2 casas decimais e separador de milhar
            dicionario['valor_venda'] = "{:,.2f}".format(float(dicionario['valor_venda'])).replace(',', 'v').replace('.', ',').replace('v', '.')
            vendas_realizadas.append(dicionario)
        
        conn.close()
        return render_template('historico.html', vendas=vendas_realizadas)
    except Exception as e:
        return f"Erro ao carregar histórico: {e}"


if __name__ == '__main__':
