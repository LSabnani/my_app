# Workspace Agent Rules: Explainer Knowledge Engine

## Global Rule for Critic Agents' Duties

All agentic evaluations and resource publications must strictly adhere to the Critic Agent Mandate and FMEA Risk Governance defined in [.agents/rules/critic_duties.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/Explainer/.agents/rules/critic_duties.md).

### 1. What Must Go Right?
1. **Pre-Publication Link Verification**: The Critic Agent MUST always check and verify all URLs (`url`, `document_url`, `website_url`, `video_url`, `reference_links`) via live HTTP HEAD/GET before publishing.
2. **CLEATS Zero-Penalty Enforcement**: If any URL fails reachability (404, invalid domain, broken redirect, soft-404), **Transparency (T) MUST be scored as `0.0`**. Any score of `0.0` permanently disqualifies the resource from Best Known Method (BKM) status.
3. **Publication Gatekeeping**: Resources with broken or unverifiable links must NEVER be published in the Top 3 recommendations if verified alternatives exist.
4. **Empirical Triangulation**: Elevation to BKM requires documented proof of 3 replications by 3 distinct practitioners at 3 distinct times with expected outcomes.
5. **Simulated Test Data Protocol & User Agreement Gate**: If test data is not available, the Critic Agent MAY propose simulated data to be used. The Critic Agent MUST NOT proceed with tests on simulated data without explicit user agreement. Upon user consent, testing proceeds with transparent simulated provenance tagging (`provenance: "SIMULATED_DATA"`).

### 2. What Can Go Wrong? (FMEA Risk Assessment & RPN)
Risk Priority Number:
$$\text{RPN} = \text{Severity } (S) \times \text{Occurrence } (O) \times \text{Detectability } (D)$$
* **Severity ($S$, 1–10)**: Financial impact in $ ($50k–$5M) and delay in time (hours to months).
* **Occurrence ($O$, 1–10)**: Likelihood of event happening.
* **Detectability ($D$, 1–10)**: Lack of detectability (hard-to-detect silent failures receive higher scores up to 10).

The Critic Agent actively screens for:
* **RSK-01 (RPN 336):** Hallucinated/synthetic dead links ($8 \times 6 \times 7$) -> Mitigated by live HTTP handshake.
* **RSK-02 (RPN 315):** Soft-404 / content removal masking ($7 \times 5 \times 9$) -> Mitigated by HTML body inspection.
* **RSK-03 (RPN 224):** Bot-shield false-negatives ($8 \times 7 \times 4$) -> Mitigated by institutional domain & DOI recognition.
* **RSK-04 (RPN 144):** Domain expiration & malicious redirection ($9 \times 2 \times 8$) -> Mitigated by redirect chain domain tracking.
* **RSK-05 (RPN 240):** Unconsented Synthetic / Simulated Data Drift ($6 \times 5 \times 8$) -> Mitigated by Mandatory User Agreement Gate.

### 3. Automated Regression Testing (The 3 Circumstances)
The Critic Agent must pass regression tests across 3 distinct circumstances:
* **Circumstance 1:** 100% Active & Healthy Links (RPN = 0, Transparency $\ge 8.5$, BKM Eligible, Top 1 published).
* **Circumstance 2:** Subtle Nested Broken Link (Transparency = 0.0, Zero-Penalty BKM Disqualified, High RPN flagged).
* **Circumstance 3:** Institutional Bot-Shield & Soft-404 Handling (Accurate classification, body inspection, reliable gatekeeping).
