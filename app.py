from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configurações do Xano
XANO_BASE_URL = os.getenv('XANO_BASE_URL', "https://xidg-u2cu-sa8e.n7c.xano.io/api:loOqZbWF")
XANO_API_KEY = os.getenv('XANO_API_KEY', "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.mkHrc0TbjCoGEtCKj09icdxyYz1l5_x_Jak_X1BHUp8_pYG3BeUaoR6aXRdVKU8Rz5mwUvg1WdB_0Xcp8e447WPZYwPKkkW2.W91buAlXx6KbbosVOeyxiA.i_59CKR8MxcFf2lcJWJxlfq2DcwC6aiqBvp8NYo9ifPgCXbM8p5cOlepfpTejTH4fYOrxBzJvzcdT_tUCq_GUQ79Iukr8PYQVrZDm8ptqoTFvcZt7oEaL1Wj8sm3WT_GM6YUAxyv4ijZiK74tGaQcw.oabJrcYhWKf369_mB6PNhwVtrHm3aXl0nSrM283X_s0")

def get_xano_data(endpoint, params=None):
    """Função auxiliar para consultar dados no Xano"""
    headers = {
        'Authorization': f'Bearer {XANO_API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(
            f'{XANO_BASE_URL}{endpoint}',
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Xano: {str(e)}")
        return None

# Rota para servir o index.html fora de templates
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Rota para o dashboard

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Rota para servir arquivos estáticos (CSS, JS, imagens)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Endpoint para listar candidatos
@app.route('/api/candidatos', methods=['GET'])
def listar_candidatos():
    try:
        search_term = request.args.get('search', '').strip()
        params = {'search': search_term} if search_term else None
        
        data = get_xano_data('/candidatos', params)

        if data is not None:
            candidatos = []
            for c in data:
                candidatos.append({
                    "nome": c.get("nome", ""),
                    "area_atuacao": c.get("area_atuacao", "")
                })

            return jsonify({
                "success": True,
                "candidatos": candidatos,
                "timestamp": datetime.now().isoformat()
            })
        return jsonify({
            "success": False,
            "message": "Erro ao consultar candidatos no Xano"
        }), 502

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

# Endpoint para registrar avaliação
@app.route('/api/avaliacoes', methods=['POST'])
def criar_avaliacao():
    try:
        data = request.json

        campos_obrigatorios = [
            'nome_candidato', 'area_atuacao', 'avaliador',
            'diagnostico_problema', 'qualidade_proposta', 'conexao_objetivos',
            'uso_dados', 'clareza_apresentacao', 'protagonismo',
            'visao_futuro', 'comunicacao', 'colaboracao', 'adequacao_cultura',
            'recomendacao_final'
        ]

        # Validação de campos obrigatórios
        faltantes = [campo for campo in campos_obrigatorios if campo not in data or not data[campo]]
        if faltantes:
            return jsonify({
                "success": False,
                "message": f"Campos obrigatórios faltantes ou vazios: {', '.join(faltantes)}"
            }), 400

        campos_notas = [
            'diagnostico_problema', 'qualidade_proposta', 'conexao_objetivos',
            'uso_dados', 'clareza_apresentacao', 'protagonismo',
            'visao_futuro', 'comunicacao', 'colaboracao', 'adequacao_cultura'
        ]

        # Conversão e validação das notas
        for campo in campos_notas:
            try:
                data[campo] = int(data[campo])
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "message": f"Nota {campo} deve ser um número inteiro válido."
                }), 400

            if data[campo] < 1 or data[campo] > 5:
                return jsonify({
                    "success": False,
                    "message": f"Nota {campo} deve ser um inteiro entre 1 e 5."
                }), 400

        # Cálculo de notas
        nota_tecnica = sum(data[campo] for campo in campos_notas[:5])
        nota_comportamental = sum(data[campo] for campo in campos_notas[5:])
        nota_total = nota_tecnica + nota_comportamental

        # Monta payload para envio ao Xano
        payload = {
            "nome_candidato": data['nome_candidato'],
            "area_atuacao": data['area_atuacao'],
            "avaliador_nome": data['avaliador'],
            "data_avaliacao": datetime.now().isoformat(),
            **{campo: data[campo] for campo in campos_notas},
            "nota_tecnica": nota_tecnica,
            "nota_comportamental": nota_comportamental,
            "nota_total": nota_total,
            "pontos_fortes": data.get('pontos_fortes', ''),
            "aspectos_aprimorar": data.get('aspectos_aprimorar', ''),
            "recomendacao_eleva": data.get('recomendacao_eleva', ''),
            "recomendacao_final": data['recomendacao_final']
        }

        headers = {
            'Authorization': f'Bearer {XANO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{XANO_BASE_URL}/avaliacoes',
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.ok:
            return jsonify({
                "success": True,
                "message": "Avaliação registrada com sucesso!",
                "dados": response.json()
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": f"Erro {response.status_code} no Xano: {response.text}"
            }), 502

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

# Healthcheck
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Avaliação API",
        "version": "1.0.0"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)