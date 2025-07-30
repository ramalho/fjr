#!/usr/bin/env python3
"""
Class C Network Scanner
Discovers active devices on a Class C network and resolves their hostnames.
"""

import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import platform

def get_local_network():
    """Get the local network subnet automatically."""
    try:
        # Get local IP address by connecting to a remote address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Convert to network address (assumes /24 subnet)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return str(network.network_address)[:-1]  # Remove last digit
    except Exception as e:
        print(f"Error detecting local network: {e}")
        return "192.168.1."  # Default fallback

def ping_host(ip):
    """Ping a single host to check if it's alive."""
    try:
        # Use ping command appropriate for the OS
        if sys.platform.startswith('win'):
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                  capture_output=True, text=True, timeout=3)
        else:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                  capture_output=True, text=True, timeout=3)
        
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False

def resolve_hostname(ip):
    """Resolve hostname for an IP address using multiple methods."""
    hostname = "Unknown"
    
    # Method 1: Standard reverse DNS lookup
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        if hostname and hostname != ip:
            return hostname
    except (socket.herror, socket.gaierror):
        pass
    
    # Method 2: Try mDNS/Bonjour resolution (common on local networks)
    try:
        # Set a shorter timeout for faster scanning
        socket.setdefaulttimeout(2)
        hostname = socket.getfqdn(ip)
        if hostname and hostname != ip and not hostname.startswith(ip):
            return hostname
    except:
        pass
    finally:
        socket.setdefaulttimeout(None)
    
    # Method 3: Try NetBIOS name resolution (Windows networks)
    if platform.system() == "Windows":
        try:
            result = subprocess.run(['nbtstat', '-A', ip], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '<00>' in line and 'UNIQUE' in line:
                        parts = line.strip().split()
                        if parts and not parts[0].startswith('<'):
                            return parts[0]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
    
    # Method 4: Try ARP table lookup for MAC address info
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['arp', '-a', ip], 
                                  capture_output=True, text=True, timeout=2)
        else:
            result = subprocess.run(['arp', '-n', ip], 
                                  capture_output=True, text=True, timeout=2)
        
        if result.returncode == 0 and result.stdout.strip():
            # If we have ARP info, the device exists but no hostname available
            return "No hostname (device found)"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    return "Unknown"

def scan_host(ip):
    """Scan a single host and return results if alive."""
    if ping_host(ip):
        hostname = resolve_hostname(ip)
        return (ip, hostname)
    return None

def scan_network(network_base="auto", max_workers=50):
    """
    Scan a Class C network for active devices.
    
    Args:
        network_base: Network base (e.g., "192.168.1.") or "auto" for auto-detection
        max_workers: Number of concurrent threads for scanning
    """
    
    if network_base == "auto":
        network_base = get_local_network()
    
    print(f"Scanning network {network_base}0/24...")
    print("This may take a few moments...\n")
    
    active_hosts = []
    
    # Create list of all IPs to scan (1-254, excluding 0 and 255)
    ip_list = [f"{network_base}{i}" for i in range(1, 255)]
    
    # Use ThreadPoolExecutor for concurrent scanning
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scanning tasks
        future_to_ip = {executor.submit(scan_host, ip): ip for ip in ip_list}
        
        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_ip):
            completed += 1
            if completed % 50 == 0:  # Progress indicator
                print(f"Progress: {completed}/254 hosts checked...")
            
            result = future.result()
            if result:
                active_hosts.append(result)
    
    return active_hosts

def print_results(active_hosts):
    """Print the results in a formatted table."""
    if not active_hosts:
        print("No active hosts found on the network.")
        return
    
    print(f"\nFound {len(active_hosts)} active host(s):")
    print("-" * 60)
    print(f"{'IP Address':<15} | {'Hostname'}")
    print("-" * 60)
    
    # Sort by IP address
    active_hosts.sort(key=lambda x: ipaddress.IPv4Address(x[0]))
    
    for ip, hostname in active_hosts:
        print(f"{ip:<15} | {hostname}")
    
    print("-" * 60)

def get_network_info():
    """Get additional network information to help with hostname resolution."""
    print("Network Configuration Info:")
    print("-" * 40)
    
    try:
        # Get local hostname
        local_hostname = socket.gethostname()
        print(f"Local hostname: {local_hostname}")
        
        # Get DNS servers (try to read from system)
        if platform.system() == "Windows":
            try:
                result = subprocess.run(['nslookup', 'localhost'], 
                                      capture_output=True, text=True, timeout=3)
                if "Server:" in result.stdout:
                    dns_line = [line for line in result.stdout.split('\n') if 'Server:' in line]
                    if dns_line:
                        print(f"DNS Server: {dns_line[0].split('Server:')[1].strip()}")
            except:
                pass
        else:
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            print(f"DNS Server: {line.split()[1]}")
                            break
            except:
                pass
                
    except Exception as e:
        print(f"Could not get network info: {e}")
    
    print()

def main():
    """Main function."""
    print("Class C Network Scanner")
    print("=" * 30)
    
    # Show network configuration info
    get_network_info()
    
    # Get network to scan
    network_input = input("Enter network base (e.g., '192.168.1.') or press Enter for auto-detection: ").strip()
    
    if not network_input:
        network_base = "auto"
    else:
        # Validate input format
        if not network_input.endswith('.'):
            network_input += '.'
        
        # Basic validation
        parts = network_input.rstrip('.').split('.')
        if len(parts) != 3 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            print("Invalid network format. Using auto-detection...")
            network_base = "auto"
        else:
            network_base = network_input
    
    try:
        # Perform the scan
        start_time = time.time()
        active_hosts = scan_network(network_base)
        scan_time = time.time() - start_time
        
        # Display results
        print_results(active_hosts)
        print(f"\nScan completed in {scan_time:.2f} seconds")
        
        # Show troubleshooting info if many unknowns
        unknown_count = sum(1 for _, hostname in active_hosts if hostname == "Unknown")
        if unknown_count > len(active_hosts) * 0.7:  # If >70% are unknown
            troubleshoot_hostname_issues()
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

def troubleshoot_hostname_issues():
    """Provide troubleshooting information for hostname resolution."""
    print("\nTroubleshooting Hostname Resolution:")
    print("=" * 45)
    print("If most hostnames show as 'Unknown', try these solutions:")
    print()
    print("1. ROUTER/NETWORK ISSUES:")
    print("   • Check if your router has hostname/DHCP client list")
    print("   • Some routers don't maintain proper DNS records")
    print("   • Consumer routers often don't support reverse DNS")
    print()
    print("2. DEVICE CONFIGURATION:")
    print("   • Devices may have firewalls blocking DNS queries")
    print("   • Some devices don't advertise hostnames on the network")
    print("   • Mobile devices often hide their hostnames for privacy")
    print()
    print("3. NETWORK SETUP:")
    print("   • Try running script as administrator/root for better access")
    print("   • Check if mDNS/Bonjour is enabled on your network")
    print("   • Windows networks may need NetBIOS name resolution")
    print()
    print("4. ALTERNATIVE METHODS:")
    print("   • Check your router's admin page for connected devices")
    print("   • Use network scanner tools like 'nmap' or 'Advanced IP Scanner'")
    print("   • Try 'arp -a' command to see MAC addresses of nearby devices")
    print()

if __name__ == "__main__":
    main()