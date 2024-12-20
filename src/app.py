import os
import requests  # Biblioteca para realizar requisições HTTP
from flask import Flask, request, jsonify, json  # Bibliotecas do Flask
import google.generativeai as genai  # Biblioteca Gemini


# Cria uma instância do aplicativo Flask
app = Flask(__name__)

# Configuração da chave de API do Gemini:
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Função para obter a previsão do tempo:
def get_weather(city):
    api_key = "3261a44eabac788b20668061bbbbe891"  # Chave da API do OpenWeatherMap (substitua por sua chave)
    
    # Monta a URL da API com a cidade, chave da API e parâmetros para unidades de temperatura em Celsius e idioma em português
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt_br"
    
    # Faz a requisição HTTP GET para obter os dados do clima
    response = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida (status 200)
    if response.status_code == 200:
        data = response.json()  # Converte a resposta JSON da API em um dicionário Python
        
        # Extrai as informações sobre o clima e a temperatura
        weather = data['weather'][0]['description']  # Descrição do clima
        temp = data['main']['temp']  # Temperatura em Celsius
        
        # Retorna as informações do clima como um dicionário
        return {
            'City': city.title(),  # title() - Primeira letra de cada palavra que compõe o nome da cidade em maiúsculo
            'Weather': weather.capitalize(),  # Descrição do clima com a primeira letra maiúscula
            'Temperature': f"{temp} °C"  # Temperatura formatada em °C
        }
    else:
        # Se a requisição falhou (status diferente de 200), retorna um erro
        return {'error': 'Não foi possível obter o clima.'}

# Função para chamar o modelo Gemini e gerar uma resposta
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

def extract_city_from_input(user_input):
    # Convertendo a entrada para minúsculas para facilitar a comparação
    user_input = user_input.lower()
    
    # Listando palavras-chave relacionadas ao clima
    keywords = ['temperatura', 'tempo', 'previsão', 'previsao', 'clima']
    
    # Verifica se a entrada contém palavras-chave de clima
    if any(keyword in user_input for keyword in keywords):
        # Se a entrada contiver a palavra "em", tenta extrair a cidade
        if "em" in user_input:
            # Extraímos o nome da cidade após a palavra "em"
            city = user_input.split("em")[-1].strip("?").strip()
            if city:
                return city.title()
    
    # Se não houver palavras-chave relacionadas ao clima, mas houver "em", tenta identificar a cidade
    if "em" in user_input:
        # Extraímos o nome da cidade após a palavra "em"
        city = user_input.split("em")[-1].strip("?").strip()
        if city:
            return city.title()

    # Se não encontrar uma cidade, retorna None
    return None


# Endpoint principal do chatbot
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'Mensagem não fornecida'}), 400

    # Chama a função para extrair o nome da cidade, usando "Pelotas" como cidade padrão
    city = extract_city_from_input(user_input)
    
    # Se a entrada mencionar uma cidade, obtém a previsão do tempo
    if city:
        weather_data = get_weather(city)
        return app.response_class(
            response=json.dumps(weather_data, ensure_ascii=False, indent=4),  # Retorna a previsão do tempo
            status=200,
            mimetype='application/json'
        )

    # Se não foi detectada uma cidade, chama o modelo Gemini
    gemini_response = get_gemini_response(user_input)

    return jsonify({'response': gemini_response})

# Roda a aplicação
if __name__ == '__main__':
    app.run(debug=True)
