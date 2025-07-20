# Tatlin Unified Assistant

Интеллектуальный агент для ответов на вопросы по документации Tatlin Unified на основе RAG-архитектуры.

## Особенности

- 💬 Чат-интерфейс с поддержкой Markdown
- 🧠 Интеграция с Langflow и LLM
- ⭐ Система оценки ответов (лайки/дизлайки)
- 📥 Экспорт диалогов в Markdown
- 📱 Адаптивный дизайн
- ❔ Примеры вопросов для адаптации пользователя

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/lokke174/Neimark-hackathon.git
   cd Neimark-hackathon
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте файл .env со следующим содержимым:
    ```text
   API_KEY=your-langflow-api-key
   LANGFLOW_ENDPOINT=http://your-langflow-endpoint
   ```

4. Инициализируйте базу данных:
    ```bash
   python -c "from database import init_db; init_db()"
   ```

5. Запустите приложение:
   ```bash
   python app.py
   ```