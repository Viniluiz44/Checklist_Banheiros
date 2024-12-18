import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from openpyxl import Workbook, load_workbook
from datetime import date
from fpdf import FPDF
import qrcode
import io


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
arquivo_excel = "manutencoes.xlsx"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from openpyxl import Workbook, load_workbook
from datetime import date

from openpyxl import Workbook, load_workbook
from datetime import date

class SistemaManutencao:
    def __init__(self, arquivo='manutencoes.xlsx'):
        self.arquivo = arquivo

    def criar_arquivo_excel(self):
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Equipamentos"
        ws1.append(["ID", "Nome", "QRCode"])
        ws2 = wb.create_sheet(title="Manutencoes")
        ws2.append(["Equipamento_ID", "Data_Manutencao", "Descricao"])
        ws3 = wb.create_sheet(title="Pecas")
        ws3.append(["Equipamento_ID", "Descricao", "Numero_Serie"])
        wb.save(self.arquivo)

    def cadastrar_equipamento(self, nome_equipamento, qr_code):
        wb = load_workbook(self.arquivo)
        ws = wb["Equipamentos"]
        next_id = ws.max_row
        ws.append([next_id, nome_equipamento, qr_code])
        wb.save(self.arquivo)

    def registrar_manutencao(self, qr_code, descricao):
        wb = load_workbook(self.arquivo)
        ws_equip = wb["Equipamentos"]

        equipamento_id = None
        for row in ws_equip.iter_rows(min_row=2, values_only=True):
            if row[2] == qr_code:
                equipamento_id = row[0]
                break

        if equipamento_id is None:
            return False

        ws_manut = wb["Manutencoes"]
        ws_manut.append([equipamento_id, str(date.today()), descricao])
        wb.save(self.arquivo)
        return True

    def consultar_historico_por_qr(self, qr_code):
        wb = load_workbook(self.arquivo)
        ws_equip = wb["Equipamentos"]
        equipamento_id = None
        nome_equipamento = None
        for row in ws_equip.iter_rows(min_row=2, values_only=True):
            if row[2] == qr_code:
                equipamento_id = row[0]
                nome_equipamento = row[1]
                break

        if equipamento_id is None:
            return None

        ws_manut = wb["Manutencoes"]
        manutencoes = []
        for row in ws_manut.iter_rows(min_row=2, values_only=True):
            if row[0] == equipamento_id:
                manutencoes.append({"data": row[1], "descricao": row[2]})

        return {"nome": nome_equipamento, "manutencoes": manutencoes}

    def adicionar_peca_excel(self, equipamento_id, descricao, numero_serie):
        try:
            wb = load_workbook(self.arquivo)
            ws = wb["Pecas"]
            ws.append([equipamento_id, descricao, numero_serie])
            wb.save(self.arquivo)
        except Exception as e:
            print(f"Erro ao adicionar peça ao Excel: {e}")


sistema = SistemaManutencao()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/criar_arquivo')
def criar_arquivo():
    sistema.criar_arquivo_excel()
    return "Arquivo Excel criado com sucesso! <br><a href='/'>Voltar</a>"

@app.route('/download_planilha')
def download_planilha():
    caminho_arquivo = os.path.join(app.root_path, 'manutencoes.xlsx')
    return send_file(caminho_arquivo, as_attachment=True, download_name='manutencoes.xlsx')


@app.route('/cadastrar_equipamento', methods=['GET', 'POST'])
def cadastrar_equipamento():
    if request.method == 'POST':
        nome_equipamento = request.form['nome_equipamento']
        qr_code = request.form['qr_code']
        sistema.cadastrar_equipamento(nome_equipamento, qr_code)
        return redirect(url_for('index'))
    return render_template('cadastrar_equipamento.html')

@app.route('/registrar_manutencao', methods=['GET', 'POST'])
def registrar_manutencao():
    checklist_items = [
        "Maçanetas", "Dobradiças", "Divisórias", "Suporte papel Higienico",
        "Suporte papel toalha", "Torneiras", "Estado lavatorio", "Estado Sifão",
        "Estado Espelho", "Quados de avisos", "Estado dos ralos", "Estado dos Vasos",
        "Válvula de descarga", "Tubo retratil vaso", "Assento sanitário", "Estado Mictório",
        "Valvula Descarga mictório", "Estado luminárias", "Espelho", "Interruptor / Tomadas",
        "Mola de porta"
    ]
    
    if request.method == 'POST':
        qr_code = request.form['qr_code']
        checklist = {key: request.form.get(f'checklist[{key}]') for key in checklist_items}
        descricao = "; ".join(f"{item}: {status}" for item, status in checklist.items() if status)
        sucesso = sistema.registrar_manutencao(qr_code, descricao)
        if sucesso:
            return "Manutenção registrada com sucesso! <br><a href='/'>Voltar</a>"
        else:
            return "QR Code não encontrado! <br><a href='/registrar_manutencao'>Tente novamente</a>"
    return render_template('registrar_manutencao.html', checklist_items=checklist_items)




@app.route('/consultar_historico', methods=['GET', 'POST'])
def consultar_historico():
    if request.method == 'POST':
        qr_code = request.form['qr_code']
        historico = sistema.consultar_historico_por_qr(qr_code)
        if historico:
            return render_template('historico.html', historico=historico)
        else:
            return "QR Code não encontrado! <br><a href='/consultar_historico'>Tente novamente</a>"
    return render_template('consultar_historico.html')

@app.route('/explorador')
def explorador():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('explorador.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('explorador'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('explorador'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
    return redirect(url_for('explorador'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('explorador'))

@app.route('/ler_qrcode')
def ler_qrcode():
    return render_template('ler_qrcode.html')

@app.route('/gerar_qrcode_pdf', methods=['POST'])
def gerar_qrcode_pdf():
    data = request.get_json()
    qr_code_text = data.get('qr_code')
    
    if not qr_code_text:
        return "QR Code é necessário", 400

    # Gerar QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_text)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Salvar a imagem em um arquivo temporário
    temp_file = 'temp_qrcode.png'
    img.save(temp_file)

    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'QR Code:', ln=True)
    pdf.image(temp_file, x=10, y=20, w=100)

    # Salvar PDF em um arquivo temporário
    temp_pdf = 'temp_qrcode.pdf'
    pdf.output(temp_pdf)

    # Ler o PDF e enviar como resposta
    with open(temp_pdf, 'rb') as f:
        buffer_pdf = f.read()

    # Remover os arquivos temporários
    os.remove(temp_file)
    os.remove(temp_pdf)

    return send_file(io.BytesIO(buffer_pdf), as_attachment=True, download_name='qrcode.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
