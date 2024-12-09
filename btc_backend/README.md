# BTC-Conversa: Conversational AI Banking Assistant

BTC-Conversa is a conversational AI banking assistant built using [Rasa](https://rasa.com/). This assistant aims to provide users with a complete banking experience through simple, natural conversations. This README file will guide you through setting up, training, and running the project locally.

## Prerequisites

- Python 3.7+
- Rasa 3.0+
- Docker

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/voiceofarsalan/BTC-Conversa.git
   cd BTC-Conversa
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

3. Install Rasa and the necessary dependencies:

   ```bash
   pip install rasa
   pip install -r requirements.txt
   ```

### Duckling Entity Extractor

BTC-Conversa uses Rasa's Duckling entity extractor for handling dates, times, and numbers. To set up Duckling using Docker, run the following commands:

1. Pull the Duckling image:
   
   ```bash
   docker pull rasa/duckling
   ```

2. Run Duckling:

   ```bash
   docker run -p 8000:8000 rasa/duckling
   ```

### Training the Model

To train the Rasa model, use the following command:

```bash
rasa train
```

This command will create a new model under the `models` directory.

### Running the Rasa Action Server

Your assistant might require custom actions to interact with external services or databases. To run the action server, use the following command:

```bash
rasa run actions
```

This will start the action server which listens for custom actions defined in `actions.py`.

### Running the Assistant

To start the assistant, use the following command:

```bash
rasa run --endpoints endpoints.yml --cors "*"
```

The assistant will be accessible on `http://localhost:5005`, and CORS is enabled to allow requests from all origins.

## Project Commands Overview

- **Train the model**:
  ```bash
  rasa train
  ```
- **Run the action server**:
  ```bash
  rasa run actions
  ```
- **Run the Rasa assistant**:
  ```bash
  rasa run --endpoints endpoints.yml --cors "*"
  ```
- **Run Duckling for entity extraction**:
  ```bash
  docker pull rasa/duckling
  docker run -p 8000:8000 rasa/duckling
