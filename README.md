# ERA5 Climate Data MCP Server

This project provides a ready-to-run MCP (Model Context Protocol) server that interfaces with the Copernicus Climate Data Store (CDS). It allows you to use natural language in an AI assistant (like Gemini CLI or Claude Desktop) to fetch and inspect ERA5 climate data.

## Features

- **Easy Data Download**: Fetch monthly-averaged ERA5 data for both single levels (e.g., surface temperature) and pressure levels (e.g., geopotential height at 500hPa).
- **Multi-Year Fetching**: Download data for the same month across multiple years in a single request.
- **Data Inspection**: Quickly inspect the contents (dimensions, coordinates, variables) of any downloaded NetCDF file.

---

## 1. Setup Copernicus API Key

Before using the server, you must have a Copernicus account and an API key.

1.  **Register**: Create an account on the [CDS Website](https://cds.climate.copernicus.eu/).
2.  **Get Key**: Log in and find your API key at the bottom of your user profile page (e.g., `https://cds.climate.copernicus.eu/user/YOUR_USER_ID`).
3.  **Create `.cdsapirc` file**: Create a file named `.cdsapirc` in your home directory (`~/.cdsapirc` on Linux/macOS, `C:\Users\YourUser\.cdsapirc` on Windows).
4.  **Add Credentials**: Add your API key to the file in the following format, replacing `YOUR_UID` and `YOUR_API_KEY` with your actual values:
    ```
    url: https://cds.climate.copernicus.eu/api/v2
    key: YOUR_UID:YOUR_API_KEY
    ```
5.  **Accept Terms**: For each dataset you want to access (`reanalysis-era5-single-levels-monthly-means` and `reanalysis-era5-pressure-levels-monthly-means`), you must visit its page on the CDS website and accept the terms of use manually. The server cannot do this for you.

---

## 2. Installation

A `requirements.txt` file is provided to install all necessary dependencies.

```bash
# Create and activate a Python virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# .\venv\Scripts\activate  # On Windows

# Install the required packages
pip install -r requirements.txt
```

---

## 3. Available Tools

This server exposes the following tools to your AI assistant:

### `fetch_era5_single_levels`
Downloads ERA5 monthly mean surface data.

- **Parameters**:
    - `variable` (str): The surface variable to download (e.g., `'2m_temperature'`).
    - `year` (str): The year for the data (e.g., `'2023'`).
    - `month` (str): The month for the data (e.g., `'01'`, `'12'`).
    - `output_filename` (str): The local path to save the file (e.g., `'data/2m_temp_2023_01.nc'`).

### `fetch_era5_pressure_levels`
Downloads ERA5 monthly mean data on specific pressure levels.

- **Parameters**:
    - `variable` (str): The variable to download (e.g., `'geopotential'`, `'temperature'`).
    - `pressure_level` (int): The pressure level in hPa (e.g., `500`, `850`).
    - `year` (str or list[str]): The year(s) for the data. Can be a single year (`'2023'`) or a list of years for multi-year downloads (`['2020', '2021', '2022']`).
    - `month` (str): The month for the data (e.g., `'03'`).
    - `output_filename` (str): The local path to save the file.

### `inspect_netcdf`
Inspects a NetCDF file and returns a summary of its contents.

- **Parameters**:
    - `filepath` (str): The absolute path to the `.nc` file to inspect.

---

## 4. Running the Server

Once installed, you can run the MCP server directly from your terminal. This will make the tools available to your connected AI assistant.

```bash
python era5_server.py
```

To add the server to your assistant permanently:
- **Gemini CLI:** `gemini tools add era5_server.py`
- **Other MCP-compatible clients**: Follow their instructions for adding a local tool server.

---

## 5. Testing the Server

A Jupyter notebook, `test_server.ipynb`, is provided to test the server's functionality directly from a Python environment.

1.  **Install Jupyter**: If you don't have it, install Jupyter Lab:
    ```bash
    pip install jupyterlab
    ```

2.  **Run the Notebook**: Start Jupyter Lab and open `test_server.ipynb`:
    ```bash
    jupyter lab
    ```

3.  **Execute Cells**: Follow the instructions in the notebook to run the cells. They will guide you through installing dependencies, setting a cache directory, and testing single-year, multi-year, and inspection tools.