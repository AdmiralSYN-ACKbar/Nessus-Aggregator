# Nessus Aggregator

Nessus Aggregator is a Python-based tool that automates aggregation of Nessus vulnerability scan results into consolidated Excel reports. The config.py script generates a run file that can be automated through crontab. This tool utilizes and builds upon [LimberDuck's Nessus File Reader](https://github.com/LimberDuck/nessus-file-reader). If you're looking for another powerful GUI-based solution for Nessus file aggregation, check out [LimberDuck's Nessus File Analyzer](https://github.com/LimberDuck/nessus-file-analyzer).

![Nessus Aggregator Interface](https://github.com/AdmiralSYN-ACKbar/Nessus-Aggregator/blob/main/screenshots/program_execution.png?raw=true)


## Prerequisites

- Python 3.7 or higher
- `python3-venv` / `python3-pip` (install with apt if needed) 
- Linux operating system
- Nessus Essentials, Professional, or Expert
- API keys from your Nessus instance [(see API key generation documentation)](https://docs.tenable.com/nessus/Content/GenerateAnAPIKey.htm)

## Installation

1. Ensure all prerequisites are met.
2. Create and activate a virtual environment: 
`python-3 -m venv environment_name`  
`source environment_name/bin/activate`
3. Install with `pip install nessus-aggregator`

# Program Execution
1. Run `nessus-aggregator` 
2. Fill out the fields in the GUI and click "ENGAGE".
3. Run the generated `run_nessus_aggregator.sh` or click the “Execute Run Script” button in the GUI to generate the report.

## Automation
- The `run_nessus_aggregator.sh` script can be scheduled via cron.

![CLI Output](https://github.com/AdmiralSYN-ACKbar/Nessus-Aggregator/blob/main/screenshots/run_script_output.png?raw=true)


## How It Works

- **API Authentication**: Uses Nessus API keys to connect to Nessus.
- **Scan Collection**: Retrieves all scans from the current calendar month or from a previous user-defined number of days.
- **Report Generation**: Processes scans and generates an Excel file with 3 tabs:
  - **Scan Information**: Overview of each scan.
  - **Vulnerability Summary**: Summary of hosts and findings by severity.
  - **Vulnerability Details**: Detailed findings with links to Tenable's plugin database.
 
## Security Notes

- API keys are stored in `~/.nessus_env` with restricted permissions (`chmod 600`). Your Nessus API keys are stored in this file. **Delete it after running if you do not want this to be stored.**
- SSL certificate verification is disabled by default due to common use of self-signed certificates.
- Downloads of scan files created through API calls are automatically deleted after processing.

## Output Format

The generated Excel report includes:
- Scan metadata
- Vulnerability summary by host and severity (Critical, High, Medium and Low only)
- Detailed findings with clickable plugin IDs

 ![Report Tab 1](https://github.com/AdmiralSYN-ACKbar/Nessus-Aggregator/blob/main/screenshots/report1.png?raw=true)
 ![Report Tab 2](https://github.com/AdmiralSYN-ACKbar/Nessus-Aggregator/blob/main/screenshots/report2.png?raw=true)
 ![Report Tab 3](https://github.com/AdmiralSYN-ACKbar/Nessus-Aggregator/blob/main/screenshots/report3.png?raw=true)

