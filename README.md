# OrchestratorAgent
## An application designed for remote communication with the Orchestrator through querying its API and performing operations on bots (subprocesses) on the machine where the Agent is located.

### To install and run the application, follow these steps: 
1. **Clone the repository**: Download the source code from GitHub and navigate to the project directory.
2. **Create and activate a virtual environment**: Isolates the project's dependencies to avoid conflicts with other projects.
3. **Install the required packages**: Use `pip` to install all dependencies listed in the `requirements.txt` file.
```sh
pip install -r requirements.txt
```

### Through the configuration file, it is essential to adjust the necessary paths for the bot to function properly:

  - "bot_venv_path" - path for virtual environment for bots on the machine
  - "bot_path" - path for bot executable files
  - "temp_path" - path for temporary file downloads

  and other optional program configurations.
