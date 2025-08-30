# ====================================================================================
# Green Hydrogen Credit Marketplace - Flask Application
# Enhanced version with role-based authentication and dashboards
# ====================================================================================

import os
import json
import datetime
from functools import wraps
from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for, flash
from brownie import project, network, accounts, run

# --- Part 1: HTML TEMPLATES AS PYTHON STRINGS ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Green Hydrogen Credit Marketplace</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f7fafc; margin: 0; color: #1a202c; }
        .login-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; width: 100%; max-width: 400px; border: 1px solid #e2e8f0; }
        h1 { color: #28a745; margin-top: 0; font-weight: 700; font-size: 2.5rem; }
        p { color: #4a5568; margin-bottom: 25px; }
        .error-message { background-color: #fed7d7; color: #c53030; padding: 12px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #feb2b2; }
        select, button { width: 100%; padding: 14px; margin-top: 20px; border-radius: 8px; border: 1px solid #cbd5e0; font-size: 16px; font-family: 'Inter', sans-serif; }
        select { appearance: none; background: #fff url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23007CB2%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E') no-repeat right 15px center; background-size: 12px; }
        button { background-color: #28a745; color: white; font-weight: 600; cursor: pointer; border: none; transition: background-color 0.2s ease-in-out; }
        button:hover { background-color: #218838; }
        .role-description { font-size: 0.9rem; color: #718096; margin-top: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Green H2 Marketplace</h1>
        <p>Blockchain-based hydrogen credit trading platform</p>
        
        {% if error_message %}
        <div class="error-message">{{ error_message }}</div>
        {% endif %}
        
        <form action="/login" method="post">
            <select name="role" id="role" required onchange="showRoleDescription()">
                <option value="" disabled selected>-- Select Your Role --</option>
                <option value="producer">Hydrogen Producer</option>
                <option value="factory">Factory / Industrial Buyer</option>
                <option value="citizen">Citizen</option>
                <option value="government">Government Regulator</option>
                <option value="state_pollution_body">State Pollution Body</option>
            </select>
            <div class="role-description" id="role-description"></div>
            <button type="submit">Access Dashboard</button>
        </form>
    </div>

    <script>
        function showRoleDescription() {
            const role = document.getElementById('role').value;
            const descriptions = {
                'producer': 'Issue credits for hydrogen production (1kg H2 = 1 credit = ₹310)',
                'factory': 'Purchase credits to meet environmental quotas and compliance',
                'citizen': 'Buy credits to support clean energy and offset carbon footprint',
                'government': 'Monitor transactions, freeze accounts, and conduct audits',
                'state_pollution_body': 'Track factory compliance and issue certificates'
            };
            document.getElementById('role-description').textContent = descriptions[role] || '';
        }
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - VeridiChain</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #28a745; --secondary: #4a5568; --danger: #e53e3e; --info: #3182ce; --bg-main: #f7fafc; --bg-card: #ffffff; --border: #e2e8f0; --text-main: #1a202c; --text-light: #718096;}
        *, *::before, *::after { box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; margin: 0; background-color: var(--bg-main); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 280px; background-color: var(--bg-card); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 24px; }
        .sidebar h1 { font-size: 1.75rem; color: var(--primary); margin: 0 0 32px 0; }
        .user-info { margin-bottom: 32px; }
        .user-info h2 { font-size: 1.1rem; margin: 0 0 8px 0; }
        .user-info code { font-size: 0.8rem; background-color: var(--bg-main); padding: 4px 8px; border-radius: 6px; display: block; word-wrap: break-word; }
        .balance-display { background-color: #e6f6e9; border: 1px solid #b7e3c1; padding: 16px; border-radius: 8px; text-align: center; }
        .balance-display .label { font-size: 0.8rem; color: var(--text-light); margin-bottom: 8px; }
        .balance-display .value { font-size: 2rem; font-weight: 700; color: var(--primary); }
        .sidebar .logout { margin-top: auto; width: 100%; text-align: center; color: var(--info); text-decoration: none; font-weight: 500; padding: 12px; border-radius: 8px; background-color: #ebf4ff; }
        main { flex: 1; padding: 32px; overflow-y: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header h2 { font-size: 1.8rem; margin: 0; }
        .card { background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .card h3 { margin-top: 0; font-size: 1.25rem; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-weight: 500; margin-bottom: 8px; }
        input, select, button { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border); font-size: 1rem; font-family: 'Inter', sans-serif; }
        button { cursor: pointer; font-weight: 600; color: white; border: none; transition: all 0.2s ease; }
        .btn-primary { background-color: var(--primary); } .btn-primary:hover { background-color: #218838; }
        .btn-danger { background-color: var(--danger); } .btn-danger:hover { background-color: #c53030; }
        .btn-info { background-color: var(--info); } .btn-info:hover { background-color: #2c5282; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-size: 0.8rem; text-transform: uppercase; color: var(--text-light); }
        td code { font-size: 0.85rem; background-color: #edf2f7; padding: 2px 6px; border-radius: 4px; }
        .status-frozen { color: var(--danger); font-weight: 600; } .status-active { color: var(--primary); font-weight: 600; }
    </style>
</head>
<body>
    <aside class="sidebar">
        <h1>Green H2 Marketplace</h1>
        <div class="user-info">
            <h2>{{ role.replace('_', ' ').title() }}</h2>
            <code id="sidebar-address">{{ account_address }}</code>
        </div>
        <div class="balance-display">
            <div class="label">Your GHC Balance</div>
            <div class="value" id="sidebar-balance">...</div>
        </div>
        {% if role == 'factory' %}
        <div class="balance-display" style="margin-top: 16px; background-color: #ebf4ff; border-color: #90cdf4;">
            <div class="label">Quota Progress</div>
            <div class="value" id="quota-progress" style="color: #3182ce; font-size: 1.2rem;">...</div>
        </div>
        {% endif %}
        <a href="/logout" class="logout">Logout</a>
    </aside>

    <main>
        <div class="header"><h2>Dashboard</h2></div>
        <div class="card">
            {% if role == 'producer' %}
                <h3>Issue New Credits</h3>
                <p>As a certified hydrogen producer, you can issue credits for your production. Each kilogram of hydrogen equals 1 credit worth ₹{{ GHC_TO_RUPEE }}.</p>
                <div class="form-group"><label for="kg-produced">Kilograms (kg) of Green Hydrogen Produced:</label><input type="number" id="kg-produced" placeholder="e.g., 500" min="1"></div>
                <button class="btn-primary" onclick="producerIssueCredits()">Issue Credits to My Wallet</button>
            {% elif role == 'factory' %}
                <h3>Purchase Credits & Quota Management</h3>
                <p>Purchase hydrogen credits to meet your environmental quota and ensure regulatory compliance.</p>
                <div class="form-group">
                    <label for="quota-amount">Set Environmental Quota (GHC):</label>
                    <input type="number" id="quota-amount" placeholder="e.g., 1000" min="1">
                    <button class="btn-info" style="margin-top: 8px;" onclick="setQuota()">Set Quota</button>
                </div>
                <div class="form-group"><label for="credits-to-buy">Amount of GHC to purchase (Price: ₹{{ GHC_TO_RUPEE }} / GHC):</label><input type="number" id="credits-to-buy" placeholder="e.g., 50" min="1"></div>
                <button class="btn-primary" onclick="marketBuyCredits()">Purchase Credits</button>
            {% elif role == 'citizen' %}
                <h3>Support Clean Energy</h3>
                <p>Purchase hydrogen credits to support clean energy production and offset your carbon footprint.</p>
                <div class="form-group"><label for="credits-to-buy">Amount of GHC to purchase (Price: ₹{{ GHC_TO_RUPEE }} / GHC):</label><input type="number" id="credits-to-buy" placeholder="e.g., 10" min="1"></div>
                <button class="btn-primary" onclick="marketBuyCredits()">Purchase Credits</button>
            {% elif role == 'government' %}
                <h3>Regulatory Oversight & Account Management</h3>
                <p>Monitor the marketplace, manage accounts, and ensure compliance with regulations.</p>
                
                <!-- Real-time Monitoring Dashboard -->
                <div class="form-group">
                    <label>System Monitoring Overview:</label>
                    <div id="monitoring-overview" style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div style="text-align: center; padding: 10px; background: #e6f6e9; border-radius: 6px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;" id="total-credits">...</div>
                                <div style="font-size: 0.9rem; color: #666;">Total Credits in Circulation</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #ebf4ff; border-radius: 6px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #3182ce;" id="active-transactions">...</div>
                                <div style="font-size: 0.9rem; color: #666;">Transactions Today</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #fef5e7; border-radius: 6px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #d69e2e;" id="frozen-accounts">...</div>
                                <div style="font-size: 0.9rem; color: #666;">Frozen Accounts</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #fed7d7; border-radius: 6px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #e53e3e;" id="compliance-alerts">...</div>
                                <div style="font-size: 0.9rem; color: #666;">Compliance Alerts</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Account Management Section -->
                <div class="form-group">
                    <label for="freeze-account-select">Account Management:</label>
                    <select id="freeze-account-select">
                    {% for r, addr in all_accounts.items() %}{% if r != 'government' %}<option value="{{ addr }}">{{ r.replace('_', ' ').title() }} ({{ addr[:10] }}...)</option>{% endif %}{% endfor %}
                    </select>
                </div>
                <button class="btn-danger" style="margin-right: 10px; width: auto;" onclick="govFreezeAccount(true)">Freeze Account</button>
                <button class="btn-primary" style="margin-right: 10px; width: auto;" onclick="govFreezeAccount(false)">Unfreeze Account</button>
                <button class="btn-info" style="width: auto;" onclick="viewAccountDetails()">View Account Details</button>
                
                <!-- Producer Management -->
                <div class="form-group" style="margin-top: 20px;">
                    <label for="producer-cert-select">Producer Certification Management:</label>
                    <select id="producer-cert-select">
                        <option value="{{ all_accounts.producer }}">Producer ({{ all_accounts.producer[:10] }}...)</option>
                    </select>
                </div>
                <button class="btn-primary" style="margin-right: 10px; width: auto;" onclick="certifyProducer(true)">Certify Producer</button>
                <button class="btn-danger" style="margin-right: 10px; width: auto;" onclick="certifyProducer(false)">Revoke Certification</button>
                
                <!-- Advanced Monitoring and Audit -->
                <div style="margin-top: 20px;">
                    <button class="btn-info" style="margin-right: 10px; width: auto;" onclick="conductAudit()">Conduct AI Audit</button>
                    <button class="btn-info" style="margin-right: 10px; width: auto;" onclick="viewRegulatoryNotifications()">View Notifications</button>
                    <button class="btn-info" style="margin-right: 10px; width: auto;" onclick="generateComplianceReport()">Generate Report</button>
                    <button class="btn-info" style="width: auto;" onclick="viewSystemHealth()">System Health</button>
                </div>
                
            {% elif role == 'state_pollution_body' %}
                <h3>Environmental Compliance & Certificate Management</h3>
                <p>Track factory compliance with environmental quotas and issue certificates for compliant factories.</p>
                
                <!-- Compliance Dashboard -->
                <div class="form-group">
                    <label>Environmental Compliance Dashboard:</label>
                    <div id="compliance-dashboard" style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px;">
                            <div style="text-align: center; padding: 10px; background: #e6f6e9; border-radius: 6px;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #28a745;" id="factories-compliant">...</div>
                                <div style="font-size: 0.8rem; color: #666;">Factories Meeting Quota</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #fef5e7; border-radius: 6px;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #d69e2e;" id="factories-pending">...</div>
                                <div style="font-size: 0.8rem; color: #666;">Factories Pending</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #ebf4ff; border-radius: 6px;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #3182ce;" id="certificates-issued">...</div>
                                <div style="font-size: 0.8rem; color: #666;">Certificates Issued</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: #fed7d7; border-radius: 6px;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #e53e3e;" id="compliance-violations">...</div>
                                <div style="font-size: 0.8rem; color: #666;">Compliance Issues</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Factory Compliance Details -->
                <div class="form-group">
                    <label>Factory Compliance Status:</label>
                    <div id="compliance-overview" style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        Loading compliance data...
                    </div>
                </div>
                
                <!-- Certificate Management -->
                <div class="form-group">
                    <label for="certificate-factory">Certificate Management:</label>
                    <select id="certificate-factory">
                        <option value="">-- Select Factory --</option>
                        <option value="{{ all_accounts.factory }}">Factory ({{ all_accounts.factory[:10] }}...)</option>
                    </select>
                </div>
                <button class="btn-info" style="margin-right: 10px; width: auto;" onclick="issueCertificate()">Issue Compliance Certificate</button>
                <button class="btn-primary" style="margin-right: 10px; width: auto;" onclick="viewIssuedCertificates()">View All Certificates</button>
                <button class="btn-info" style="margin-right: 10px; width: auto;" onclick="trackFactoryProgress()">Track Factory Progress</button>
                <button class="btn-info" style="width: auto;" onclick="generateComplianceReport()">Generate Compliance Report</button>
            {% endif %}
        </div>

        <div class="card">
            <h3>Network Balances</h3>
            <table id="balances-table"><thead><tr><th>Role</th><th>Address</th><th>Balance (GHC)</th><th>Status</th></tr></thead><tbody id="balances-body"></tbody></table>
        </div>
        
        <div class="card">
            <h3>Transaction Log</h3>
            <table id="tx-table"><thead><tr><th>Timestamp</th><th>Type</th><th>Details</th><th>Amount</th><th>Tx Hash</th></tr></thead><tbody id="tx-body"></tbody></table>
        </div>
    </main>

<script>
    const GHC_TO_RUPEE = {{ GHC_TO_RUPEE }};
    const CURRENT_USER_ROLE = '{{ role }}';
    const CURRENT_USER_ADDRESS = '{{ account_address }}';

    async function callAPI(endpoint, method = 'GET', body = null) {
        try {
            const options = { method, headers: { 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            const response = await fetch(endpoint, options);
            if (response.status === 401) {
                alert("Your session has expired. Please log in again.");
                window.location.href = '/';
                return null;
            }
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'An unknown error occurred.');
            return result;
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            if (error instanceof SyntaxError) {
                 alert("A critical error occurred (likely a session timeout). Redirecting to login.");
                 window.location.href = '/';
            } else {
                alert(`ERROR: ${error.message}`);
            }
            return null;
        }
    }

    async function updateAllData() {
        const balances = await callAPI('/api/balances');
        const transactions = await callAPI('/api/transactions');
        if (balances) updateBalancesUI(balances);
        if (transactions) updateTransactionsUI(transactions);
    }

    function updateBalancesUI(data) {
        const tbody = document.getElementById('balances-body');
        tbody.innerHTML = '';
        Object.entries(data).forEach(([role, info]) => {
            let roleName = role.replace('_', ' ').charAt(0).toUpperCase() + role.slice(1).replace('_', ' ');
            let statusClass = info.frozen ? 'status-frozen' : 'status-active';
            let statusText = info.frozen ? 'Frozen' : 'Active';
            
            // Add role-specific status information
            let roleStatus = '';
            if (role === 'producer') {
                roleStatus = info.certified ? (info.active ? ' (Certified)' : ' (Inactive)') : ' (Not Certified)';
            } else if (role === 'factory' && info.has_quota) {
                roleStatus = info.quota_met ? ' (Quota Met ✓)' : ` (${info.credits_purchased.toFixed(1)}/${info.quota} GHC)`;
            }
            
            tbody.innerHTML += `<tr><td><strong>${roleName}${roleStatus}</strong></td><td><code>${info.address}</code></td><td>${info.balance.toFixed(2)}</td><td><span class="${statusClass}">${statusText}</span></td></tr>`;
            
            if (info.address === CURRENT_USER_ADDRESS) {
                document.getElementById('sidebar-balance').textContent = info.balance.toFixed(2);
                
                // Update quota progress for factories
                if (CURRENT_USER_ROLE === 'factory' && info.has_quota) {
                    const quotaElement = document.getElementById('quota-progress');
                    if (quotaElement) {
                        const progress = info.quota > 0 ? ((info.credits_purchased / info.quota) * 100).toFixed(1) : 0;
                        quotaElement.textContent = `${progress}%`;
                        if (info.quota_met) {
                            quotaElement.style.color = '#28a745';
                            quotaElement.textContent += ' ✓';
                        } else {
                            quotaElement.style.color = '#3182ce';
                        }
                    }
                }
            }
        });
    }

    function updateTransactionsUI(data) {
        const tbody = document.getElementById('tx-body');
        tbody.innerHTML = '<tr><td colspan="5">No transactions recorded yet.</td></tr>';
        if (!data || data.length === 0) return;
        tbody.innerHTML = '';
        data.slice().reverse().forEach(tx => {
            tbody.innerHTML += `<tr><td>${new Date(tx.timestamp).toLocaleString()}</td><td>${tx.type}</td><td>${tx.details}</td><td>${tx.amount_ghc} GHC</td><td><a href="#" title="${tx.tx_hash}"><code>${tx.tx_hash.substring(0,12)}...</code></a></td></tr>`;
        });
    }

    async function producerIssueCredits() {
        const amount = document.getElementById('kg-produced').value;
        if (!amount || amount <= 0) return alert('Please enter a valid amount.');
        const result = await callAPI('/api/producer/issue', 'POST', { amount: parseInt(amount) });
        if (result) { alert(result.message); updateAllData(); }
    }
    
    async function marketBuyCredits() {
        const amount = document.getElementById('credits-to-buy').value;
        if (!amount || amount <= 0) return alert('Please enter a valid amount.');
        if (confirm(`Confirm purchase of ${amount} GHC for ₹${amount * GHC_TO_RUPEE}?`)) {
            const result = await callAPI('/api/market/buy', 'POST', { amount: parseInt(amount), buyerRole: CURRENT_USER_ROLE });
            if (result) { alert(result.message); updateAllData(); }
        }
    }

    async function govFreezeAccount(status) {
        const address = document.getElementById('freeze-account-select').value;
        const action = status ? 'freeze' : 'unfreeze';
        if (confirm(`Are you sure you want to ${action} this account?`)) {
            const result = await callAPI('/api/gov/freeze', 'POST', { address, status });
            if (result) { alert(result.message); updateAllData(); }
        }
    }

    async function setQuota() {
        const amount = document.getElementById('quota-amount').value;
        if (!amount || amount <= 0) return alert('Please enter a valid quota amount.');
        if (confirm(`Set environmental quota to ${amount} GHC?`)) {
            const result = await callAPI('/api/factory/quota', 'POST', { quota: parseInt(amount) });
            if (result) { alert(result.message); updateAllData(); }
        }
    }

    async function conductAudit() {
        const result = await callAPI('/api/gov/audit', 'POST');
        if (result) {
            alert(`AI Audit Results:\\n\\n${result.summary}\\n\\nDetailed report available in system logs.`);
        }
    }

    async function certifyProducer(certified) {
        const producer = document.getElementById('producer-cert-select').value;
        const action = certified ? 'certify' : 'revoke certification for';
        if (confirm(`Are you sure you want to ${action} this producer?`)) {
            const result = await callAPI('/api/gov/certify', 'POST', { producer_address: producer, certified });
            if (result) { alert(result.message); updateAllData(); }
        }
    }

    async function viewRegulatoryNotifications() {
        const result = await callAPI('/api/gov/notifications');
        if (result && result.length > 0) {
            let notificationText = 'Recent Regulatory Notifications:\\n\\n';
            result.slice(0, 10).forEach(notif => {
                notificationText += `${new Date(notif.timestamp).toLocaleString()}: ${notif.action} - ${notif.details}\\n`;
            });
            alert(notificationText);
        } else {
            alert('No recent regulatory notifications found.');
        }
    }

    async function viewAccountDetails() {
        const address = document.getElementById('freeze-account-select').value;
        const result = await callAPI(`/api/gov/account-details?address=${address}`);
        if (result) {
            let details = `Account Details for ${address}:\\n\\n`;
            details += `Role: ${result.role}\\n`;
            details += `Balance: ${result.balance} GHC\\n`;
            details += `Status: ${result.frozen ? 'FROZEN' : 'ACTIVE'}\\n`;
            details += `Total Transactions: ${result.transaction_count}\\n`;
            if (result.role === 'producer') {
                details += `Certified: ${result.certified ? 'YES' : 'NO'}\\n`;
                details += `Total Issued: ${result.total_issued} GHC\\n`;
            } else if (result.role === 'factory') {
                details += `Quota Set: ${result.has_quota ? 'YES' : 'NO'}\\n`;
                if (result.has_quota) {
                    details += `Quota: ${result.quota} GHC\\n`;
                    details += `Progress: ${result.credits_purchased}/${result.quota} GHC\\n`;
                    details += `Quota Met: ${result.quota_met ? 'YES' : 'NO'}\\n`;
                }
            }
            alert(details);
        }
    }

    async function generateComplianceReport() {
        const result = await callAPI('/api/compliance-report');
        if (result) {
            let report = `Compliance Report - ${new Date().toLocaleDateString()}:\\n\\n`;
            report += `Total Credits in Circulation: ${result.total_credits} GHC\\n`;
            report += `Active Producers: ${result.active_producers}\\n`;
            report += `Factories with Quotas: ${result.factories_with_quotas}\\n`;
            report += `Factories Meeting Quotas: ${result.compliant_factories}\\n`;
            report += `Certificates Issued: ${result.certificates_issued}\\n`;
            report += `Frozen Accounts: ${result.frozen_accounts}\\n\\n`;
            report += `Compliance Rate: ${result.compliance_rate}%\\n`;
            report += `System Health: ${result.system_health}`;
            alert(report);
        }
    }

    async function viewSystemHealth() {
        const result = await callAPI('/api/gov/system-health');
        if (result) {
            let health = `System Health Report:\\n\\n`;
            health += `Overall Status: ${result.status}\\n`;
            health += `Active Users: ${result.active_users}\\n`;
            health += `Transaction Volume (24h): ${result.daily_transactions}\\n`;
            health += `Credit Utilization: ${result.credit_utilization}%\\n`;
            health += `Network Stability: ${result.network_stability}\\n\\n`;
            if (result.alerts && result.alerts.length > 0) {
                health += `Active Alerts:\\n`;
                result.alerts.forEach(alert => health += `- ${alert}\\n`);
            } else {
                health += 'No active system alerts.';
            }
            alert(health);
        }
    }

    async function updateMonitoringOverview() {
        if (CURRENT_USER_ROLE === 'government') {
            const balances = await callAPI('/api/balances');
            const transactions = await callAPI('/api/transactions');
            const notifications = await callAPI('/api/gov/notifications');
            
            if (balances && transactions) {
                // Calculate total credits in circulation
                const totalCredits = Object.values(balances).reduce((sum, info) => sum + info.balance, 0);
                document.getElementById('total-credits').textContent = totalCredits.toFixed(0);
                
                // Count today's transactions
                const today = new Date().toDateString();
                const todayTransactions = transactions.filter(tx => 
                    new Date(tx.timestamp).toDateString() === today
                ).length;
                document.getElementById('active-transactions').textContent = todayTransactions;
                
                // Count frozen accounts
                const frozenCount = Object.values(balances).filter(info => info.frozen).length;
                document.getElementById('frozen-accounts').textContent = frozenCount;
                
                // Count compliance alerts (recent notifications)
                const recentAlerts = notifications ? notifications.filter(notif => 
                    (new Date() - new Date(notif.timestamp)) < 24 * 60 * 60 * 1000
                ).length : 0;
                document.getElementById('compliance-alerts').textContent = recentAlerts;
            }
        }
    }

    async function issueCertificate() {
        const factory = document.getElementById('certificate-factory').value;
        if (!factory) return alert('Please select a factory.');
        if (confirm('Issue compliance certificate for selected factory?')) {
            const result = await callAPI('/api/pollution/certificate', 'POST', { factory_address: factory });
            if (result) { alert(result.message); updateAllData(); updateComplianceOverview(); }
        }
    }

    async function viewIssuedCertificates() {
        const result = await callAPI('/api/certificates');
        if (result && result.length > 0) {
            let certText = 'Issued Certificates:\\n\\n';
            result.forEach(cert => {
                certText += `${cert.certificate_id} - Factory: ${cert.factory_address.substring(0,10)}... - Status: ${cert.compliance_status} - Date: ${new Date(cert.issue_date).toLocaleDateString()}\\n`;
            });
            alert(certText);
        } else {
            alert('No certificates have been issued yet.');
        }
    }

    async function updateComplianceOverview() {
        if (CURRENT_USER_ROLE === 'state_pollution_body') {
            const balances = await callAPI('/api/balances');
            const certificates = await callAPI('/api/certificates');
            
            if (balances && balances.factory) {
                const factory = balances.factory;
                let overviewHtml = '<strong>Factory Compliance Status:</strong><br>';
                
                if (factory.has_quota) {
                    const progress = ((factory.credits_purchased / factory.quota) * 100).toFixed(1);
                    overviewHtml += `Quota: ${factory.quota} GHC | Purchased: ${factory.credits_purchased} GHC (${progress}%)<br>`;
                    overviewHtml += `Status: ${factory.quota_met ? '<span style="color: #28a745;">✓ QUOTA MET</span>' : '<span style="color: #dc3545;">Quota Not Met</span>'}<br>`;
                    
                    if (certificates && certificates.length > 0) {
                        const factoryCerts = certificates.filter(c => c.factory_address === factory.address);
                        overviewHtml += `Certificates Issued: ${factoryCerts.length}`;
                    } else {
                        overviewHtml += 'Certificates Issued: 0';
                    }
                } else {
                    overviewHtml += '<span style="color: #ffc107;">No environmental quota set</span>';
                }
                
                document.getElementById('compliance-overview').innerHTML = overviewHtml;
            }
            
            // Update compliance dashboard
            await updateComplianceDashboard();
        }
    }

    async function updateComplianceDashboard() {
        if (CURRENT_USER_ROLE === 'state_pollution_body') {
            const balances = await callAPI('/api/balances');
            const certificates = await callAPI('/api/certificates');
            
            if (balances) {
                // Count compliant factories (those meeting quotas)
                let compliantFactories = 0;
                let pendingFactories = 0;
                let totalFactories = 0;
                
                Object.entries(balances).forEach(([role, info]) => {
                    if (role === 'factory') {
                        totalFactories++;
                        if (info.has_quota) {
                            if (info.quota_met) {
                                compliantFactories++;
                            } else {
                                pendingFactories++;
                            }
                        } else {
                            pendingFactories++;
                        }
                    }
                });
                
                document.getElementById('factories-compliant').textContent = compliantFactories;
                document.getElementById('factories-pending').textContent = pendingFactories;
                document.getElementById('certificates-issued').textContent = certificates ? certificates.length : 0;
                
                // Calculate compliance violations (factories not meeting quotas after deadline)
                const violations = pendingFactories; // Simplified for demo
                document.getElementById('compliance-violations').textContent = violations;
            }
        }
    }

    async function trackFactoryProgress() {
        const result = await callAPI('/api/pollution/factory-progress');
        if (result) {
            let progress = `Factory Progress Report:\\n\\n`;
            result.forEach(factory => {
                progress += `Factory: ${factory.address.substring(0, 10)}...\\n`;
                progress += `Quota: ${factory.quota} GHC\\n`;
                progress += `Purchased: ${factory.credits_purchased} GHC\\n`;
                progress += `Progress: ${factory.progress_percentage}%\\n`;
                progress += `Status: ${factory.status}\\n\\n`;
            });
            alert(progress);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        updateAllData();
        if (CURRENT_USER_ROLE === 'state_pollution_body') {
            updateComplianceOverview();
        }
        if (CURRENT_USER_ROLE === 'government') {
            updateMonitoringOverview();
        }
        setInterval(() => {
            updateAllData();
            if (CURRENT_USER_ROLE === 'state_pollution_body') {
                updateComplianceOverview();
            }
            if (CURRENT_USER_ROLE === 'government') {
                updateMonitoringOverview();
            }
        }, 15000);
    });
</script>
</body>
</html>
"""

# --- Part 2: FLASK APPLICATION LOGIC ---
GHC_TO_RUPEE = 310

# --- 1. BLOCKCHAIN & PROJECT SETUP ---
try:
    if not network.is_connected(): network.connect('development')
    print("Successfully connected to the local blockchain.")
    p = project.load()
    GreenHydrogenCredit = p.GreenHydrogenCredit
    print("Brownie project loaded successfully.")
except Exception as e:
    print(f"FATAL: Setup failed. Ensure Ganache is running and project is sound. Error: {e}")
    exit()

# --- 2. LOAD ACCOUNTS ---
try:
    with open('accounts.json', 'r') as f: account_map = json.load(f)
    all_accounts = {role: accounts[idx] for role, idx in account_map.items()}
    gov_account = all_accounts['government']
    producer_account = all_accounts['producer']
    print("Loaded accounts from accounts.json")
except Exception as e:
    print(f"FATAL: Could not load accounts.json (ensure certifier is removed). Error: {e}")
    exit()

# --- 3. DEPLOY/CONNECT CONTRACT ---
try:
    credit_contract = GreenHydrogenCredit[-1]
    print(f"Found existing contract at: {credit_contract.address}")
except IndexError:
    print("Contract not found. Deploying and configuring...")
    try:
        run('scripts/deploy.py', 'main')
        credit_contract = GreenHydrogenCredit[-1]
        print(f"New contract deployed at: {credit_contract.address}")
    except Exception as e:
        print(f"FATAL: Deployment/configuration failed. Error: {e}")
        exit()

# --- 4. INITIALIZE ROLES AND SETUP ---
def initialize_contract_roles():
    """Initialize all account roles in the smart contract"""
    try:
        # Set government address (should already be set by constructor)
        gov_role = credit_contract.getUserRole(gov_account.address)
        if gov_role[0] == 0:  # UserRole.NONE
            print("Setting up government role...")
            tx = credit_contract.setGovernmentAddress(gov_account.address, {'from': gov_account})
            tx.wait(1)
        
        # Set pollution body address
        pollution_account = all_accounts['state_pollution_body']
        pollution_role = credit_contract.getUserRole(pollution_account.address)
        if pollution_role[0] == 0:  # UserRole.NONE
            print("Setting up pollution body role...")
            tx = credit_contract.setPollutionBodyAddress(pollution_account.address, {'from': gov_account})
            tx.wait(1)
        
        # Register and certify producer
        producer_role = credit_contract.getUserRole(producer_account.address)
        if producer_role[0] == 0:  # UserRole.NONE
            print("Registering producer...")
            tx = credit_contract.registerAsProducer({'from': producer_account})
            tx.wait(1)
        
        # Certify the producer
        producer_info = credit_contract.getProducerInfo(producer_account.address)
        if not producer_info[0]:  # not certified
            print("Certifying producer...")
            tx = credit_contract.certifyProducer(producer_account.address, True, {'from': gov_account})
            tx.wait(1)
        
        # Register factory
        factory_account = all_accounts['factory']
        factory_role = credit_contract.getUserRole(factory_account.address)
        if factory_role[0] == 0:  # UserRole.NONE
            print("Registering factory...")
            tx = credit_contract.registerAsFactory({'from': factory_account})
            tx.wait(1)
        
        # Register citizen
        citizen_account = all_accounts['citizen']
        citizen_role = credit_contract.getUserRole(citizen_account.address)
        if citizen_role[0] == 0:  # UserRole.NONE
            print("Registering citizen...")
            tx = credit_contract.registerAsCitizen({'from': citizen_account})
            tx.wait(1)
        
        print("All roles initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing roles: {e}")

# Initialize roles
initialize_contract_roles()

# --- UTILITY: TRANSACTION LOGGER ---
def log_transaction(tx_type, details, amount_ghc, tx_hash):
    log_file = 'transactions.json'
    new_log = {'timestamp': datetime.datetime.utcnow().isoformat() + "Z", 'type': tx_type, 'details': details, 'amount_ghc': amount_ghc, 'tx_hash': tx_hash}
    try:
        logs = []
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            with open(log_file, 'r') as f: logs = json.load(f)
        logs.append(new_log)
        with open(log_file, 'w') as f: json.dump(logs, f, indent=2)
    except Exception as e: print(f"Error writing to transaction log: {e}")

# --- 4. FLASK WEB SERVER ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return jsonify({'message': 'Authentication required. Please log in.'}), 401
        
        # Check if role is valid
        if session['role'] not in all_accounts:
            session.clear()
            return jsonify({'message': 'Invalid session. Please log in again.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---
@app.route('/')
def index():
    if 'role' in session: 
        return redirect(url_for('dashboard'))
    error_message = request.args.get('error')
    return render_template_string(LOGIN_HTML, error_message=error_message)

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    if not role:
        return redirect(url_for('index', error='Please select a role to continue.'))
    
    if role in all_accounts:
        session['role'] = role
        session['login_time'] = datetime.datetime.utcnow().isoformat()
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index', error='Invalid role selected. Please try again.'))

@app.route('/dashboard')
def dashboard():
    if 'role' not in session: 
        return redirect(url_for('index', error='Please log in to access the dashboard.'))
    
    role = session['role']
    if role not in all_accounts:
        session.clear()
        return redirect(url_for('index', error='Invalid session. Please log in again.'))
    
    return render_template_string(DASHBOARD_HTML, 
                                role=role, 
                                account_address=all_accounts[role].address, 
                                all_accounts={r: a.address for r, a in all_accounts.items()}, 
                                GHC_TO_RUPEE=GHC_TO_RUPEE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- API ENDPOINTS ---
@app.route('/api/balances', methods=['GET'])
@login_required
def get_balances():
    balances = {}
    for role, acc in all_accounts.items():
        balance_info = {
            'address': acc.address, 
            'balance': credit_contract.balanceOf(acc) / 10**18, 
            'frozen': credit_contract.isAccountFrozen(acc)
        }
        
        # Add role-specific information
        if role == 'factory':
            try:
                factory_info = credit_contract.getFactoryInfo(acc.address)
                balance_info['quota'] = factory_info[0] / 10**18 if factory_info[1] else 0  # quota amount
                balance_info['quota_met'] = factory_info[3] if factory_info[1] else False  # quotaMet
                balance_info['credits_purchased'] = factory_info[2] / 10**18  # creditsPurchased
                balance_info['has_quota'] = factory_info[1]  # hasQuota
            except Exception as e:
                print(f"Error getting factory info: {e}")
                balance_info['quota'] = 0
                balance_info['quota_met'] = False
                balance_info['credits_purchased'] = 0
                balance_info['has_quota'] = False
        
        elif role == 'producer':
            try:
                producer_info = credit_contract.getProducerInfo(acc.address)
                balance_info['certified'] = producer_info[0]  # certified
                balance_info['total_issued'] = producer_info[1] / 10**18  # totalIssued
                balance_info['active'] = producer_info[3]  # isActive
            except Exception as e:
                print(f"Error getting producer info: {e}")
                balance_info['certified'] = False
                balance_info['total_issued'] = 0
                balance_info['active'] = False
        
        balances[role] = balance_info
    
    return jsonify(balances)

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    log_file = 'transactions.json'
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        with open(log_file, 'r') as f: return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/producer/issue', methods=['POST'])
@login_required
def producer_issue():
    # Only the producer can issue, so we check the session role
    if session.get('role') != 'producer':
        return jsonify({'message': 'Only certified hydrogen producers can issue credits.'}), 403
    
    data = request.get_json()
    amount_kg = int(data.get('amount', 0))
    
    if amount_kg <= 0: 
        return jsonify({'message': 'Invalid amount. Please enter kilograms of hydrogen produced.'}), 400
    
    if amount_kg > 10000:  # Safety limit
        return jsonify({'message': 'Amount too large. Maximum 10,000 kg per issuance.'}), 400
    
    try:
        # Check if producer is certified and active
        producer_info = credit_contract.getProducerInfo(producer_account.address)
        if not producer_info[0]:  # not certified
            return jsonify({'message': 'Producer is not certified. Contact government for certification.'}), 403
        
        if not producer_info[3]:  # not active
            return jsonify({'message': 'Producer account is not active. Contact government.'}), 403
        
        # Convert kg to credits (1 kg H2 = 1 credit)
        credits_to_issue = amount_kg
        amount_wei = credits_to_issue * 10**18
        
        # Calculate equivalent value in rupees (1 credit = 310 rupees)
        total_value_rupees = credits_to_issue * GHC_TO_RUPEE
        
        # Issue credits using smart contract
        tx = credit_contract.issueCredits(amount_wei, {'from': producer_account})
        tx.wait(1)
        
        # Log the transaction with detailed information
        log_transaction(
            'ISSUE', 
            f"Producer issued {credits_to_issue} GHC for {amount_kg}kg H2 production (₹{total_value_rupees} value)", 
            credits_to_issue, 
            tx.txid
        )
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'CREDIT_ISSUANCE',
            producer_account.address,
            None,
            credits_to_issue,
            f"Value: ₹{total_value_rupees}, H2 Production: {amount_kg}kg"
        )
        
        return jsonify({
            'message': f'SUCCESS: Issued {credits_to_issue} GHC for {amount_kg}kg hydrogen production. Total value: ₹{total_value_rupees}',
            'tx_hash': tx.txid,
            'credits_issued': credits_to_issue,
            'hydrogen_kg': amount_kg,
            'value_rupees': total_value_rupees
        })
        
    except Exception as e: 
        error_msg = str(e)
        if "Only certified active producers" in error_msg:
            return jsonify({'message': 'Producer certification required. Contact government for certification.'}), 403
        elif "Account is frozen" in error_msg:
            return jsonify({'message': 'Account is frozen by government. Contact authorities.'}), 403
        else:
            return jsonify({'message': f'Credit issuance failed: {error_msg}'}), 400

@app.route('/api/market/buy', methods=['POST'])
@login_required
def market_buy():
    data = request.get_json()
    amount = int(data.get('amount', 0))
    buyer_role = session.get('role')  # Use session role instead of passed role for security
    
    if amount <= 0: 
        return jsonify({'message': 'Invalid amount.'}), 400
    
    if buyer_role not in ['factory', 'citizen']:
        return jsonify({'message': 'Only factories and citizens can purchase credits.'}), 403
    
    buyer_account = all_accounts[buyer_role]
    total_cost = amount * GHC_TO_RUPEE
    
    try:
        # Step 1: Mock Razorpay payment processing
        payment_result = process_mock_razorpay_payment(buyer_account.address, amount, total_cost)
        if not payment_result['success']:
            return jsonify({'message': f'Payment failed: {payment_result["error"]}'}), 400
        
        # Step 2: Check if producer has sufficient credits
        amount_wei = amount * 10**18
        if credit_contract.balanceOf(producer_account) < amount_wei:
            return jsonify({'message': 'Insufficient credits available in marketplace.'}), 400
        
        # Step 3: Execute blockchain transaction using the new purchaseCredits function
        tx = credit_contract.purchaseCredits(
            producer_account.address, 
            amount_wei, 
            total_cost, 
            {'from': buyer_account}
        )
        tx.wait(1)
        
        # Step 4: Log the transaction
        log_transaction(
            'PURCHASE', 
            f"{buyer_role.title()} purchased {amount} GHC for ₹{total_cost}", 
            amount, 
            tx.txid
        )
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'CREDIT_PURCHASE',
            producer_account.address,
            buyer_account.address,
            amount,
            f"Buyer: {buyer_role.title()}, Cost: ₹{total_cost}"
        )
        
        # Step 5: Check if factory quota is met (for factories only)
        quota_message = ""
        if buyer_role == 'factory':
            try:
                factory_info = credit_contract.getFactoryInfo(buyer_account.address)
                if factory_info[1]:  # hasQuota
                    credits_purchased = factory_info[2] / 10**18
                    quota = factory_info[0] / 10**18
                    if factory_info[3]:  # quotaMet
                        quota_message = f" 🎉 Congratulations! You have met your environmental quota of {quota} GHC."
                    else:
                        remaining = quota - credits_purchased
                        quota_message = f" Progress: {credits_purchased}/{quota} GHC ({remaining} remaining to meet quota)."
            except Exception as e:
                print(f"Error checking quota status: {e}")
        
        return jsonify({
            'message': f'Successfully purchased {amount} GHC for ₹{total_cost}.{quota_message}',
            'tx_hash': tx.txid,
            'payment_id': payment_result['payment_id']
        })
        
    except Exception as e: 
        return jsonify({'message': f'Purchase failed: {str(e)}'}), 400

def process_mock_razorpay_payment(user_address, amount_ghc, amount_rupees):
    """
    Mock Razorpay payment processing function
    In a real implementation, this would integrate with actual Razorpay API
    """
    import random
    import time
    
    # Simulate payment processing delay
    time.sleep(0.5)
    
    # Generate mock payment ID
    payment_id = f"pay_mock_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Mock payment validation (90% success rate for demo purposes)
    if random.random() < 0.9:
        # Log payment record
        payment_record = {
            'payment_id': payment_id,
            'user_address': user_address,
            'amount_ghc': amount_ghc,
            'amount_rupees': amount_rupees,
            'gateway': 'razorpay_mock',
            'status': 'SUCCESS',
            'timestamp': datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        # Save payment record to file
        try:
            payments_file = 'payments.json'
            payments = []
            if os.path.exists(payments_file) and os.path.getsize(payments_file) > 0:
                with open(payments_file, 'r') as f:
                    payments = json.load(f)
            payments.append(payment_record)
            with open(payments_file, 'w') as f:
                json.dump(payments, f, indent=2)
        except Exception as e:
            print(f"Error saving payment record: {e}")
        
        return {'success': True, 'payment_id': payment_id}
    else:
        return {'success': False, 'error': 'Payment gateway declined the transaction'}

def notify_regulatory_bodies(action_type, details, subject_address=None):
    """
    Send notifications to government and pollution body for regulatory oversight
    This function ensures automatic notifications for all transactions as required
    """
    notification = {
        'timestamp': datetime.datetime.utcnow().isoformat() + "Z",
        'action': action_type,
        'details': details,
        'subject_address': subject_address,
        'notified_by': 'system',
        'notification_id': f"{action_type}_{int(datetime.datetime.utcnow().timestamp())}"
    }
    
    try:
        notifications_file = 'regulatory_notifications.json'
        notifications = []
        if os.path.exists(notifications_file) and os.path.getsize(notifications_file) > 0:
            with open(notifications_file, 'r') as f:
                notifications = json.load(f)
        
        notifications.append(notification)
        
        # Keep only last 1000 notifications to prevent file from growing too large
        if len(notifications) > 1000:
            notifications = notifications[-1000:]
        
        with open(notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)
        
        # Log notification for audit trail
        print(f"REGULATORY NOTIFICATION: {action_type} - {details}")
        
        # In a real system, this would also send real-time notifications
        # to government and pollution body dashboards via WebSocket or similar
            
    except Exception as e:
        print(f"Error saving regulatory notification: {e}")

def enhanced_transaction_monitoring(tx_type, from_address, to_address, amount, additional_details=""):
    """
    Enhanced monitoring function that ensures all transactions are properly tracked
    and regulatory bodies are notified automatically
    """
    try:
        # Create detailed notification for regulatory oversight
        if tx_type == 'CREDIT_ISSUANCE':
            notify_regulatory_bodies(
                'CREDIT_ISSUANCE',
                f"Producer {from_address[:10]}... issued {amount} GHC credits. {additional_details}",
                from_address
            )
        elif tx_type == 'CREDIT_PURCHASE':
            notify_regulatory_bodies(
                'CREDIT_PURCHASE', 
                f"Credit purchase: {amount} GHC from {from_address[:10]}... to {to_address[:10]}... {additional_details}",
                to_address
            )
        elif tx_type == 'QUOTA_COMPLETION':
            notify_regulatory_bodies(
                'QUOTA_COMPLETION',
                f"Factory {from_address[:10]}... has completed their environmental quota. {additional_details}",
                from_address
            )
        elif tx_type == 'REGULATORY_ACTION':
            notify_regulatory_bodies(
                'REGULATORY_ACTION',
                f"Government action: {additional_details}",
                to_address
            )
        
        # Additional monitoring for compliance tracking
        if tx_type in ['CREDIT_PURCHASE', 'QUOTA_COMPLETION']:
            # Check if this triggers any compliance milestones
            check_compliance_milestones(to_address if to_address else from_address)
            
    except Exception as e:
        print(f"Error in enhanced transaction monitoring: {e}")

def check_compliance_milestones(address):
    """
    Check if a transaction triggers any compliance milestones that need regulatory attention
    """
    try:
        # Check if address is a factory
        for role, acc in all_accounts.items():
            if acc.address == address and role == 'factory':
                factory_info = credit_contract.getFactoryInfo(address)
                if factory_info[1]:  # hasQuota
                    quota = factory_info[0] / 10**18
                    purchased = factory_info[2] / 10**18
                    progress = (purchased / quota * 100) if quota > 0 else 0
                    
                    # Notify at key milestones
                    if progress >= 50 and progress < 75:
                        notify_regulatory_bodies(
                            'COMPLIANCE_MILESTONE',
                            f"Factory {address[:10]}... has reached 50% of environmental quota ({purchased}/{quota} GHC)",
                            address
                        )
                    elif progress >= 75 and progress < 100:
                        notify_regulatory_bodies(
                            'COMPLIANCE_MILESTONE', 
                            f"Factory {address[:10]}... has reached 75% of environmental quota ({purchased}/{quota} GHC)",
                            address
                        )
                    elif factory_info[3]:  # quotaMet
                        notify_regulatory_bodies(
                            'QUOTA_COMPLETION',
                            f"Factory {address[:10]}... has completed environmental quota ({purchased}/{quota} GHC) - eligible for certificate",
                            address
                        )
                break
    except Exception as e:
        print(f"Error checking compliance milestones: {e}")

def conduct_mock_ai_audit():
    """
    Mock AI audit function that analyzes system activity and provides compliance insights
    In a real implementation, this would use machine learning models to analyze patterns
    """
    import random
    
    # Simulate AI analysis of transaction patterns, account behaviors, etc.
    risk_factors = []
    recommendations = []
    
    try:
        # Analyze transaction history
        if os.path.exists('transactions.json') and os.path.getsize('transactions.json') > 0:
            with open('transactions.json', 'r') as f:
                transactions = json.load(f)
            
            # Mock analysis of transaction patterns
            if len(transactions) > 50:
                risk_factors.append("High transaction volume detected")
                recommendations.append("Monitor for unusual trading patterns")
            
            # Check for rapid succession transactions
            recent_transactions = [t for t in transactions if 
                                 (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00'))).days < 1]
            
            if len(recent_transactions) > 10:
                risk_factors.append("Rapid transaction activity in last 24 hours")
                recommendations.append("Verify legitimacy of high-frequency trading")
        
        # Analyze account balances for anomalies
        balances = {}
        for role, acc in all_accounts.items():
            balance = credit_contract.balanceOf(acc) / 10**18
            balances[role] = balance
        
        # Check for concentration of credits
        total_credits = sum(balances.values())
        if total_credits > 0:
            for role, balance in balances.items():
                if balance / total_credits > 0.7:  # More than 70% concentration
                    risk_factors.append(f"High credit concentration in {role} account")
                    recommendations.append(f"Monitor {role} account for market manipulation")
        
        # Determine overall risk level
        if len(risk_factors) == 0:
            risk_level = "LOW"
        elif len(risk_factors) <= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Generate summary
        if len(risk_factors) == 0:
            summary = "System audit completed. No significant risk factors detected. All accounts and transactions appear normal."
        else:
            summary = f"System audit completed. {len(risk_factors)} risk factor(s) identified. Risk level: {risk_level}. Review recommended."
        
        # Add standard recommendations
        recommendations.extend([
            "Continue regular monitoring of all transactions",
            "Verify producer certifications quarterly",
            "Review factory quota compliance monthly"
        ])
        
        return {
            'risk_level': risk_level,
            'summary': summary,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'audit_timestamp': datetime.datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        return {
            'risk_level': 'ERROR',
            'summary': f'Audit failed due to system error: {str(e)}',
            'risk_factors': ['System error during audit'],
            'recommendations': ['Contact system administrator'],
            'audit_timestamp': datetime.datetime.utcnow().isoformat() + "Z"
        }

@app.route('/api/factory/quota', methods=['POST'])
@login_required
def set_factory_quota():
    if session.get('role') != 'factory':
        return jsonify({'message': 'Only factories can set quotas.'}), 403
    
    data = request.get_json()
    quota = int(data.get('quota', 0))
    
    if quota <= 0:
        return jsonify({'message': 'Invalid quota amount.'}), 400
    
    try:
        factory_account = all_accounts['factory']
        
        # Use the smart contract's setQuota function
        tx = credit_contract.setQuota(quota * 10**18, {'from': factory_account})
        tx.wait(1)
        
        log_transaction('QUOTA_SET', f"Factory set environmental quota to {quota} GHC", quota, tx.txid)
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'REGULATORY_ACTION',
            factory_account.address,
            None,
            quota,
            f"Factory set environmental quota to {quota} GHC"
        )
        
        return jsonify({
            'message': f'Environmental quota set to {quota} GHC. Start purchasing credits to meet your compliance target.',
            'tx_hash': tx.txid
        })
    except Exception as e:
        return jsonify({'message': f'Quota setting failed: {str(e)}'}), 400

@app.route('/api/gov/freeze', methods=['POST'])
@login_required
def gov_freeze():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can freeze accounts.'}), 403
    
    data = request.get_json()
    target_address = data.get('address')
    status = bool(data.get('status'))
    
    if not target_address: 
        return jsonify({'message': 'Invalid address.'}), 400
    
    try:
        tx = credit_contract.setAccountFrozen(target_address, status, {'from': gov_account})
        tx.wait(1)
        action = "FROZEN" if status else "UNFROZEN"
        log_transaction('REGULATORY', f"Government {action} account {target_address[:12]}...", 0, tx.txid)
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'REGULATORY_ACTION',
            gov_account.address,
            target_address,
            0,
            f"Account {target_address[:12]}... has been {action.lower()}"
        )
        
        return jsonify({'message': f'Account has been {action.lower()}.', 'tx_hash': tx.txid})
    except Exception as e: 
        return jsonify({'message': f'Action Failed: {e}'}), 400

@app.route('/api/gov/certify', methods=['POST'])
@login_required
def gov_certify_producer():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can certify producers.'}), 403
    
    data = request.get_json()
    producer_address = data.get('producer_address')
    certified = bool(data.get('certified'))
    
    if not producer_address:
        return jsonify({'message': 'Invalid producer address.'}), 400
    
    try:
        tx = credit_contract.certifyProducer(producer_address, certified, {'from': gov_account})
        tx.wait(1)
        
        action = "CERTIFIED" if certified else "DECERTIFIED"
        log_transaction('REGULATORY', f"Government {action} producer {producer_address[:12]}...", 0, tx.txid)
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'REGULATORY_ACTION',
            gov_account.address,
            producer_address,
            0,
            f"Producer {producer_address[:12]}... has been {action.lower()}"
        )
        
        return jsonify({
            'message': f'Producer has been {action.lower()} successfully.',
            'tx_hash': tx.txid
        })
    except Exception as e:
        return jsonify({'message': f'Certification failed: {str(e)}'}), 400

@app.route('/api/gov/audit', methods=['POST'])
@login_required
def gov_conduct_audit():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can conduct audits.'}), 403
    
    try:
        # Mock AI audit analysis
        audit_results = conduct_mock_ai_audit()
        
        # Log the audit
        log_transaction('AUDIT', f"AI audit conducted - {audit_results['risk_level']} risk level detected", 0, f"audit_{int(datetime.datetime.utcnow().timestamp())}")
        
        return jsonify({
            'message': 'AI audit completed successfully.',
            'summary': audit_results['summary'],
            'risk_level': audit_results['risk_level'],
            'recommendations': audit_results['recommendations']
        })
    except Exception as e:
        return jsonify({'message': f'Audit failed: {str(e)}'}), 400

@app.route('/api/gov/notifications', methods=['GET'])
@login_required
def get_regulatory_notifications():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can view regulatory notifications.'}), 403
    
    notifications_file = 'regulatory_notifications.json'
    if os.path.exists(notifications_file) and os.path.getsize(notifications_file) > 0:
        with open(notifications_file, 'r') as f:
            notifications = json.load(f)
        # Return most recent 50 notifications
        return jsonify(notifications[-50:])
    
    return jsonify([])

@app.route('/api/gov/account-details', methods=['GET'])
@login_required
def get_account_details():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can view account details.'}), 403
    
    address = request.args.get('address')
    if not address:
        return jsonify({'message': 'Address parameter required.'}), 400
    
    try:
        # Find the role for this address
        role = None
        for r, acc in all_accounts.items():
            if acc.address == address:
                role = r
                break
        
        if not role:
            return jsonify({'message': 'Address not found in system.'}), 404
        
        # Get basic account info
        balance = credit_contract.balanceOf(address) / 10**18
        frozen = credit_contract.isAccountFrozen(address)
        
        # Count transactions for this address
        transaction_count = 0
        if os.path.exists('transactions.json') and os.path.getsize('transactions.json') > 0:
            with open('transactions.json', 'r') as f:
                transactions = json.load(f)
            # Count transactions involving this address
            for tx in transactions:
                if address in tx.get('details', ''):
                    transaction_count += 1
        
        account_details = {
            'address': address,
            'role': role,
            'balance': balance,
            'frozen': frozen,
            'transaction_count': transaction_count
        }
        
        # Add role-specific information
        if role == 'producer':
            producer_info = credit_contract.getProducerInfo(address)
            account_details.update({
                'certified': producer_info[0],
                'total_issued': producer_info[1] / 10**18,
                'active': producer_info[3]
            })
        elif role == 'factory':
            factory_info = credit_contract.getFactoryInfo(address)
            account_details.update({
                'has_quota': factory_info[1],
                'quota': factory_info[0] / 10**18 if factory_info[1] else 0,
                'credits_purchased': factory_info[2] / 10**18,
                'quota_met': factory_info[3] if factory_info[1] else False
            })
        
        return jsonify(account_details)
        
    except Exception as e:
        return jsonify({'message': f'Error retrieving account details: {str(e)}'}), 400

@app.route('/api/gov/system-health', methods=['GET'])
@login_required
def get_system_health():
    if session.get('role') != 'government':
        return jsonify({'message': 'Only government officials can view system health.'}), 403
    
    try:
        # Calculate system health metrics
        active_users = len(all_accounts)
        
        # Count daily transactions
        daily_transactions = 0
        if os.path.exists('transactions.json') and os.path.getsize('transactions.json') > 0:
            with open('transactions.json', 'r') as f:
                transactions = json.load(f)
            today = datetime.datetime.utcnow().date()
            daily_transactions = len([tx for tx in transactions if 
                datetime.datetime.fromisoformat(tx['timestamp'].replace('Z', '+00:00')).date() == today])
        
        # Calculate credit utilization
        total_credits = 0
        for role, acc in all_accounts.items():
            total_credits += credit_contract.balanceOf(acc) / 10**18
        
        # Mock credit utilization calculation (percentage of credits in active use)
        credit_utilization = min(85, (daily_transactions * 10) + 20)  # Mock calculation
        
        # Determine overall system status
        alerts = []
        if daily_transactions > 100:
            alerts.append("High transaction volume detected")
        if credit_utilization > 90:
            alerts.append("Credit utilization approaching maximum")
        
        # Check for frozen accounts
        frozen_count = 0
        for role, acc in all_accounts.items():
            if credit_contract.isAccountFrozen(acc):
                frozen_count += 1
        
        if frozen_count > 0:
            alerts.append(f"{frozen_count} account(s) currently frozen")
        
        status = "HEALTHY" if len(alerts) == 0 else "ATTENTION_REQUIRED" if len(alerts) <= 2 else "CRITICAL"
        
        return jsonify({
            'status': status,
            'active_users': active_users,
            'daily_transactions': daily_transactions,
            'credit_utilization': credit_utilization,
            'network_stability': "STABLE",  # Mock value
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({'message': f'Error retrieving system health: {str(e)}'}), 400

@app.route('/api/compliance-report', methods=['GET'])
@login_required
def get_compliance_report():
    if session.get('role') not in ['government', 'state_pollution_body']:
        return jsonify({'message': 'Only government and pollution body officials can view compliance reports.'}), 403
    
    try:
        # Calculate compliance metrics
        total_credits = 0
        active_producers = 0
        factories_with_quotas = 0
        compliant_factories = 0
        frozen_accounts = 0
        
        for role, acc in all_accounts.items():
            balance = credit_contract.balanceOf(acc) / 10**18
            total_credits += balance
            
            if credit_contract.isAccountFrozen(acc):
                frozen_accounts += 1
            
            if role == 'producer':
                producer_info = credit_contract.getProducerInfo(acc.address)
                if producer_info[0] and producer_info[3]:  # certified and active
                    active_producers += 1
            elif role == 'factory':
                factory_info = credit_contract.getFactoryInfo(acc.address)
                if factory_info[1]:  # hasQuota
                    factories_with_quotas += 1
                    if factory_info[3]:  # quotaMet
                        compliant_factories += 1
        
        # Count certificates issued
        certificates_issued = 0
        if os.path.exists('certificates.json') and os.path.getsize('certificates.json') > 0:
            with open('certificates.json', 'r') as f:
                certificates = json.load(f)
            certificates_issued = len(certificates)
        
        # Calculate compliance rate
        compliance_rate = (compliant_factories / factories_with_quotas * 100) if factories_with_quotas > 0 else 100
        
        # Determine system health
        system_health = "EXCELLENT" if compliance_rate >= 90 else "GOOD" if compliance_rate >= 70 else "NEEDS_IMPROVEMENT"
        
        return jsonify({
            'total_credits': total_credits,
            'active_producers': active_producers,
            'factories_with_quotas': factories_with_quotas,
            'compliant_factories': compliant_factories,
            'certificates_issued': certificates_issued,
            'frozen_accounts': frozen_accounts,
            'compliance_rate': round(compliance_rate, 1),
            'system_health': system_health
        })
        
    except Exception as e:
        return jsonify({'message': f'Error generating compliance report: {str(e)}'}), 400



@app.route('/api/pollution/certificate', methods=['POST'])
@login_required
def issue_certificate():
    if session.get('role') != 'state_pollution_body':
        return jsonify({'message': 'Only state pollution bodies can issue certificates.'}), 403
    
    data = request.get_json()
    factory_address = data.get('factory_address')
    
    if not factory_address:
        return jsonify({'message': 'Invalid factory address.'}), 400
    
    try:
        # Check if factory has met quota requirements
        factory_info = credit_contract.getFactoryInfo(factory_address)
        
        if not factory_info[1]:  # hasQuota
            return jsonify({'message': 'Factory has not set an environmental quota.'}), 400
        
        if not factory_info[3]:  # quotaMet
            quota = factory_info[0] / 10**18
            purchased = factory_info[2] / 10**18
            return jsonify({
                'message': f'Factory has not met quota requirements. Progress: {purchased}/{quota} GHC'
            }), 400
        
        # Generate compliance certificate
        certificate_id = f"CERT-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{factory_address[:8].upper()}"
        certificate_data = {
            'certificate_id': certificate_id,
            'factory_address': factory_address,
            'quota_amount': factory_info[0] / 10**18,
            'credits_purchased': factory_info[2] / 10**18,
            'issue_date': datetime.datetime.utcnow().isoformat() + "Z",
            'issued_by': 'State Pollution Control Board',
            'compliance_status': 'QUOTA_MET',
            'benefits_eligible': True
        }
        
        # Save certificate to file
        certificates_file = 'certificates.json'
        certificates = []
        if os.path.exists(certificates_file) and os.path.getsize(certificates_file) > 0:
            with open(certificates_file, 'r') as f:
                certificates = json.load(f)
        certificates.append(certificate_data)
        with open(certificates_file, 'w') as f:
            json.dump(certificates, f, indent=2)
        
        # Log the certificate issuance
        log_transaction(
            'CERTIFICATE', 
            f"Compliance certificate {certificate_id} issued to factory", 
            0, 
            f"cert_{certificate_id}"
        )
        
        # Enhanced monitoring and notification for regulatory bodies
        enhanced_transaction_monitoring(
            'REGULATORY_ACTION',
            all_accounts['state_pollution_body'].address,
            factory_address,
            0,
            f"Compliance certificate {certificate_id} issued - factory eligible for benefits"
        )
        
        return jsonify({
            'message': f'Compliance certificate {certificate_id} issued successfully. Factory is eligible for environmental benefits.',
            'certificate_id': certificate_id,
            'benefits_eligible': True
        })
        
    except Exception as e:
        return jsonify({'message': f'Certificate issuance failed: {str(e)}'}), 400

@app.route('/api/payments', methods=['GET'])
@login_required
def get_payments():
    """Get payment history for the current user"""
    payments_file = 'payments.json'
    user_address = all_accounts[session['role']].address
    
    if os.path.exists(payments_file) and os.path.getsize(payments_file) > 0:
        with open(payments_file, 'r') as f:
            all_payments = json.load(f)
        
        # Filter payments for current user
        user_payments = [p for p in all_payments if p['user_address'] == user_address]
        return jsonify(user_payments)
    
    return jsonify([])

@app.route('/api/certificates', methods=['GET'])
@login_required
def get_certificates():
    """Get certificates for the current user (factories) or all certificates (pollution body)"""
    certificates_file = 'certificates.json'
    user_role = session['role']
    user_address = all_accounts[user_role].address
    
    if os.path.exists(certificates_file) and os.path.getsize(certificates_file) > 0:
        with open(certificates_file, 'r') as f:
            all_certificates = json.load(f)
        
        # If pollution body, return all certificates; if factory, return only their certificates
        if user_role == 'state_pollution_body':
            return jsonify(all_certificates)
        elif user_role == 'factory':
            user_certificates = [c for c in all_certificates if c['factory_address'] == user_address]
            return jsonify(user_certificates)
    
    return jsonify([])

@app.route('/api/pollution/factory-progress', methods=['GET'])
@login_required
def get_factory_progress():
    if session.get('role') != 'state_pollution_body':
        return jsonify({'message': 'Only state pollution bodies can view factory progress.'}), 403
    
    try:
        factory_progress = []
        
        # Get all factory accounts (in a real system, this would query all registered factories)
        for role, acc in all_accounts.items():
            if role == 'factory':
                factory_info = credit_contract.getFactoryInfo(acc.address)
                
                if factory_info[1]:  # hasQuota
                    quota = factory_info[0] / 10**18
                    credits_purchased = factory_info[2] / 10**18
                    progress_percentage = (credits_purchased / quota * 100) if quota > 0 else 0
                    
                    status = "QUOTA_MET" if factory_info[3] else "IN_PROGRESS" if progress_percentage > 0 else "NOT_STARTED"
                    
                    factory_progress.append({
                        'address': acc.address,
                        'quota': quota,
                        'credits_purchased': credits_purchased,
                        'progress_percentage': round(progress_percentage, 1),
                        'status': status,
                        'quota_met': factory_info[3]
                    })
                else:
                    factory_progress.append({
                        'address': acc.address,
                        'quota': 0,
                        'credits_purchased': 0,
                        'progress_percentage': 0,
                        'status': "NO_QUOTA_SET",
                        'quota_met': False
                    })
        
        return jsonify(factory_progress)
        
    except Exception as e:
        return jsonify({'message': f'Error retrieving factory progress: {str(e)}'}), 400

# --- MAIN ---
if __name__ == '__main__':
    if os.path.exists('transactions.json'): os.remove('transactions.json')
    if os.path.exists('payments.json'): os.remove('payments.json')
    if os.path.exists('certificates.json'): os.remove('certificates.json')
    if os.path.exists('regulatory_notifications.json'): os.remove('regulatory_notifications.json')
    print("Starting Green Hydrogen Credit Marketplace Application...")
    app.run(port=5001, debug=True, use_reloader=False)
