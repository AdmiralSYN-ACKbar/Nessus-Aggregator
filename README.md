# Nessus Aggregator

Nessus Aggregator is a Python-based tool that automates aggregation of Nessus vulnerability scan results into consolidated Excel reports. The setup.py script generates a run file that can be automated through crontab. This tool utilizes and builds upon [LimberDuck's Nessus File Reader](https://github.com/LimberDuck/nessus-file-reader). If you're looking for another powerful GUI-based solution for Nessus file aggregation, check out [LimberDuck's Nessus File Analyzer](https://github.com/LimberDuck/nessus-file-analyzer).

## Prerequisites

- Python 3.7 or higher
- `python3-venv` / `python3-pip` (install with apt if needed)
- Linux operating system
- Nessus Professional, Essentials, or Expert (required for API access)
- API access keys from your Nessus installation

## Installation

1. Ensure all system requirements are met.
2. Run `setup.py` with Python and fill out the fields in the GUI. 
3. A virtual environment with the necessary Python modules and a `run_nessus_aggregator.sh` script will be generated.
4. Run the `run_nessus_aggregator.sh` or click the “Execute Run Script” button in the GUI to generate the report.

## Automation
- The `run_nessus_aggregator.sh` script can be scheduled via cron

## How It Works

- **API Authentication**: Uses Nessus API keys to connect to Nessus.
- **Scan Collection**: Retrieves all scans from the current calendar month or from a previous user-defined number of days.
- **Report Generation**: Processes scans and generates an Excel file with 3 tabs:
  - **Scan Information**: Overview of each scan.
  - **Vulnerability Summary**: Summary of hosts and findings by severity.
  - **Vulnerability Details**: Detailed findings with links to Tenable's plugin database.

## Output Format

The generated Excel report includes:
- Scan metadata (name, targets, timing)
- Vulnerability counts by severity (Critical, High, Medium, Low)
- Detailed findings with clickable plugin IDs
- Host operating system information
- Automatic totals and formatting

## Security Notes

- API keys are stored in `~/.nessus_env` with restricted permissions (`chmod 600`).
- SSL certificate verification is disabled by default due to common use of self-signed certificates.
- Scan files are automatically cleaned up after processing.
- Environment variables are secured in the user's home directory.

## Additional Information

This tool is based on LimberDuck’s Nessus File Reader and was created to aggregate Nessus scans in an automated fashion. Scans can be done manually as well. We recommend users check out Nessus File Analyzer by LimberDuck for a GUI-based solution for analyzing individual Nessus files.

The script creates a file at `~/.nessus_env` that includes the Nessus API keys and runs `chmod 600` on it. Your Nessus API keys are stored in this file. Delete it after running if you do not want this to be stored.