from flask import Flask, render_template, request, jsonify
import dns.resolver
import requests
import time

app = Flask(__name__)

def check_google_mx(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        for mx in mx_records:
            if 'google' in str(mx.exchange).lower():
                return "Google Workspace is found"
        return "No Google Workspace"
    except dns.resolver.NXDOMAIN:
        return "Domain does not exist"
    except dns.resolver.NoAnswer:
        return "No MX records found"
    except Exception as e:
        return f"Error checking MX records: {str(e)}"

def check_mx_history(domain, api_key):
    try:
        url = "https://api.apifreaks.com/v1.0/domain/dns/history"
        params = {
            "host-name": domain,
            "type": "mx",
            "page": 1
        }
        headers = {
            'X-apiKey': api_key
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            historical_records = data.get('historicalDnsRecords', [])
            
            for record_set in historical_records:
                dns_records = record_set.get('dnsRecords', [])
                for record in dns_records:
                    target = record.get('target', '').lower()
                    if 'google' in target or 'aspmx.l.google.com' in target:
                        query_time = record_set.get('queryTime', 'unknown date')
                        return f"Previously used Google MX (last seen: {query_time})"
            
            return "No historical Google MX records found"
        else:
            return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Error checking history: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_mx', methods=['POST'])
def check_mx():
    data = request.json
    domains = data.get('domains', [])
    check_history = data.get('checkHistory', False)
    api_key = data.get('apiKey', '')
    
    if not domains:
        return jsonify({'error': 'No domains provided'}), 400
    
    results = {}
    for domain in domains:
        domain = domain.strip()
        result = {
            'current': check_google_mx(domain),
            'history': None
        }
        
        if check_history and api_key:
            if len(domains) > 1:  # Only add delay in bulk mode
                time.sleep(2)  # 2 second delay between API calls
            result['history'] = check_mx_history(domain, api_key)
        
        results[domain] = result
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)