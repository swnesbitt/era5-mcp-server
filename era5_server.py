import os
import cdsapi
import xarray as xr
from pathlib import Path
from fastmcp import FastMCP
import asyncio
import time
from typing import Union, List

# --- MCP Server Setup ---
mcp = FastMCP(name="ERA5 Climate Data Server")

# --- Internal Core Logic ---
# These functions contain the actual logic and can be imported for testing.

async def _internal_inspect_netcdf(filepath: str) -> str:
    """
    (Internal) Inspects a NetCDF file and returns a summary.
    """
    def _sync_inspect():
        if not Path(filepath).exists():
            return f"Error: File not found at '{filepath}'"
        try:
            with xr.open_dataset(filepath) as ds:
                summary = [f"--- NetCDF Inspection Summary for {Path(filepath).name} ---", "\n[Dimensions]"]
                summary.extend(f"- {dim}: {size}" for dim, size in ds.dims.items())
                summary.append("\n[Coordinates]")
                summary.extend(f"- {name} ({c.dims}): {c.attrs.get('long_name', '')} [{c.attrs.get('units', '')}]" for name, c in ds.coords.items())
                summary.append("\n[Variables]")
                summary.extend(f"- {name} ({v.dims}): {v.attrs.get('long_name', '')} [{v.attrs.get('units', '')}]" for name, v in ds.data_vars.items())
                summary.append("\n--- End of Summary ---")
                return "\n".join(summary)
        except Exception as e:
            return f"Error inspecting NetCDF file: {e}"

    loop = asyncio.get_running_loop()
    summary = await loop.run_in_executor(None, _sync_inspect)
    return summary

async def _internal_fetch_and_inspect(dataset: str, request: dict, output_filename: str) -> str:
    """
    (Internal) Generic ERA5 data fetching and inspection logic.
    """
    output_path = Path(output_filename).resolve()

    def _blocking_download():
        print("[DEBUG] Entering blocking download function.")
        try:
            print("[DEBUG] Initializing cdsapi.Client...")
            c = cdsapi.Client()
            print("[DEBUG] CDS API Client initialized.")
            
            print(f"[DEBUG] Starting download for dataset '{dataset}' to '{output_path}'. This may take a while...")
            start_time = time.time()
            c.retrieve(dataset, request, str(output_path))
            end_time = time.time()
            print(f"[DEBUG] Download completed in {end_time - start_time:.2f} seconds.")

            print("[DEBUG] Starting file inspection...")
            inspection_summary = asyncio.run(_internal_inspect_netcdf(str(output_path)))
            print("[DEBUG] File inspection complete.")
            
            return f"Successfully downloaded data to '{output_path}'.\n\n{inspection_summary}"
        except Exception as e:
            error_message = f"Error during CDS API request: {str(e)}."
            print(f"[DEBUG] {error_message}")
            return error_message

    loop = asyncio.get_running_loop()
    result_message = await loop.run_in_executor(None, _blocking_download)
    return result_message

async def _internal_fetch_era5_pressure_levels(variable: str, pressure_level: int, year: Union[str, List[str]], month: str, output_filename: str) -> str:
    request = {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': variable,
        'pressure_level': str(pressure_level),
        'year': year,
        'month': month,
        'time': '00:00',
        'data_format': 'netcdf',
    }
    return await _internal_fetch_and_inspect('reanalysis-era5-pressure-levels-monthly-means', request, output_filename)

async def _internal_fetch_era5_single_levels(variable: str, year: str, month: str, output_filename: str) -> str:
    request = {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': variable,
        'year': year,
        'month': month,
        'time': '00:00',
        'data_format': 'netcdf',
    }
    return await _internal_fetch_and_inspect('reanalysis-era5-single-levels-monthly-means', output_filename)

# --- MCP Tool Definitions ---
@mcp.tool
async def inspect_netcdf(filepath: str) -> str:
    """
    Inspects a NetCDF file and returns a summary of its contents (dimensions, variables, coordinates).
    
    :param filepath: The absolute path to the .nc file to inspect.
    """
    return await _internal_inspect_netcdf(filepath)

@mcp.tool
async def fetch_era5_pressure_levels(variable: str, pressure_level: int, year: Union[str, List[str]], month: str, output_filename: str) -> str:
    """
    Downloads ERA5 monthly mean data on specific pressure levels for a given month across one or more years.
    
    :param variable: The variable to download (e.g., 'geopotential', 'temperature').
    :param pressure_level: The pressure level in hPa (e.g., 500, 850, 1000).
    :param year: The year(s) for the data (e.g., '2023' or ['2021', '2022', '2023']).
    :param month: The month for the data (e.g., '01', '12').
    :param output_filename: The local filename for the downloaded data (e.g., 'data/geopotential_500hpa_multi_year.nc').
    """
    return await _internal_fetch_era5_pressure_levels(variable, pressure_level, year, month, output_filename)

@mcp.tool
async def fetch_era5_single_levels(variable: str, year: str, month: str, output_filename: str) -> str:
    """
    Downloads ERA5 monthly mean surface data.
    
    :param variable: The surface variable to download (e.g., '2m_temperature').
    :param year: The year for the data (e.g., '2023').
    :param month: The month for the data (e.g., '01', '12').
    :param output_filename: The local filename for the downloaded data (e.g., 'data/2m_temp_2023_01.nc').
    """
    return await _internal_fetch_era5_single_levels(variable, year, month, output_filename)

# --- Main Execution ---
if __name__ == "__main__":
    mcp.run()