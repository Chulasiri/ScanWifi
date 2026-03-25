import subprocess
import json
import platform
import re
import os
import socket
import urllib.request
import time

def get_windows_wifi():
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            if 'SSID' in line and 'BSSID' not in line:
                if current_network:
                    networks.append(current_network)
                ssid = line.split(':')[1].strip() if ':' in line else ''
                current_network = {'ssid': ssid, 'bssid': '', 'signal': 0, 'channel': '', 'security': '', 'auth': ''}
            
            elif 'BSSID' in line:
                bssid = line.split(':')[1].strip() if ':' in line else ''
                current_network['bssid'] = bssid
            
            elif 'Signal' in line:
                try:
                    signal = line.split(':')[1].strip().replace('%', '')
                    current_network['signal'] = int(signal)
                except:
                    pass
            
            elif 'Channel' in line:
                try:
                    channel = line.split(':')[1].strip()
                    current_network['channel'] = channel
                except:
                    pass
            
            elif 'Authentication' in line:
                auth = line.split(':')[1].strip() if ':' in line else ''
                current_network['auth'] = auth
            
            elif 'Cipher' in line:
                cipher = line.split(':')[1].strip() if ':' in line else ''
                current_network['security'] = cipher
        
        if current_network and current_network.get('ssid'):
            networks.append(current_network)
        
        return networks
    except Exception as e:
        return {'error': str(e)}

def get_linux_wifi():
    try:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,CHAN,FREQ', 'device', 'wifi', 'list', '--rescan', 'yes'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        networks = []
        for line in result.stdout.split('\n'):
            if line.strip():
                parts = line.split(':')
                if len(parts) >= 2:
                    ssid = parts[0]
                    signal = int(parts[1]) if parts[1].isdigit() else 0
                    security = parts[2] if len(parts) > 2 else ''
                    channel = parts[3] if len(parts) > 3 else ''
                    freq = parts[4] if len(parts) > 4 else ''
                    
                    if ssid:
                        networks.append({
                            'ssid': ssid,
                            'bssid': '',
                            'signal': signal,
                            'channel': channel,
                            'security': security,
                            'auth': security
                        })
        
        return networks
    except Exception as e:
        try:
            result = subprocess.run(
                ['iwlist', 'scan'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            networks = []
            current = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Cell ' in line:
                    if current.get('ssid'):
                        networks.append(current)
                    current = {'bssid': '', 'ssid': '', 'signal': 0, 'channel': '', 'security': '', 'auth': ''}
                
                elif 'Address:' in line:
                    current['bssid'] = line.split(':')[1].strip()
                
                elif 'ESSID:' in line:
                    ssid = line.split('"')[1] if '"' in line else ''
                    current['ssid'] = ssid
                
                elif 'Signal level' in line:
                    try:
                        match = re.search(r'Signal level[=:](\s*-?\d+)', line)
                        if match:
                            current['signal'] = int(match.group(1))
                    except:
                        pass
                
                elif 'Channel' in line:
                    try:
                        chan = re.search(r'Channel\s+(\d+)', line)
                        if chan:
                            current['channel'] = chan.group(1)
                    except:
                        pass
            
            if current.get('ssid'):
                networks.append(current)
            
            return networks
        except:
            return {'error': str(e)}

def get_public_ip_info():
    try:
        with urllib.request.urlopen('https://ipapi.co/json/', timeout=5) as response:
            data = json.loads(response.read().decode())
            return data
    except:
        return {}

def get_isp_links(isp_name):
    isp_links = {
        'TRUE': {'name': 'TRUE Online', 'url': 'https://www.trueinternet.co.th/', 'color': '#ff6b35'},
        '3BB': {'name': '3BB', 'url': 'https://www.3bb.co.th/', 'color': '#00a8e8'},
        'AIS': {'name': 'AIS Fibre', 'url': 'https://www.ais.th/fibre', 'color': '#8b5cf6'},
        'DTAC': {'name': 'DTAC', 'url': 'https://www.dtac.co.th/', 'color': '#ec4899'},
        'CAT': {'name': 'CAT Telecom', 'url': 'https://www.cattelecom.com/', 'color': '#10b981'},
        'TOT': {'name': 'TOT', 'url': 'https://www.tot.co.th/', 'color': '#f59e0b'},
        'SINGTEL': {'name': 'Singtel', 'url': 'https://www.singtel.com/', 'color': '#eab308'},
        'MAXIS': {'name': 'Maxis', 'url': 'https://www.maxis.com.my/', 'color': '#ef4444'},
        'STARHUB': {'name': 'StarHub', 'url': 'https://www.starhub.com/', 'color': '#0ea5e9'},
    }
    
    isp_name_upper = isp_name.upper()
    for key, isp in isp_links.items():
        if key in isp_name_upper:
            return isp
    
    return {'name': isp_name, 'url': '#', 'color': '#6b7280'}

def scan_wifi():
    system = platform.system()
    
    if system == 'Windows':
        networks = get_windows_wifi()
    elif system == 'Linux':
        networks = get_linux_wifi()
    else:
        networks = {'error': f'Unsupported OS: {system}'}
    
    public_info = get_public_ip_info()
    
    isp_info = public_info.get('org', 'Unknown ISP')
    isp_data = get_isp_links(isp_info)
    
    result = {
        'platform': system,
        'networks': networks if isinstance(networks, list) else [],
        'error': networks.get('error') if isinstance(networks, dict) else None,
        'public_ip': public_info.get('ip', 'N/A'),
        'isp': isp_data,
        'location': f"{public_info.get('city', 'N/A')}, {public_info.get('country', 'N/A')}",
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result

if __name__ == '__main__':
    print(json.dumps(scan_wifi(), ensure_ascii=False, indent=2))
