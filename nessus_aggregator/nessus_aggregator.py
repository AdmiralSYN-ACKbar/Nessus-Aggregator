import os
import requests
import urllib3
from datetime import datetime, date, timedelta
import pandas as pd
from pathlib import Path
import shutil
import nessus_file_reader as nfr
import ipaddress

# Monkey patch the ip_range_split function
def new_ip_range_split(ip_range):
    ip_network_hosts = ipaddress.ip_network(ip_range, strict=False).hosts()
    return [str(ip) for ip in ip_network_hosts]

nfr.utilities.ip_range_split = new_ip_range_split

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_scans(download_dir):
    access_key = os.getenv("NESSUS_ACCESS_KEY")
    secret_key = os.getenv("NESSUS_SECRET_KEY")
    nessus_url = os.getenv("NESSUS_URL")
    scan_type = os.getenv("NESSUS_SCAN_TYPE", "current_month")
    days_back = int(os.getenv("NESSUS_DAYS_BACK", "0"))
    
    headers = {'Content-Type': 'application/json','X-ApiKeys': f'accessKey={access_key};secretKey={secret_key}'}
    
    today = date.today()
    if scan_type == "current_month":
        start_date = date(today.year, today.month, 1)
    else:
        start_date = today - timedelta(days=days_back)
    
    try:
        response = requests.get(f'{nessus_url}/scans', headers=headers, verify=False)
        
        if response.status_code == 200:
            scans = response.json()['scans']
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
                
            for scan in scans:
                scan_date = date.fromtimestamp(scan['last_modification_date'])
                if scan_date >= start_date:
                    scan_id = scan['id']
                    export_response = requests.post(
                        f'{nessus_url}/scans/{scan_id}/export',
                        headers=headers,
                        json={'format': 'nessus'},
                        verify=False
                    )
                    
                    if export_response.status_code == 200:
                        file_id = export_response.json()['file']
                        while True:
                            status_response = requests.get(
                                f'{nessus_url}/scans/{scan_id}/export/{file_id}/status',
                                headers=headers,
                                verify=False
                            )
                            
                            if status_response.json()['status'] == 'ready':
                                download_response = requests.get(
                                    f'{nessus_url}/scans/{scan_id}/export/{file_id}/download',
                                    headers=headers,
                                    verify=False
                                )
                                
                                scan_name = sanitize_filename(scan['name'])
                                scan_date_str = scan_date.strftime('%Y%m%d')
                                filename = f"{scan_date_str}_{scan_name}.nessus"
                                filepath = os.path.join(download_dir, filename)
                                
                                with open(filepath, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"Downloaded: {filename}")
                                break
    except Exception as e:
        print(f"Error downloading scans: {str(e)}")

def process_nessus_directory(scan_dir, output_file):
    scan_info_data = []
    vulnerability_summary = []
    vulnerability_details = []
    
    for filename in os.listdir(scan_dir):
        if filename.endswith('.nessus'):
            nessus_file = os.path.join(scan_dir, filename)
            root = nfr.file.nessus_scan_file_root_element(nessus_file)
            
            scan_info = {
                'Scan Name': nfr.scan.report_name(root),
                'Target Hosts': nfr.scan.number_of_target_hosts(root),
                'Scanned Hosts': nfr.scan.number_of_scanned_hosts(root),
                'Credentialed Hosts': nfr.scan.number_of_scanned_hosts_with_credentialed_checks_yes(root),
                'Scan Start': nfr.scan.scan_time_start(root),
                'Scan End': nfr.scan.scan_time_end(root),
                'Scan Duration': nfr.scan.scan_time_elapsed(root)
            }
            
            scan_info_data.append(scan_info)
            
            for report_host in nfr.scan.report_hosts(root):
                hostname = nfr.host.report_host_name(report_host)
                detected_os = nfr.host.detected_os(report_host)
                if detected_os:
                    detected_os = detected_os.split('\n')[0]
                    
                summary = {
                    'Hostname': hostname,
                    'Operating System': detected_os,
                    'Critical': nfr.host.number_of_plugins_per_risk_factor(report_host, 'Critical'),
                    'High': nfr.host.number_of_plugins_per_risk_factor(report_host, 'High'),
                    'Medium': nfr.host.number_of_plugins_per_risk_factor(report_host, 'Medium'),
                    'Low': nfr.host.number_of_plugins_per_risk_factor(report_host, 'Low')
                }
                
                vulnerability_summary.append(summary)
                
                report_items = nfr.host.report_items(report_host)
                for report_item in report_items:
                    risk_factor = nfr.plugin.report_item_value(report_item, 'risk_factor')
                    if risk_factor in ['Low', 'Medium', 'High', 'Critical']:
                        plugin_id = nfr.plugin.report_item_value(report_item, 'pluginID')
                        plugin_name = nfr.plugin.report_item_value(report_item, 'pluginName')
                        vuln_detail = {
                            'Hostname': hostname,
                            'Plugin ID': f'=HYPERLINK("https://www.tenable.com/plugins/nessus/{plugin_id}","{plugin_id}")',
                            'Severity': risk_factor,
                            'Plugin Name': plugin_name
                        }
                        vulnerability_details.append(vuln_detail)
    
    scan_info_df = pd.DataFrame(scan_info_data)
    vulnerability_summary_df = pd.DataFrame(vulnerability_summary)
    vulnerability_details_df = pd.DataFrame(vulnerability_details)
    
    vulnerability_summary_df = vulnerability_summary_df.groupby('Hostname').agg({
        'Operating System': 'first',
        'Critical': 'max',
        'High': 'max',
        'Medium': 'max',
        'Low': 'max'
    }).reset_index()
    
    totals = {
        'Hostname': 'TOTAL',
        'Operating System': '',
        'Critical': vulnerability_summary_df['Critical'].sum(),
        'High': vulnerability_summary_df['High'].sum(),
        'Medium': vulnerability_summary_df['Medium'].sum(),
        'Low': vulnerability_summary_df['Low'].sum()
    }
    
    empty_row = {col: '' for col in vulnerability_summary_df.columns}
    vulnerability_summary_df = pd.concat([
        vulnerability_summary_df,
        pd.DataFrame([empty_row]),
        pd.DataFrame([totals])
    ], ignore_index=True)
    
    vulnerability_details_df = vulnerability_details_df.drop_duplicates(
        subset=['Hostname', 'Plugin ID', 'Plugin Name'],
        keep='first'
    )
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        scan_info_df.to_excel(writer, sheet_name='Scan Information', index=False)
        vulnerability_summary_df.to_excel(writer, sheet_name='Vulnerability Summary', index=False)
        vulnerability_details_df.to_excel(writer, sheet_name='Vulnerability Details', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Vulnerability Details']
        link_format = workbook.add_format({'color': 'blue', 'underline': True})
        worksheet.set_column('B:B', None, link_format)
        
        worksheet = writer.sheets['Vulnerability Summary']
        bold_format = workbook.add_format({'bold': True})
        last_row = len(vulnerability_summary_df)
        worksheet.set_row(last_row - 1, None, bold_format)

def cleanup_scan_files(scan_dir):
    try:
        shutil.rmtree(scan_dir)
    except Exception as e:
        print(f"Error cleaning up scan files: {str(e)}")

if __name__ == "__main__":
    output_dir = os.getenv("NESSUS_OUTPUT_DIR", os.path.expanduser("~/nessus_output"))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    scan_dir = os.path.join(output_dir, 'temp_scans')
    output_file = os.path.join(output_dir, f'vulnerability_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    
    print("Downloading scans...")
    download_scans(scan_dir)
    
    print("\nProcessing downloaded scans...")
    process_nessus_directory(scan_dir, output_file)
    
    print("\nCleaning up scan files...")
    cleanup_scan_files(scan_dir)
    
    print(f"\nComplete! Results saved to: {output_file}")