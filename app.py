# app.py
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session
import requests
import json
import uuid
import time
from datetime import datetime
from database import init_db, add_chat, add_message, update_feedback, get_chat_history, get_chat_id_by_session

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_KEY = os.getenv('API_KEY')
LANGFLOW_ENDPOINT = os.getenv('LANGFLOW_ENDPOINT')
if not all([API_KEY, LANGFLOW_ENDPOINT]):
    print(
        "Для запуска проекта вы должны указать переменные окружения:\nAPI_KEY - ключ для взаимодействия с LLM\nLANGFLOW_ENDPOINT - эндпойнт для взаимодействия с LLM")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

# Инициализация базы данных
init_db()


@app.get('/chat')
def chat():
    # Создаем новую сессию, если нет
    if 'session_id' not in session:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        # Создаем новый чат в БД
        chat_id = add_chat(session_id)
        session['chat_id'] = chat_id
    else:
        # Получаем chat_id из БД
        session_id = session['session_id']
        chat_id = get_chat_id_by_session(session_id)
        if not chat_id:
            chat_id = add_chat(session_id)
        session['chat_id'] = chat_id

    return render_template('index.html')


@app.post('/chat')
def chat_proxy():
    user_input = request.json.get('message')
    session_id = session.get('session_id')
    chat_id = session.get('chat_id')

    if not session_id or not chat_id:
        return jsonify({"error": "Session not initialized"}), 400

    # Сохраняем сообщение пользователя в БД
    user_message_id = add_message(chat_id, 'user', user_input)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "input_value": user_input,
        "input_type": 'chat',
        "output_type": "chat",
        "session_id": session_id
    }

    try:
        start_time = time.time()
        response = requests.post(
            LANGFLOW_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        # Обновленная логика парсинга ответа
        try:
            # Попытка извлечь данные из новой структуры ответа
            message_data = result['outputs'][0]['outputs'][0]['results']['message']
            answer = message_data['text']
            sources = message_data['properties'].get('sources', [])
        except KeyError:
            # Фолбэк на старую структуру
            answer = result.get('message', {}).get('text', '')
            sources = result.get('message', {}).get('properties', {}).get('sources', [])

        # Рассчет времени ответа
        response_time = round(time.time() - start_time, 2)

        # Сохраняем ответ бота в БД
        bot_message_id = add_message(
            chat_id,
            'bot',
            answer,
            sources,
            response_time
        )

        return jsonify({
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "response_time": response_time,
            "message_id": bot_message_id
        })
    except Exception as e:
        app.logger.error(f"Error in chat_proxy: {str(e)}")
        return jsonify({"error": "Произошла ошибка при обработке запроса. Попробуйте еще раз."}), 500


@app.post('/feedback')
def handle_feedback():
    data = request.json
    message_id = data.get('message_id')
    feedback_type = data.get('type')

    if not message_id:
        return jsonify({"error": "Message ID not provided"}), 400

    try:
        update_feedback(message_id, feedback_type)
        return jsonify({
            "status": "success",
            "message": "Спасибо за ваш отзыв!"
        })
    except Exception as e:
        app.logger.error(f"Error updating feedback: {str(e)}")
        return jsonify({"error": "Ошибка при обработке отзыва"}), 500


@app.get('/history')
def get_history():
    chat_id = session.get('chat_id')
    if not chat_id:
        return jsonify([])

    history = get_chat_history(chat_id)
    return jsonify(history)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
