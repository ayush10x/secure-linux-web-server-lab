"""Build the recruiter PDF from curated, verified lab results.

Run: python3 scripts/build-report.py (requires reportlab).
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/secure-linux-web-server-report.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
INK = colors.HexColor("#183143")
GREEN = colors.HexColor("#087961")
PALE = colors.HexColor("#eef5f4")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="LabTitle", fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=INK, spaceAfter=15))
styles.add(ParagraphStyle(name="LabHeading", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=GREEN, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="LabBody", fontName="Helvetica", fontSize=10, leading=14, textColor=INK, spaceAfter=9, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="LabSmall", fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK, spaceAfter=5))
story = []

def p(text, style="LabBody"):
    return Paragraph(text, styles[style])

def section(title, text):
    story.extend([p(title, "LabHeading"), p(text)])

def table(rows, widths):
    data = [[p(str(cell), "LabSmall") for cell in row] for row in rows]
    result = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#cddbdc")),
    ]))
    story.append(result)

story.extend([p("LINUX ADMINISTRATION / PORTFOLIO LAB", "LabSmall"), Spacer(1, 12),
              p("Secure Linux<br/>Web Server", "LabTitle"),
              p("Ayush Kaushik | Validated 10 October 2026", "LabBody")])
section("Project outcome", "Built and validated a two-VM Ubuntu ARM64 lab with Nginx, key-based SSH, source-restricted UFW rules, operational checks, and tested site-backup recovery. Client access works after Server reboot; unauthorized SSH paths are denied.")
table([
    ["Server: kapserver", "Client: ubuntu26"],
    ["Ubuntu 26.04 LTS ARM64<br/>2 CPUs / 3 GB RAM / 25 GB disk", "Ubuntu 26.04 LTS ARM64<br/>2 CPUs / about 4.4 GB RAM / 25 GB disk"],
    ["Host-only IP: 192.168.56.200", "Host-only IP: 192.168.56.201"],
    ["Nginx site + OpenSSH + UFW", "Dedicated Ed25519 key + acceptance checks"],
], [239, 239])
section("Network design", "Apple M2 Pro host running VirtualBox. Both guests use NAT for package downloads and the same host-only network for private lab traffic. Fixed addresses .200 and .201 are outside the DHCP pool. UFW permits TCP 22 from the Client and TCP 80 from the lab subnet; the Mac host's SSH probe is denied.")
section("Skills demonstrated", "Linux accounts and permissions; systemd service management; Netplan and NetworkManager; OpenSSH policy validation; UFW; log interpretation; Bash automation; checksum-backed recovery; GitHub CI and technical documentation.")
section("Scope", "Private-network learning lab serving static HTTP. No public endpoint, production TLS, high availability or production-experience claim. The trusted Mac/Client and source-IP restriction do not defend against host or key compromise; see the threat model.")

story.append(PageBreak())
story.append(p("Validation and controls", "LabTitle"))
table([
    ["Test", "Observed result"],
    ["Client web access", "HTTP 200; missing page 404; requests appear in the site's log."],
    ["Administrator key + sudo", "Fresh key session authenticates ayush; sudo returns root."],
    ["SSH policy evidence", "Effective daemon settings disable root/password/interactive access; account-denial logs and Client probes support this."],
    ["Firewall restriction", "Default deny incoming; only the intended SSH and HTTP rules. Mac-host SSH times out with UFW block evidence."],
    ["Health and recovery", "Health exit 0; SHA-256 archive check OK; temporary restore diff exit 0."],
    ["Server reboot", "Client HTTP 200 and fresh key access return; root/password denials persist."],
    ["Package integrity", "APT refresh/upgrade exit 0; dpkg audit empty. Four packages deferred by Ubuntu phasing."],
], [146, 332])
section("Security decisions", "The named sudo administrator is separate from a locked regular account. Site ownership is root:www-data with a 0750 directory and 0640 HTML file. The Client SSH directory and Server authorized_keys use 0700 and 0600 permissions. No private keys or passwords are published.")
section("SSH precedence", "The lab policy is installed as 00-lab-hardening.conf, before Ubuntu's 50-cloud-init.conf. OpenSSH uses the first value obtained for these directives, so effective settings were inspected with sshd -T before reloading. Key login and sudo were proven before password authentication was disabled.")
section("Evidence boundary", "CI checks Bash syntax, ShellCheck, required artifacts and offline fixtures. VM tests are separate. The original BatchMode password probe alone did not prove policy; effective settings support it. Revised tests reject transport/host-key failures and inspect offered methods; new coverage is offline, not a guest rerun or security certification.")

story.append(PageBreak())
story.append(p("Operations and lessons", "LabTitle"))
section("Recovery workflow", "The backup tool creates a root-only site archive and SHA-256 checksum. Validation checks the checksum and compares a temporary extraction with the live site. Baseline and powered-off configured snapshots support rollback. Live snapshotting stalled; cold-restart recovery was approved and access tests passed again. The Client snapshot predates its profile-priority fix; see the operations guide.")
section("Troubleshooting", "Replaced an incompatible AMD64 installer with ARM64. Worked around a stalled Client GUI frontend using headless boot and SSH. Corrected SSH drop-in precedence. After a long pause, corrected stale guest time and restarted chrony so APT metadata validation could succeed without bypassing its checks.")
section("Known limitations", "The Client's headless boot and SSH work, but its GUI launch issue remains. Chrony had no selected source at final inspection; ongoing NTP synchronization is not claimed. HTTP is isolated-lab only. The dedicated key is unencrypted. Backups are local and cover site content; full disaster recovery, scheduled backups, TLS, and centralized monitoring are future work.")
section("Portfolio use", "Suggested resume entry: Built and validated an assisted two-VM Ubuntu ARM64 web-server lab using Nginx, Ed25519 SSH authentication, and source-restricted UFW rules. Automated health and backup checks, verified checksum-based recovery, and documented positive and negative tests with GitHub CI.")
section("Ownership and assistance", "Built for Ayush Kaushik with Codex assistance for setup, troubleshooting, scripts, and documentation. The owner should explain and reproduce the implementation before presenting it as personal expertise. The project demonstrates lab practice, not production employment experience.")
section("Repository and further reading", '<link href="https://github.com/ayush10x/secure-linux-web-server-lab" color="#087961">github.com/ayush10x/secure-linux-web-server-lab</link><br/>README, project report, recruiter brief, verification evidence, setup guide, operations guide, and separate action/decision log.')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GREEN)
    canvas.line(58, 43, A4[0] - 58, 43)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK)
    canvas.drawString(58, 29, "Ayush Kaushik | Secure Linux Web Server Lab")
    canvas.drawRightString(A4[0] - 58, 29, f"{doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=58, leftMargin=58,
                        topMargin=48, bottomMargin=62, title="Secure Linux Web Server Lab",
                        author="Ayush Kaushik", subject="Validated Linux administration portfolio lab")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
