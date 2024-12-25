# Telegram Bot Framework with Dynamic Updates and Plugin System

This project implements a flexible Telegram bot framework with dynamic updates and a plugin system. It provides a robust foundation for building and maintaining Telegram bots with modular functionality.

The framework consists of a main bot application, an update system for keeping the bot code current, and a plugin architecture for extending bot capabilities. Key features include:

- Asynchronous bot implementation using the aiogram library
- Automatic or manual updates from a GitHub repository 
- Dynamic loading of handlers and plugins
- Configurable database backend (local JSON, MongoDB, MySQL, PostgreSQL)
- Logging and web view services

The modular design allows developers to easily add new commands and features by creating plugins, while the update system enables seamless deployment of changes and improvements.

## Repository Structure

```
.
├── __main__.py
├── config_reader.py  
├── README.md
├── req_gen.py
└── update.py
```

- `__main__.py`: Entry point for the bot application
- `update.py`: Handles automatic/manual updates from GitHub
- `req_gen.py`: Generates requirements.txt file
- `config_reader.py`: Reads configuration settings

## Usage Instructions

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/telegram-bot-framework.git
   cd telegram-bot-framework
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up configuration:
   - Create a `config.json` file with your bot token and other settings
   - Create a `.env` file with your `BOT_TOKEN`

### Running the Bot

To start the bot:

```
python __main__.py
```

This will initialize services, load handlers and plugins, and start the bot polling loop.

### Updating the Bot

For automatic updates:
1. Set `"update_mode": "auto"` in `config.json`
2. Run `python update.py`

For manual updates:
1. Set `"update_mode": "manual"` in `config.json` 
2. Run `python update.py`
3. When prompted, run the manual update command

### Adding Plugins

To create a new plugin:
1. Create a new Python file in the `plugins` directory
2. Implement the plugin logic using the aiogram framework
3. The plugin will be automatically loaded on bot startup

### Configuration

Key configuration options in `config.json`:
- `admin_id`: Telegram user ID of the bot administrator
- `database`: Database configuration (type, connection details)
- `update_mode`: "auto" or "manual"

## Data Flow

1. User sends message to Telegram
2. Telegram forwards message to bot via webhook or long polling
3. `__main__.py` receives update and passes to appropriate handler
4. Handler processes message, potentially using plugins
5. Response is sent back to Telegram
6. Telegram delivers response to user

```
User <-> Telegram <-> Bot (__main__.py) <-> Handlers <-> Plugins
                           ^
                           |
                        Database
```

## Deployment

1. Set up a server with Python 3.7+
2. Clone the repository and install dependencies
3. Configure the bot token and other settings
4. Set up a process manager (e.g., systemd, supervisor) to keep the bot running
5. (Optional) Configure a reverse proxy for the web view service

## Infrastructure

The project does not have a dedicated infrastructure stack defined in the provided code. It is designed to run as a standalone Python application, with the option to use various database backends as configured.