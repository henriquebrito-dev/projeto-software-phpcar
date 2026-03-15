from flask import Flask, render_template, request, flash, redirect
import pyodbc

app = Flask(__name__)
app.secret_key = "php_soluctions_key_2024" # Segurança para as mensagens de aviso

# Suas configurações originais de conexão
config_db = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost,1401;'
    'DATABASE=php car;' 
    'UID=sa;'
    'PWD=hgservices23'
)

# Listas de opções que você usava no script original
OPCOES_COMBUSTIVEL = ['Gasolina', 'Álcool', 'Flex', 'Diesel', 'GNV', 'Elétrico', 'Híbrido']
OPCOES_TRANSMISSAO = ['Manual', 'Automático', 'CVT', 'Automatizado']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Coleta de dados do formulário (Substitui o obter_input)
        marca = request.form.get('marca').strip()
        modelo = request.form.get('modelo').strip()
        versao = request.form.get('versao').strip()
        
        # Tratamento de anos (como você fazia: removendo pontos e convertendo)
        try:
            ano_fab = int(request.form.get('ano_fab').replace('.', ''))
            ano_mod = int(request.form.get('ano_mod').replace('.', ''))
        except:
            flash("❌ Erro nos campos de Ano. Use apenas números.", "danger")
            return redirect('/')

        cor = request.form.get('cor').strip()
        km = request.form.get('km').strip() # Mantido como texto conforme seu original
        combustivel = request.form.get('combustivel')
        transmissao = request.form.get('transmissao')
        placa = request.form.get('placa').strip()
        preco = request.form.get('preco').strip() # Mantido como texto conforme seu original
        descricao = request.form.get('descricao').strip()

        # Validação de segurança (Caso alguém tente burlar o formulário)
        if combustivel not in OPCOES_COMBUSTIVEL or transmissao not in OPCOES_TRANSMISSAO:
            flash("❌ Opção de combustível ou transmissão inválida!", "danger")
            return redirect('/')

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
            
            flash(f"✅ {marca} {modelo} cadastrado com sucesso! (Preço: R$ {preco})", "success")
            
        except Exception as e:
            flash(f"❌ Erro ao gravar no banco: {e}", "danger")

        return redirect('/')

    # Carrega a página passando as listas para o HTML criar os menus automáticos
    return render_template('index.html', combustiveis=OPCOES_COMBUSTIVEL, transmissoes=OPCOES_TRANSMISSAO)

if __name__ == '__main__':
    # Adicionamos o parâmetro port=5001
    app.run(debug=True, port=5001) 