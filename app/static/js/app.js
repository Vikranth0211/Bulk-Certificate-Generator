document.addEventListener('DOMContentLoaded', () => {
    // Navigation Tabs
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            navButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.style.display = 'none');
            
            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.tab);
            if (target) target.style.display = 'block';

            if (btn.dataset.tab === 'jobs-panel') {
                loadJobsList();
            }
        });
    });

    // Sample Data Loader
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', () => {
            document.getElementById('jobTitle').value = 'Python & FastAPI Masterclass 2026';
            document.getElementById('eventName').value = 'Advanced Backend Development';
            document.getElementById('issuerName').value = 'Global Software Institute';
            document.getElementById('issueDate').value = 'October 10, 2026';

            const sampleRecipients = [
                { name: "Eleanor Vance", email: "eleanor.vance@example.com" },
                { name: "Marcus Brody", email: "marcus.b@example.org" },
                { name: "Sophia Martinez", email: "sophia.m@domain.com" },
                { name: "   ", email: "invalid-email-format" }, // Intentionally invalid to demonstrate isolated failure handling!
                { name: "Liam O'Connor", email: "liam.oc@techcorp.io" }
            ];

            document.getElementById('recipientsJson').value = JSON.stringify(sampleRecipients, null, 2);
        });
    }

    // Submit JSON Batch Form
    const jsonForm = document.getElementById('jsonBatchForm');
    if (jsonForm) {
        jsonForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('jobTitle').value.trim();
            const event_name = document.getElementById('eventName').value.trim();
            const issuer = document.getElementById('issuerName').value.trim();
            const issue_date = document.getElementById('issueDate').value.trim();
            const rawJson = document.getElementById('recipientsJson').value.trim();

            let recipients;
            try {
                recipients = JSON.parse(rawJson);
            } catch (err) {
                alert('Invalid JSON in Recipients field. Please fix formatting syntax.');
                return;
            }

            const payload = { title, event_name, issuer, issue_date, recipients };
            
            try {
                const res = await fetch('/api/v1/jobs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) {
                    const errData = await res.json();
                    alert(`Error (${res.status}): ${JSON.stringify(errData.detail)}`);
                    return;
                }

                const data = await res.json();
                alert(`Job '${data.title}' created successfully (ID: ${data.job_id}). Switch to Jobs tab to monitor progress.`);
                
                // Switch to jobs panel
                document.querySelector('[data-tab="jobs-panel"]').click();
            } catch (err) {
                alert('Network error submitting job: ' + err.message);
            }
        });
    }

    // Submit CSV Batch Form
    const csvForm = document.getElementById('csvBatchForm');
    if (csvForm) {
        csvForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(csvForm);

            try {
                const res = await fetch('/api/v1/jobs/csv', {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    const errData = await res.json();
                    alert(`CSV Import Error: ${JSON.stringify(errData.detail)}`);
                    return;
                }

                const data = await res.json();
                alert(`CSV Batch Job '${data.title}' created successfully!`);
                csvForm.reset();
                document.querySelector('[data-tab="jobs-panel"]').click();
            } catch (err) {
                alert('CSV Upload Failed: ' + err.message);
            }
        });
    }

    // Verification Form
    const verifyForm = document.getElementById('verifyForm');
    if (verifyForm) {
        verifyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('verifyInput').value.trim();
            if (!query) return;

            const resultDiv = document.getElementById('verifyResult');
            resultDiv.innerHTML = '<p style="color: var(--text-muted)">Verifying certificate authenticity...</p>';

            try {
                const res = await fetch(`/api/v1/certificates/verify/${encodeURIComponent(query)}`);
                const data = await res.json();

                if (data.valid) {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid var(--success); border-radius: 12px; padding: 1.25rem;">
                            <h3 style="color: var(--success); margin-bottom: 0.5rem;">✓ Authentic Certificate Verified</h3>
                            <p><strong>Recipient:</strong> ${data.recipient_name}</p>
                            <p><strong>Event:</strong> ${data.event_name}</p>
                            <p><strong>Issuer:</strong> ${data.issuer}</p>
                            <p><strong>Issue Date:</strong> ${data.issue_date}</p>
                            <p><strong>Verification Code:</strong> <code>${data.verification_code}</code></p>
                            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">SHA-256 Checksum: ${data.checksum}</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid var(--danger); border-radius: 12px; padding: 1.25rem;">
                            <h3 style="color: var(--danger); margin-bottom: 0.5rem;">✕ Verification Failed</h3>
                            <p>${data.message}</p>
                        </div>
                    `;
                }
            } catch (err) {
                resultDiv.innerHTML = `<p style="color: var(--danger)">Verification error: ${err.message}</p>`;
            }
        });
    }

    // Modal Close
    document.querySelectorAll('.close-btn, .modal-backdrop').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target === el) {
                document.getElementById('certModal').classList.remove('active');
            }
        });
    });

    // Auto Polling for Jobs
    setInterval(() => {
        const jobsTab = document.getElementById('jobs-panel');
        if (jobsTab && jobsTab.style.display !== 'none') {
            loadJobsList(false); // silent refresh
        }
    }, 2000);

    // Initial load
    loadJobsList();
});

async function loadJobsList(showSpinner = true) {
    const tableBody = document.getElementById('jobsTableBody');
    if (!tableBody) return;

    try {
        const res = await fetch('/api/v1/jobs');
        if (!res.ok) return;

        const jobs = await res.json();

        if (jobs.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No certificate jobs found. Create your first batch in the Generator tab!</td></tr>`;
            return;
        }

        tableBody.innerHTML = jobs.map(j => {
            const statusClass = `badge-${j.status.toLowerCase()}`;
            return `
                <tr>
                    <td><strong>${escapeHtml(j.title)}</strong><br><small style="color: var(--text-muted)">${escapeHtml(j.event_name)}</small></td>
                    <td><span class="badge ${statusClass}">${j.status}</span></td>
                    <td>
                        <div>${j.processed_count} / ${j.total_count} (${j.progress_percentage}%)</div>
                        <div class="progress-container"><div class="progress-bar" style="width: ${j.progress_percentage}%"></div></div>
                    </td>
                    <td><span style="color: var(--success); font-weight: 600;">${j.success_count}</span></td>
                    <td><span style="color: ${j.failed_count > 0 ? 'var(--danger)' : 'var(--text-muted)'}; font-weight: 600;">${j.failed_count}</span></td>
                    <td>${new Date(j.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                    <td>
                        <div style="display: flex; gap: 0.4rem;">
                            <button class="btn btn-secondary btn-sm" onclick="viewJobDetails('${j.job_id}')">Details</button>
                            ${j.success_count > 0 ? `<a href="/api/v1/jobs/${j.job_id}/download-all" class="btn btn-accent btn-sm" download>ZIP</a>` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        console.error('Error fetching jobs:', err);
    }
}

async function viewJobDetails(jobId) {
    try {
        const res = await fetch(`/api/v1/jobs/${jobId}`);
        if (!res.ok) return;
        const job = await res.json();

        const modal = document.getElementById('certModal');
        const modalBody = document.getElementById('modalBody');

        const recipientRows = job.recipients.map(r => {
            const isSuccess = r.status === 'SUCCESS';
            return `
                <tr>
                    <td><strong>${escapeHtml(r.name)}</strong></td>
                    <td>${r.email ? escapeHtml(r.email) : '-'}</td>
                    <td>
                        <span class="badge ${isSuccess ? 'badge-completed' : 'badge-failed'}">${r.status}</span>
                    </td>
                    <td>
                        ${isSuccess 
                            ? `<button class="btn btn-primary btn-sm" onclick="previewCertificate('${r.certificate_id}')">Preview & Download</button>`
                            : `<span style="color: var(--danger); font-size: 0.85rem;">${escapeHtml(r.error_message || 'Validation Error')}</span>`
                        }
                    </td>
                </tr>
            `;
        }).join('');

        modalBody.innerHTML = `
            <h2 style="font-family: var(--font-heading); margin-bottom: 0.5rem;">Job Details: ${escapeHtml(job.title)}</h2>
            <p style="color: var(--text-muted); margin-bottom: 1.25rem;">Event: ${escapeHtml(job.event_name)} | Issuer: ${escapeHtml(job.issuer)} | Date: ${escapeHtml(job.issue_date)}</p>
            
            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-muted);">Total Recipients</div>
                    <div style="font-size: 1.4rem; font-weight: 700;">${job.total_count}</div>
                </div>
                <div style="flex: 1; background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--success);">Successful</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--success);">${job.success_count}</div>
                </div>
                <div style="flex: 1; background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--danger);">Failed</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--danger);">${job.failed_count}</div>
                </div>
            </div>

            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Recipient</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th>Action / Error Detail</th>
                        </tr>
                    </thead>
                    <tbody>${recipientRows}</tbody>
                </table>
            </div>
        `;

        modal.classList.add('active');
    } catch (err) {
        alert('Failed to fetch job details: ' + err.message);
    }
}

async function previewCertificate(certId) {
    try {
        const res = await fetch(`/api/v1/certificates/${certId}`);
        if (!res.ok) return;
        const cert = await res.json();

        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <h2 style="font-family: var(--font-heading); margin-bottom: 0.5rem;">Certificate Preview</h2>
            <p style="color: var(--text-muted); margin-bottom: 1rem;">Recipient: <strong>${escapeHtml(cert.recipient_name)}</strong></p>

            ${cert.png_download_url ? `<img src="${cert.png_download_url}" class="cert-preview-img" alt="Certificate Preview">` : ''}

            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                <a href="${cert.pdf_download_url}" class="btn btn-primary" download>📄 Download PDF Certificate</a>
                ${cert.png_download_url ? `<a href="${cert.png_download_url}" class="btn btn-secondary" download>🖼️ Download PNG Image</a>` : ''}
            </div>

            <div style="margin-top: 1.5rem; background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 10px; font-size: 0.85rem; color: var(--text-muted);">
                <p><strong>Certificate ID:</strong> ${cert.certificate_id}</p>
                <p><strong>Verification Code:</strong> <code>${cert.verification_code}</code></p>
                <p><strong>SHA-256 Checksum:</strong> ${cert.checksum}</p>
            </div>
        `;
    } catch (err) {
        alert('Error previewing certificate: ' + err.message);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
