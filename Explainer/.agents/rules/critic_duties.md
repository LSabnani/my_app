# Global Rule: Critic Agent Duties, "What Must Go Right", and FMEA Risk Governance

## 1. Core Mandate: "What Must Go Right?"

The **Critic Agent (Evaluator / CLEATS Gatekeeper)** is the definitive arbiter of empirical truth, transparency, and link reachability before any candidate resource, architectural blueprint, or Best Known Method (BKM) is published to end users.

### The Four Non-Negotiable Requirements ("What Must Go Right")

1. **Pre-Publication Active Link Verification**:
   - The Critic MUST actively probe and verify every link attached to a candidate resource (`url`, `document_url`, `website_url`, `video_url`, and all entries in `reference_links`) using concurrent HTTP requests before ranking or publishing.
   - Passive string validation or regex syntax checks are STRICTLY INSUFFICIENT; the destination route must respond with a reachable HTTP status (200, 30x, or recognized bot-protected gateway 401/403).

2. **CLEATS Zero-Penalty Enforcement**:
   - If any URL fails reachability (404 Not Found, DNS resolution failure, connection drop, or soft-404), **Transparency (T) MUST be assigned a strict score of `0.0`**.
   - Under the CLEATS Zero-Penalty Rule:
     $$\text{Any Metric} = 0.0 \implies \text{Strictly Disqualified from Best Known Method (BKM) status}$$
     *"ZEROS cannot contribute to BKMs."*

3. **Publishing Gatekeeping**:
   - Candidates with broken or unverifiable links must NEVER be published in the Top 3 recommendations if verified alternatives exist.
   - Any resource failing link audit must be flagged with `critic_verified = False` and clear audit diagnostics indicating the dead URL.

4. **Triangulated Empirical Replication (Rule of 3)**:
   - For a method to be elevated to an official BKM template, it must have documented evidence of **3 distinct practitioners at 3 distinct time windows** achieving the predicted outcome with zero error spikes.

5. **Simulated Test Data Protocol & User Agreement Gate**:
   - If empirical test data (telemetry, live replication traces, benchmark metrics, or candidate slide decks) is **not available or unmeasurable**:
     - The Critic Agent **MAY propose simulated data / synthetic test fixtures** to be used.
     - **MANDATORY GATE:** The Critic MUST NEVER execute tests on simulated data unilaterally. The Critic must present the simulated dataset proposal (scope, generation methodology, parameter bounds, and rationale) to the user.
     - **ONLY after explicit user agreement / consent** may the Critic proceed with the test.
     - Once approved by the user, the test proceeds with transparent simulated provenance tagging (`provenance: "SIMULATED_DATA"`, `user_agreed: true`).
     - **Integrity Rule:** Simulated data CANNOT unilaterally elevate a candidate to an official Best Known Method (BKM); BKM elevation strictly requires 3 real-world empirical replications.

---

## 2. Risk Engineering: "What Can Go Wrong?" (FMEA & RPN Assessment)

The Critic Agent operates under **Failure Mode and Effects Analysis (FMEA)** to continuously guard against systemic risks.

### Risk Priority Number (RPN) Formula

$$\text{RPN} = \text{Severity } (S) \times \text{Occurrence } (O) \times \text{Detectability } (D)$$

Where:
* **Severity ($S$, 1–10):** Worst-case real-world damage measured in **financial loss ($)** and **project delay (time)**.
* **Occurrence ($O$, 1–10):** Likelihood or frequency of the risk event happening without active Critic intervention.
* **Detectability ($D$, 1–10):** **Inverse detectability** before publication. **Critical Rule: If a risk trigger is silent or difficult to detect, its lack of detectability gets a HIGHER score ($D \to 10$)**.

### Comprehensive Critic FMEA Risk Matrix

| Risk ID | Failure Mode (What can go wrong?) | Worst That Can Happen (Realized Risk) | Impact in $ & Time (Severity $S$) | Probability ($O$) | How Risk Becomes Visible (Tell-Tale Signs) | Lack of Detectability ($D$) | RPN ($S \times O \times D$) | Critic Countermeasure / Gatekeeper Mandate |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| **RSK-01** | **Hallucinated / Synthetic Dead URLs**<br>AI/Harvester generates fictitious file paths (e.g. `/cable-manufacturing-should-cost-model-architecture-deepdive.pptx`). | Executive or procurement engineer attempts to verify should-cost calculations in high-stakes vendor negotiation; link 404s. Model cannot be defended; vendor overcharges or contract collapses. | **$500,000 – $1,500,000** procurement loss; **8–12 weeks** renegotiation slip.<br>($S = 8$) | **6** (Frequent in generative workflows without live web checks) | User browser renders 404 page; browser network log records HTTP 404; user reports dead reference link. | **7** (Syntactically looks like a valid `.pptx` URL; completely invisible without live HTTP handshake) | **336** | **Mandatory Active Probe:** Critic executes live HTTP HEAD/GET handshake on all candidate URLs before ranking. |
| **RSK-02** | **Soft-404 & Content Removal Masking**<br>Host server returns HTTP 200 OK, but page body contains "Item has been removed", "Slide not found", or generic portal home. | Engineering team relies on "verified" BKM template during an emergency infrastructure migration; link lands on a deleted asset page during a live outage. | **$100,000 – $450,000** production downtime; **24–72 hours** emergency remediation.<br>($S = 7$) | **5** (Common on legacy deck-sharing platforms) | Browser displays "Presentation removed"; page title is generic login/404; Content-Length < 1.5 KB. | **9** (Extremely hard to detect via HTTP status code alone since status is 200 OK) | **315** | **Body Content Inspection:** Critic scans response HTML for soft-404 strings ("not found", "removed", "no longer available") and validates payload size. |
| **RSK-03** | **Bot-Shield False Negative (Cloudflare 403 on Elsevier/ScienceDirect)**<br>Automated scraper receives 403 Forbidden from publisher bot defense; Critic mistakes it for dead paper. | Ground-truth peer-reviewed empirical benchmarks are falsely disqualified; team adopts an unverified amateur blog instead, introducing latent architectural bugs. | **$250,000 – $1,000,000** in architectural rework and technical debt; **3–5 months** delayed feature rollout.<br>($S = 8$) | **7** (Elsevier/ScienceDirect aggressively challenge automated bots) | Programmatic client gets 403; response contains `CF-RAY` or `server: cloudflare`; link opens perfectly in human browser. | **4** (Status 403 is immediately visible in logs, but easily misclassified as dead) | **224** | **Domain & DOI Verification:** Critic recognizes protected publisher domains and verifies academic papers via Crossref REST API and DOI resolution (`https://doi.org/...`). |
| **RSK-04** | **Domain Expiry & Malicious Redirect**<br>Author domain expires; domain squatter redirects traffic to spam or malicious payload. | Enterprise user clicks "verified" link in the Explainer tool, leading to credential theft, malware drive-by, or infosec compliance audit violation. | **$1,000,000 – $5,000,000** security breach remediation, forensic investigation, and audit penalties; **6+ months** remediation.<br>($S = 9$) | **2** (Rare for curated top-tier repositories, but high risk over time) | Destination URL hostname changes abruptly (e.g. `tech-example.org` redirects to `spam-casino.xyz`); SSL cert domain mismatch. | **8** (Redirect chain returns 200 at destination; requires domain shift tracking) | **144** | **Redirect Shift Detection:** Critic tracks redirect chains (`r.url.host`) and flags cross-domain redirection to untrusted domains. |
| **RSK-05** | **Unconsented Simulated Data Drift**<br>Critic runs evaluations on synthetic data without user consent; results diverge from customer operational reality. | Engineering decisions committed based on synthetic assumptions; production system fails under live stress because simulated inputs did not mirror production edge cases. | **$200,000 – $600,000** architectural rework; **4–8 weeks** unplanned redesign.<br>($S = 6$) | **5** (Common when benchmark data is unavailable) | Telemetry shows synthetic distribution markers; discrepancies between lab benchmarks and field telemetry; unflagged synthetic provenance. | **8** (Synthetic data appears statistically clean and valid unless provenance is audited) | **240** | **Mandatory User Agreement Gate:** Critic must formally present simulated data proposal and await explicit user agreement before testing. |

---

## 3. Mandatory Testing Verification (The 3 Circumstances)

To confirm compliance with this rule, the Critic Agent MUST pass automated regression tests across **3 distinct real-world circumstances**:

1. **Circumstance 1: All Links 100% Active & Healthy**
   - Inputs: Candidate with verified presentation, video, and paper URLs.
   - Expected: Critic verifies all URLs (HTTP 200), awards Transparency $\ge 8.5$, preserves BKM eligibility, ranks #1 for publication.
2. **Circumstance 2: Subtle Deep Broken Link in Reference Array**
   - Inputs: Candidate whose top-level URL is active, but a secondary `document_url` or nested `reference_links` URL returns 404/DNS error.
   - Expected: Critic catches the nested failure, marks `critic_verified = False`, zeroes Transparency ($T = 0.0$), disqualifies from BKM, and prevents publication in top rank.
3. **Circumstance 3: Bot-Shielded Institutional Domain & Soft-404 Detection**
   - Inputs: Candidate with Cloudflare-protected publisher link (HTTP 403) and another with a soft-404 payload ("Page not found" with HTTP 200).
   - Expected: Critic accurately distinguishes institutional bot-shielding from true dead links, detects soft-404 bodies, and assigns correct RPN and Transparency scores.
