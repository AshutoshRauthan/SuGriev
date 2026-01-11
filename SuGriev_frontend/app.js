// =============================================================================
// SUGRIEV - PUBLIC GRIEVANCE PORTAL
// Application Logic
// =============================================================================

// User context (managed by session storage and API)
const currentUser = {
    role: "admin",
    name: "Admin User"
};

// =============================================================================
// DASHBOARD FUNCTIONS
// =============================================================================

/**
 * Renders the admin dashboard with statistics and complaints table
 * Called when dashboard.html is loaded
 */
async function renderDashboard() {
    try {
        // Show loading state?

        // Fetch stats and complaints
        const [stats, complaints] = await Promise.all([
            API.getDashboardStats(),
            API.getComplaints(5) // Get recent 5
        ]);

        // Update statistics cards
        document.getElementById('total-count').textContent = stats.total_complaints || 0;
        document.getElementById('pending-count').textContent = stats.pending || 0;
        document.getElementById('progress-count').textContent = stats.in_progress || 0;
        document.getElementById('critical-count').textContent = stats.high_critical || 0;

        // Render complaints table
        renderComplaintsTable(complaints);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        // Could show error message on UI
    }
}

/**
 * Renders the complaints table
 * @param {Array} complaints - List of complaints
 */
function renderComplaintsTable(complaints) {
    const tbody = document.getElementById('complaints-tbody');
    if (!tbody) return;

    // Clear existing rows
    tbody.innerHTML = '';

    if (!complaints || complaints.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No complaints found</td></tr>';
        return;
    }

    // Create table rows for each complaint
    // Create table rows for each complaint
    complaints.forEach(complaint => {
        const row = document.createElement('tr');

        // Backend Response Schema for get_admin_complaints:
        // { complaint_number, department, district, urgency, status, date }

        const id = complaint.complaint_number || complaint.id;
        const dept = complaint.department || 'N/A';
        const district = complaint.district || (complaint.complaint && complaint.complaint.complaint_district) || 'N/A';
        // 'urgency' in list view, 'urgency_level' in detail view
        const urgency = complaint.urgency || complaint.urgency_level || 'Low';
        const status = complaint.status || 'Pending';
        // 'date' in list view, 'created_at' in detail view
        const date = complaint.date || complaint.created_at || complaint.created_date || 'N/A';
        const similar = complaint.similar_complaints_count || complaint.similar_count || 0;

        row.innerHTML = `
            <td>
                <a href="detail.html?id=${id}" class="complaint-id">
                    ${id}
                </a>
            </td>
            <td>${dept}</td>
            <td>${district}</td>
            <td>${getUrgencyBadge(urgency)}</td>
            <td>${getStatusBadge(status)}</td>
            <td style="text-align:center; font-weight:bold;">${similar}</td>
            <td>${formatDate(date)}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Helper to format date
 */
function formatDate(dateString) {
    if (!dateString || dateString === 'N/A') return 'N/A';
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString; // Invalid date, return as is string
        return date.toLocaleDateString('en-GB', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

/**
 * Returns HTML for urgency badge with appropriate styling
 * @param {string} level - Urgency level (Low, Medium, High, Critical)
 * @returns {string} HTML string for badge
 */
function getUrgencyBadge(level) {
    const levelLower = level ? level.toLowerCase() : 'low';
    return `<span class="badge badge--${levelLower}">${level || 'Low'}</span>`;
}

/**
 * Returns HTML for status badge with appropriate styling
 * @param {string} status - Status (Pending, In Progress, Resolved)
 * @returns {string} HTML string for badge
 */
function getStatusBadge(status) {
    if (!status) return '';
    const lowerStatus = status.toLowerCase();

    let badgeClass = 'pending';
    if (lowerStatus === 'in progress' || lowerStatus === 'in_progress') badgeClass = 'progress';
    if (lowerStatus === 'resolved') badgeClass = 'resolved';

    // Capitalize for display if needed
    // const displayStatus = status.charAt(0).toUpperCase() + status.slice(1);

    return `<span class="badge badge--${badgeClass}">${status}</span>`;
}

// =============================================================================
// COMPLAINT DETAIL FUNCTIONS
// =============================================================================

/**
 * Renders the complaint detail page with data for a specific complaint
 * @param {string} complaintId - The complaint ID to display
 */
async function renderComplaintDetails(complaintId) {
    try {
        const complaint = await API.getComplaintDetails(complaintId);

        if (!complaint) {
            console.error('Complaint not found:', complaintId);
            // Optionally redirect or show error
            document.querySelector('.main').innerHTML = '<div style="text-align:center; padding: 2rem;"><h2>Complaint not found</h2></div>';
            return;
        }

        // Update page header
        document.getElementById('complaint-id-header').textContent = complaint.complaint_number;

        // Update urgency banner
        updateUrgencyBanner({
            level: complaint.urgency_level,
            score: complaint.urgency_score
        });

        // Update complainant information
        document.getElementById('complainant-name').textContent =
            `${complaint.first_name} ${complaint.last_name}`;
        document.getElementById('complainant-email').textContent = complaint.email;
        document.getElementById('complainant-mobile').textContent = complaint.mobile;
        document.getElementById('complainant-gender').textContent = complaint.gender;

        // Update location details
        document.getElementById('location-district').textContent = complaint.district;
        document.getElementById('location-block').textContent = complaint.block || '-';
        document.getElementById('location-village').textContent = complaint.village_city || '-';
        document.getElementById('location-pincode').textContent = complaint.pincode || '-';
        document.getElementById('location-address').textContent = complaint.address;

        // Update complaint description
        document.getElementById('complaint-description').textContent = complaint.description;

        // Update status & urgency section
        const urgencyLevel = complaint.urgency_level || 'Low';
        document.getElementById('urgency-badge').textContent = urgencyLevel;
        document.getElementById('urgency-badge').className =
            `badge badge--${urgencyLevel.toLowerCase()}`;
        document.getElementById('urgency-score-text').textContent =
            `Score: ${complaint.urgency_score}/100`;

        document.getElementById('status-badge').textContent = complaint.status;
        updateStatusBadgeClass('status-badge', complaint.status);

        // Set status dropdown value
        const statusSelect = document.getElementById('status-update');
        if (statusSelect) {
            let statusValue = complaint.status.toLowerCase();
            // Map status text to value if needed. Assuming select options are: pending, in_progress, resolved
            if (statusValue === 'in progress') statusValue = 'in_progress';

            // Iterate options to find match (safe way)
            for (let i = 0; i < statusSelect.options.length; i++) {
                if (statusSelect.options[i].value === statusValue) {
                    statusSelect.selectedIndex = i;
                    break;
                }
            }

            // Add event listener for status change
            // Remove existing listener (clone node trick)
            const newStatusSelect = statusSelect.cloneNode(true);
            statusSelect.parentNode.replaceChild(newStatusSelect, statusSelect);

            // Retry logic helper
            const updateStatusWithRetry = async (id, status, retries = 3) => {
                try {
                    await API.updateComplaintStatus(id, status);
                    return true;
                } catch (error) {
                    if (retries > 0 && error.message && error.message.includes('500')) {
                        console.warn(`Retrying status update... attempts left: ${retries}`);
                        await new Promise(r => setTimeout(r, 1000)); // Wait 1s
                        return updateStatusWithRetry(id, status, retries - 1);
                    }
                    throw error;
                }
            };

            newStatusSelect.addEventListener('change', async function () {
                // Use .value (e.g., 'in_progress') NOT text (e.g., 'In Progress')
                const newStatusValue = this.value;
                const newStatusText = this.options[this.selectedIndex].text;

                // Disable while updating
                this.disabled = true;

                try {
                    await updateStatusWithRetry(complaintId, newStatusValue);

                    const statusBadge = document.getElementById('status-badge');
                    statusBadge.textContent = newStatusText;
                    updateStatusBadgeClass('status-badge', newStatusText); // Use newStatusText ('In Progress') for style check

                    alert('Status updated successfully');
                } catch (error) {
                    console.error(error);
                    alert('Failed to update status: ' + error.message);
                    // Revert selection logic logic could go here
                } finally {
                    this.disabled = false;
                }
            });
        }

        // Update department information
        document.getElementById('dept-name').textContent = complaint.department;
        document.getElementById('dept-sub').textContent = complaint.sub_department;
        document.getElementById('dept-district').textContent = complaint.complaint_district;

        // Update meta information
        document.getElementById('meta-date').textContent = formatDate(complaint.created_at || complaint.date_filed);
        document.getElementById('meta-updated').textContent = formatDate(complaint.updated_at || complaint.last_updated || 'N/A');
        document.getElementById('similar-count').textContent = complaint.similar_complaints_detected || complaint.similar_count || 0;
        document.getElementById('meta-id').textContent = complaint.complaint_number;

    } catch (error) {
        console.error('Error fetching details:', error);
        alert('Failed to load complaint details.');
    }
}

/**
 * Updates the urgency banner based on urgency data
 * @param {object} urgency - Urgency object with level and score
 */
function updateUrgencyBanner(urgency) {
    const banner = document.getElementById('urgency-banner');
    const title = document.getElementById('urgency-title');
    const message = document.getElementById('urgency-message');

    if (!banner) return;

    // Remove existing urgency classes
    banner.classList.remove('urgency-banner--low', 'urgency-banner--medium',
        'urgency-banner--high', 'urgency-banner--critical');

    const level = urgency.level || 'Low';

    // Add appropriate class and update content
    banner.classList.add(`urgency-banner--${level.toLowerCase()}`);
    title.textContent = `${level} Urgency - Score: ${urgency.score}/100`;

    // Set appropriate message based on urgency level
    const messages = {
        'Low': 'This complaint will be addressed in due course.',
        'Medium': 'This complaint requires attention within a reasonable timeframe.',
        'High': 'This complaint requires immediate attention.',
        'Critical': 'URGENT: This complaint requires immediate action!'
    };
    message.textContent = messages[level] || messages['Medium'];
}

/**
 * Updates the status badge class based on status
 * @param {string} elementId - The element ID to update
 * @param {string} status - The status value
 */
function updateStatusBadgeClass(elementId, status) {
    const element = document.getElementById(elementId);
    if (!element) return;
    element.classList.remove('badge--pending', 'badge--progress', 'badge--resolved');
    if (status === 'In Progress') {
        element.classList.add('badge--progress');
    } else if (status === 'Resolved') {
        element.classList.add('badge--resolved');
    } else {
        element.classList.add('badge--pending');
    }
}

// =============================================================================
// REGISTRATION FORM FUNCTIONS
// =============================================================================

/**
 * Word counter for complaint description textarea
 * Counts words (not characters) and updates the counter display
 */
function initializeWordCounter() {
    const textarea = document.getElementById('complaint_description');
    const wordCountDisplay = document.getElementById('word-count');
    if (!textarea || !wordCountDisplay) return;
    textarea.addEventListener('input', function () {
        // Count words (split by whitespace, filter empty strings)
        const words = this.value.trim().split(/\s+/).filter(word => word.length > 0);
        const wordCount = words.length;
        // Update display
        wordCountDisplay.textContent = `${wordCount}/500 words`;
        // Visual feedback if over limit
        if (wordCount > 500) {
            wordCountDisplay.style.color = '#DC3545';
        } else {
            wordCountDisplay.style.color = '';
        }
    });
}

/**
 * Form submission handler
 * Validates form and prepares data for backend submission
 */
function initializeFormSubmission() {
    const form = document.getElementById('complaint-form');
    if (!form) return;
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        // Collect form data
        const formData = new FormData(form);
        const complaintData = {};
        // Convert FormData to object
        for (let [key, value] of formData.entries()) {
            complaintData[key] = value;
        }
        // Validate word count
        const description = complaintData.complaint_description || '';
        const words = description.trim().split(/\s+/).filter(word => word.length > 0);
        if (words.length > 500) {
            alert('Complaint description exceeds 500 words. Please shorten your description.');
            return;
        }

        // Rename inputs to match backend schema
        // Backend expects: description, not complaint_description
        if (complaintData.complaint_description) {
            complaintData.description = complaintData.complaint_description;
            delete complaintData.complaint_description;
        }

        // Backend expects: mobile, form has mobile_number
        if (complaintData.mobile_number) {
            complaintData.mobile = complaintData.mobile_number;
            delete complaintData.mobile_number;
        }

        // Backend expects: attribute, form has attributes
        if (complaintData.attributes) {
            complaintData.attribute = complaintData.attributes;
            delete complaintData.attributes;
        }

        // Backend expects: pincode, but form has pin_code
        if (complaintData.pin_code) {
            complaintData.pincode = complaintData.pin_code;
            delete complaintData.pin_code;
        }

        // Show loading state
        const submitBtn = document.getElementById('submit-btn');
        const originalBtnText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        // Submit via API
        API.submitComplaint(complaintData)
            .then(data => {
                // Handle success
                alert(`Complaint submitted successfully!\nYour Complaint ID is: ${data.complaint_number}\nUrgency Score: ${data.urgency_score} (${data.urgency_level})`);
                form.reset();
                // Optionally redirect
                // window.location.href = `detail.html?id=${data.complaint_number}`;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to submit complaint: ' + error.message);
            })
            .finally(() => {
                // Reset button state
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            });
    });
}

// =============================================================================
// UTTARAKHAND BLOCK DATA (for cascading dropdowns)
// =============================================================================
const uttarakhandBlocks = {
    "Almora": ["Bhaisiya Chhana", "Bhikiyasain", "Chaukhutiya", "Dwarahat", "Hawalbagh"],
    "Bageshwar": ["Bageshwar", "Garur", "Kapkot"],
    "Chamoli": ["Dasholi", "Dewal", "Gairsain", "Ghat", "Joshimath", "Karnaprayag", "Narayanbagar", "Pokhari", "Tharali"],
    "Champawat": ["Barakot", "Champawat", "Lohaghat", "Pati"],
    "Dehradun": ["Chakrata", "Doiwala", "Kalsi", "Raipur", "Sahaspur", "Vikasnagar"],
    "Haridwar": ["Bahadrabad", "Bhagwanpur", "Khanpur", "Laksar", "Roorkee"],
    "Nainital": ["Bhimtal", "Haldwani", "Kotabagh", "Ramnagar"],
    "Pauri Garhwal": ["Bironkhal", "Dugadda", "Dwarikhal", "Ekeshwar", "Kaljikhal", "Khirsu", "Kot", "Nainidanda", "Pauri", "Pokhra", "Rikhnikhal", "Thalisain", "Yamkeshwar"],
    "Pithoragarh": ["Berinag", "Bin", "Dharchula", "Didihat", "Gangolihat", "Kanalichhina", "Munakot", "Munsyari"],
    "Rudraprayag": ["Augustmuni", "Jakholi", "Ukhimath"],
    "Tehri Garhwal": ["Bhilangna", "Chamba", "Deoprayag", "Jakhnidhar", "Jaunpur", "Kirtinagar", "Narendranagar", "Pratapnagar", "Thauldhar"],
    "Udham Singh Nagar": ["Bajpur", "Kashipur", "Rudrapur", "Sitarganj"],
    "Uttarkashi": ["Bhatwari", "Chinyalisaur", "Dunda", "Mori", "Naugao", "Purola"]
};

// Uttarakhand Department Data
const uttarakhandDepartments = {
    "Public Works Department (PWD)": ["Road Construction/Repair", "Bridge Maintenance", "Government Building Maintenance", "Encroachment Removal"],
    "Jal Sansthan (Water Supply)": ["Water Supply Disruption", "Pipeline Leakage", "Contaminated Water", "New Connection Request", "Handpump Repair"],
    "Electricity (UPCL)": ["Frequent Power Cuts", "Electric Pole Damage", "Transformer Issues", "Incorrect Billing", "New Connection Delay", "Street Light Issues"],
    "Health Department": ["Hospital/Clinic Cleanliness", "Doctor Unavailability", "Medicine Shortage", "Ambulance Service", "Birth/Death Certificate Issues"],
    "Municipal Corporation / Nagar Nigam": ["Garbage Collection", "Drain Cleaning", "Sanitation Issues", "Stray Animals", "Dead Animal Removal"],
    "Education Department": ["School Infrastructure", "Teacher Absenteeism", "Mid-Day Meal Issues", "Scholarship Issues"],
    "Police Department": ["Theft/Burglary", "Traffic Issues", "Cyber Crime", "Public Nuisance", "Harassment"],
    "Revenue Department": ["Land Records (Khatauni)", "Caste/Income Certificate", "Land Dispute", "Encroachment on Government Land"],
    "Transport Department": ["Bus Service Irregularity", "RTO Related Issues", "Overcharging in Public Transport"],
    "Food & Civil Supplies": ["Ration Card Issues", "Ration Shop Irregularities", "Food Quality Issues"]
};

/**
 * Initialize cascading dropdowns for District -> Block dependency
 */
function initializeCascadingDropdowns() {
    // 1. District -> Block
    const districtSelect = document.getElementById('district');
    const blockSelect = document.getElementById('block');

    if (districtSelect && blockSelect) {
        districtSelect.addEventListener('change', function () {
            const selectedDistrict = this.value;
            blockSelect.innerHTML = '<option value="">Select Block</option>';
            if (selectedDistrict && uttarakhandBlocks[selectedDistrict]) {
                uttarakhandBlocks[selectedDistrict].forEach(block => {
                    const option = document.createElement('option');
                    option.value = block;
                    option.textContent = block;
                    blockSelect.appendChild(option);
                });
            }
        });
    }

    // 2. Department -> Sub-Department
    const deptSelect = document.getElementById('department');
    const subDeptSelect = document.getElementById('sub_department');

    if (deptSelect && subDeptSelect) {
        // Populate Departments first (clear hardcoded options if any)
        deptSelect.innerHTML = '<option value="">Select Department</option>';
        Object.keys(uttarakhandDepartments).forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            deptSelect.appendChild(option);
        });

        // Event listener for change
        deptSelect.addEventListener('change', function () {
            const selectedDept = this.value;
            subDeptSelect.innerHTML = '<option value="">Select Sub Department</option>';

            if (selectedDept && uttarakhandDepartments[selectedDept]) {
                uttarakhandDepartments[selectedDept].forEach(subDept => {
                    const option = document.createElement('option');
                    option.value = subDept;
                    option.textContent = subDept;
                    subDeptSelect.appendChild(option);
                });
            }
        });
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

/**
 * Initialize page-specific functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function () {
    const path = window.location.pathname;

    // Initialize common components
    initializeCascadingDropdowns();

    // Page specific init
    if (document.getElementById('complaint-form')) {
        initializeWordCounter();
        initializeFormSubmission();
    }

    if (path.includes('dashboard') || document.getElementById('total-count')) {
        renderDashboard();
    }

    if (path.includes('detail') || document.getElementById('complaint-id-header')) {
        // Get ID from URL query params
        const urlParams = new URLSearchParams(window.location.search);
        const complaintId = urlParams.get('id');
        if (complaintId) {
            renderComplaintDetails(complaintId);
        } else {
            console.error('No complaint ID provided');
            // Redirect or error
        }
    }
});
