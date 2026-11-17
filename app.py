import os
import hashlib
import mimetypes
import json
from flask import Flask, render_template_string, request, redirect, url_for, flash, Response
from web3 import Web3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

app = Flask(__name__)
app.secret_key = "mobilechain_guard_forensic_secret"

# --- CONFIGURATION ---
RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
def get_web3_contract():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        return None, None
    
    artifact_path = os.path.join("artifacts", "contracts", "EvidenceRegistry.sol", "EvidenceRegistry.json")
    if not os.path.exists(artifact_path):
        return w3, None
    
    with open(artifact_path, "r") as f:
        abi = json.load(f)["abi"]
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
    return w3, contract

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def parse_blockchain_error(e):
    """Extracts clean human-readable error messages from raw Web3/Solidity exceptions."""
    err_str = str(e)
    if "reverted with reason string" in err_str:
        try:
            start = err_str.index("reverted with reason string '") + len("reverted with reason string '")
            end = err_str.index("'", start)
            return err_str[start:end]
        except Exception:
            pass
    if "execution reverted" in err_str:
        return "Smart contract execution reverted. Check your inputs or case ID."
    if "could not connect" in err_str or "Connection refused" in err_str:
        return "Blockchain Connection Error: Is 'npx hardhat node' running?"
    return err_str

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MobileChain-Guard | Forensic Triage & Audit Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #141414; color: #f8fafc; margin: 0; padding: 30px; }
        .container { max-width: 1000px; margin: auto; background: #171717; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top: 0; }
        h2 { color: #38bdf8; font-size: 1.2rem; margin-top: 0; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #242424; padding: 20px; border-radius: 8px; margin-top: 15px; border: 1px solid #334155; }
        label { display: block; margin-top: 10px; font-weight: bold; color: #94a3b8; font-size: 0.9rem; }
        input[type="text"], select { width: 100%; padding: 10px; margin-top: 5px; background: #1e293b; border: 1px solid #475569; color: #fff; border-radius: 6px; box-sizing: border-box; }
        button { background: #0284c7; color: white; border: none; padding: 12px 20px; margin-top: 15px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
        button:hover { background: #0ea5e9; }
        .btn-green { background: #16a34a; }
        .btn-green:hover { background: #15803d; }
        .btn-purple { background: #7c3aed; display: inline-block; text-align: center; text-decoration: none; padding: 12px 20px; margin-top: 15px; border-radius: 6px; color: white; font-weight: bold; width: 100%; box-sizing: border-box; }
        .btn-purple:hover { background: #6d28d9; }
        .success { background: rgba(22, 163, 74, 0.2); border: 1px solid #16a34a; padding: 15px; border-radius: 6px; margin-top: 15px; }
        .alert { background: rgba(220, 38, 38, 0.2); border: 1px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 15px; }
        .badge { display: inline-block; padding: 4px 8px; font-size: 12px; font-weight: bold; border-radius: 4px; background: #334155; color: #38bdf8; }
        code { background: #090d16; padding: 2px 6px; border-radius: 4px; color: #38bdf8; word-break: break-all; }
        hr { border: 0; border-top: 1px solid #334155; margin: 25px 0; }
        .flash-success { background: rgba(22, 163, 74, 0.2); border: 1px solid #16a34a; color: #4ade80; padding: 12px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #16a34a; word-break: break-word; font-weight: 500; }
        .flash-error { background: rgba(220, 38, 38, 0.2); border: 1px solid #dc2626; color: #fca5a5; padding: 12px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #dc2626; word-break: break-word; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MobileChain-Guard Forensic Suite</h1>
        <p>Automated Android Evidence Triage, Blockchain Anchoring & Chain-of-Custody Audit System</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, msg in messages %}
              <div class="{{ 'flash-success' if category == 'success' else 'flash-error' }}">
                {{ '' if category == 'success' else '⚠️' }} {{ msg }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="grid">
            <!-- Left Column: Evidence Ingestion & Registration -->
            <div class="card">
                <h2>Ingest & Register Evidence</h2>
                <form method="POST" action="/register">
                    <label>Case ID:</label>
                    <input type="text" name="case_id" placeholder="e.g., CASE-2026-MOB-090" required>
                    
                    <label>Local File Path / Extracted Artifact:</label>
                    <input type="text" name="file_path" placeholder="e.g., mmssms.db or evidence.png" required>
                    
                    <label>Examiner ID:</label>
                    <input type="text" name="examiner_id" value="EXAM-9021" required>
                    
                    <label>Android Device ID / Serial:</label>
                    <input type="text" name="android_id" value="droid_14_98234" required>

                    <label>Device IMEI Hash:</label>
                    <input type="text" name="imei_hash" value="sha256_imei_mock_abc123" required>

                    <button type="submit" class="btn-green">Compute Hash & Anchor On-Chain</button>
                </form>
            </div>

            <!-- Right Column: Integrity Verification -->
            <div class="card">
                <h2>Verify Evidence Integrity</h2>
                <form method="POST" action="/verify">
                    <label>Case ID to Verify:</label>
                    <input type="text" name="case_id" placeholder="e.g., CASE-2026-MOB-089" required>
                    
                    <label>Current Evidence File Path:</label>
                    <input type="text" name="file_path" placeholder="e.g., mmssms.db" required>
                    
                    <button type="submit">Run Tamper-Detection Check</button>
                </form>

                <hr>

                <h2>Chain-of-Custody Transfer</h2>
                <form method="POST" action="/transfer">
                    <label>Case ID:</label>
                    <input type="text" name="case_id" placeholder="e.g., CASE-2026-MOB-089" required>
                    
                    <label>New Custodian Ethereum Address:</label>
                    <input type="text" name="new_handler" placeholder="0x..." required>

                    <label>Transfer Notes / Reason:</label>
                    <input type="text" name="notes" placeholder="Transferred to Forensic Lab Section B" required>
                    
                    <button type="submit" style="background: #d97706;">Log Custody Transfer</button>
                </form>
            </div>
        </div>

        {% if audit_result %}
        <div class="card" style="margin-top: 25px;">
            <h2>Audit Report & File Analysis</h2>
            <p><strong>Case ID:</strong> <span class="badge">{{ audit_result.case_id }}</span></p>
            <p><strong>File Type Detected:</strong> <span class="badge">{{ audit_result.file_type }}</span></p>
            <p><strong>Computed SHA-256 Hash:</strong> <code>{{ audit_result.current_hash }}</code></p>
            <p><strong>On-Chain Baseline Hash:</strong> <code>{{ audit_result.onchain_hash }}</code></p>
            
            {% if audit_result.verified %}
                <div class="success">
                    <h3>[SUCCESS] INTEGRITY VERIFIED: Evidence is AUTHENTIC</h3>
                    <p><strong>Examiner ID:</strong> {{ audit_result.examiner_id }}</p>
                    <p><strong>Android Device ID:</strong> {{ audit_result.android_id }}</p>
                    <p><strong>Submitting Blockchain Address:</strong> {{ audit_result.examiner_addr }}</p>
                    <p><strong>On-Chain Timestamp:</strong> {{ audit_result.timestamp }}</p>
                </div>
            {% else %}
                <div class="alert">
                    <h3>[ALERT] TAMPERING DETECTED: Hash Mismatch!</h3>
                    <p>The file contents have been modified or altered since initial seizure and registration.</p>
                </div>
            {% endif %}

            <a href="/export/{{ audit_result.case_id }}?file_path={{ audit_result.file_path }}" class="btn-purple">📥 Download Courtroom Audit Report (PDF)</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/verify", methods=["POST"])
def verify():
    case_id = request.form.get("case_id")
    file_path = request.form.get("file_path")
    
    if not os.path.exists(file_path):
        flash(f"File Error: '{file_path}' not found on server.", 'error')
        return redirect(url_for('index'))
    
    current_hash = compute_sha256(file_path)
    file_type, _ = mimetypes.guess_type(file_path)
    file_type = file_type or "Unknown / Binary Asset"
    
    w3, contract = get_web3_contract()
    if not contract:
        flash("Blockchain Error: Could not connect to node or contract artifact missing.", 'error')
        return redirect(url_for('index'))
    
    try:
        res = contract.functions.getEvidenceDetails(case_id).call()
        onchain_hash = res[0]
        android_id = res[2]
        os_version = res[3]
        examiner_id = res[4]
        timestamp = res[5]
        examiner_addr = res[6]
        
        verified = (onchain_hash.strip().lower() == current_hash.strip().lower())
        
        audit_result = {
            "case_id": case_id,
            "file_type": file_type,
            "current_hash": current_hash,
            "onchain_hash": onchain_hash,
            "verified": verified,
            "android_id": android_id,
            "examiner_id": examiner_id,
            "timestamp": timestamp,
            "examiner_addr": examiner_addr,
            "file_path": file_path
        }
        return render_template_string(HTML_TEMPLATE, audit_result=audit_result)
    except Exception as e:
        clean_msg = parse_blockchain_error(e)
        flash(f"Verification Error: {clean_msg}", 'error')
        return redirect(url_for('index'))

@app.route("/export/<case_id>", methods=["GET"])
def export_report(case_id):
    file_path = request.args.get("file_path", "mmssms.db")
    if not os.path.exists(file_path):
        flash(f"Export Error: Evidence file '{file_path}' not found.", 'error')
        return redirect(url_for('index'))
    
    current_hash = compute_sha256(file_path)
    w3, contract = get_web3_contract()
    if not contract:
        flash("Blockchain Error: Could not connect to node.", 'error')
        return redirect(url_for('index'))
    
    try:
        res = contract.functions.getEvidenceDetails(case_id).call()
        onchain_hash = res[0]
        imei_hash = res[1]
        android_id = res[2]
        os_version = res[3]
        examiner_id = res[4]
        timestamp = res[5]
        examiner_addr = res[6]
        
        verified = (onchain_hash.strip().lower() == current_hash.strip().lower())
        status_text = "AUTHENTIC (INTEGRITY VERIFIED)" if verified else "TAMPERED (HASH MISMATCH DETECTED)"
        status_color = colors.HexColor("#16a34a") if verified else colors.HexColor("#dc2626")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#0284c7"), spaceAfter=4)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=15)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#334155"), spaceBefore=10, spaceAfter=6)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#1e293b"), leading=12)
        code_style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#0f172a"), fontName="Courier", leading=10)

        elements.append(Paragraph("MOBILECHAIN-GUARD", title_style))
        elements.append(Paragraph("Official Forensic Audit & Courtroom Report", subtitle_style))
        
        data = [
            [Paragraph("<b>Case ID:</b>", body_style), Paragraph(case_id, body_style)],
            [Paragraph("<b>Audit Timestamp:</b>", body_style), Paragraph(str(timestamp), body_style)],
            [Paragraph("<b>Verification Status:</b>", body_style), Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", body_style)]
        ]
        t = Table(data, colWidths=[130, 400])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1"))
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("Cryptographic Hash Analysis", section_style))
        hash_data = [
            [Paragraph("<b>On-Chain Baseline Hash</b>", body_style), Paragraph(onchain_hash, code_style)],
            [Paragraph("<b>Runtime Computed Hash</b>", body_style), Paragraph(current_hash, code_style)]
        ]
        t_hash = Table(hash_data, colWidths=[130, 400])
        t_hash.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1"))
        ]))
        elements.append(t_hash)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("Device Seizure & Examiner Metadata", section_style))
        meta_data = [
            [Paragraph("<b>Android Device ID / Serial</b>", body_style), Paragraph(android_id, body_style)],
            [Paragraph("<b>Device OS Version</b>", body_style), Paragraph(os_version, body_style)],
            [Paragraph("<b>Hashed IMEI Identifier</b>", body_style), Paragraph(imei_hash, code_style)],
            [Paragraph("<b>Examiner Badge / ID</b>", body_style), Paragraph(examiner_id, body_style)],
            [Paragraph("<b>Submitting Address (ETH)</b>", body_style), Paragraph(examiner_addr, code_style)]
        ]
        t_meta = Table(meta_data, colWidths=[130, 400])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1"))
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("<i>[NOTE]: This cryptographic report is generated automatically by MobileChain-Guard and anchored to an immutable Ethereum smart contract ledger for courtroom presentation.</i>", ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#64748b"))))

        doc.build(elements)
        buffer.seek(0)

        response = Response(buffer.getvalue(), mimetype="application/pdf")
        response.headers["Content-Disposition"] = f"attachment; filename=Audit_Report_{case_id}.pdf"
        return response
    except Exception as e:
        clean_msg = parse_blockchain_error(e)
        flash(f"PDF Report Generation Error: {clean_msg}", 'error')
        return redirect(url_for('index'))

@app.route("/register", methods=["POST"])
def register():
    case_id = request.form.get("case_id")
    file_path = request.form.get("file_path")
    examiner_id = request.form.get("examiner_id")
    android_id = request.form.get("android_id")
    imei_hash = request.form.get("imei_hash")
    
    if not os.path.exists(file_path):
        flash(f"File Error: Evidence file '{file_path}' not found.", 'error')
        return redirect(url_for('index'))
    
    file_hash = compute_sha256(file_path)
    w3, contract = get_web3_contract()
    if not contract:
        flash("Blockchain Error: Could not connect to local node.", 'error')
        return redirect(url_for('index'))
    
    try:
        sender_account = w3.eth.accounts[0]
        tx_hash = contract.functions.registerEvidence(
            case_id,
            file_hash,
            imei_hash,
            android_id,
            "Android 14",
            examiner_id
        ).transact({'from': sender_account})
        
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash(f"SUCCESS: Evidence {case_id} registered and anchored on-chain with hash {file_hash[:12]}...", 'success')
    except Exception as e:
        clean_msg = parse_blockchain_error(e)
        flash(f"Registration Error: {clean_msg}", 'error')
        
    return redirect(url_for('index'))

@app.route("/transfer", methods=["POST"])
def transfer():
    case_id = request.form.get("case_id")
    new_handler = request.form.get("new_handler")
    notes = request.form.get("notes")
    
    w3, contract = get_web3_contract()
    if not contract:
        flash("Blockchain Error: Could not connect to local node.", 'error')
        return redirect(url_for('index'))
    
    try:
        sender_account = w3.eth.accounts[0]
        tx_hash = contract.functions.transferCustody(
            case_id,
            Web3.to_checksum_address(new_handler),
            notes
        ).transact({'from': sender_account})
        
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash(f"SUCCESS: Custody for case {case_id} transferred to {new_handler[:8]}...", 'success')
    except Exception as e:
        clean_msg = parse_blockchain_error(e)
        flash(f"Custody Transfer Error: {clean_msg}", 'error')
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)