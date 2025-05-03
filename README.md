# Project Setup and Requirements

## Installation Options

### 1. System Python + Poetry

If you prefer using your system's Python installation:

1. Ensure you have Python installed on your system (Requires version: 3.12.10).

    - Verify installation with:

        ```bash
        python --version
        ```

    - If not installed, follow the [Python installation guide](https://www.python.org/downloads/).

2. Install Poetry:

    - [Poetry installation guide](https://python-poetry.org/docs/)
    - Run Poetry installation command from their official site

3. Configure Poetry:

    ```bash
    # Set virtual environment to be in project (required for Jupyter notebooks)
    poetry config virtualenvs.in-project true

    # Initialize Poetry in the project
    poetry install
    ```

### 2. Conda + Poetry (Recommended)

For a more isolated environment with better dependency management:

1. Install Miniconda:

    - [Miniconda installation guide](https://www.anaconda.com/docs/getting-started/miniconda/install)
    - [Miniconda installation download link](https://www.anaconda.com/download)
    - Verify installation with:

        ```bash
        conda --version
        ```

        If conda is not recognized, add **C:\Users\YourUsername\miniconda3\Scripts** to your PATH.

    - Update conda to the latest version:

        ```bash
        conda update conda
        ```

    - If you use git bash as your terminal, you need to run this command in cmd or powershell:

        ```bash
        conda init bash
        ```

2. Configure conda to use conda-forge channel:

    ```bash
    # Add conda-forge as the priority channel
    conda config --add channels conda-forge
    conda config --set channel_priority strict

    # Verify your .condarc file configuration
    # On Windows: %USERPROFILE%\.condarc
    # On Linux/MacOS: ~/.condarc
    ```

    Check channel priority with:

    ```bash
    conda config --get channels
    ```

3. Disable (base) environment auto-activation:

    ```bash
    # Disable auto-activation of the base environment
    conda config --set auto_activate_base false
    ```

4. Create and configure environment:

    ```bash
    # Create conda environment from configuration file
    conda env create -f environment.yml

    # Activate the conda environment
    conda activate BachelorProject_Babiar
    ```

5. Configure Poetry with Conda:

    ```bash
    # Configure Poetry to use Conda's environment path

    # Get the path to the conda environment
    conda info --envs

    # You will see something like this:
    # # conda environments:
    # #
    # base                      C:\Users\<YouUsername>\miniconda3
    # BachelorProject_Babiar *  C:\Users\<YouUsername>\miniconda3\envs\BachelorProject_Babiar

    # The path in this case is C:\Users\<YouUsername>\miniconda3\envs
    # For Windows use "\\" instead of "\"
    # The final command should look like this:
    poetry config virtualenvs.path C:\\Users\\<YouUsername>\\miniconda3\\envs

    # Check if the path is set correctly
    poetry config --list | grep virtualenvs.path

    # Prevent Poetry from creating separate virtual environments
    poetry config virtualenvs.create false

    # Install project dependencies
    poetry install
    ```

## Package Management Commands

### Poetry Commands

-   `poetry config --list` - Display all configuration options
-   `poetry install` - Install project dependencies
-   `poetry update` - Update project dependencies
-   `poetry add <package>` - Add a package to the project
-   `poetry remove <package>` - Remove a package from the project

## Docker Setup

### Docker Commands

-   **Reset and run in foreground**:
    ```bash
    docker-compose down -v && docker-compose up --build
    ```
-   **Reset and run in background (detached mode)**:
    ```bash
    docker-compose down -v && docker-compose up -d --build
    ```
-   **Reset and run with database initialization (foreground)**:
    ```bash
    docker-compose down && docker-compose up --build && docker rm -f catbase_postgres_original_db_init || true
    ```
-   **Reset and run with database initialization (background)**:
    ```bash
    docker-compose down && docker-compose up -d --build && docker rm -f catbase_postgres_original_db_init || true
    ```

## Troubleshooting

### Neo4j Heap Memory Error

If you encounter this error:

```
{code: Neo.TransientError.General.OutOfMemoryError} {message: There is not enough memory to perform the current task. Please try increasing 'server.memory.heap.max_size' in the neo4j configuration (normally in 'conf/neo4j.conf' or, if you are using Neo4j Desktop, found through the user interface) or if you are running an embedded installation increase the heap by using '-Xmx' command line flag, and then restart the database.}
```

**Solution**: Lower the **batch_size** in `src/util/config.json` under `graph_database->batch_size` to reduce memory consumption during data processing.
